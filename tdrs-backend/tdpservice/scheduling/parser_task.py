"""Celery hook for parsing tasks."""

from __future__ import absolute_import

from dataclasses import dataclass
from typing import Callable

from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.db.models import Case, Count, IntegerField, When
from django.db.utils import DatabaseError
from django.utils import timezone

from celery import current_app, shared_task

from tdpservice.core.utils import log
from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.error_reports import ErrorReportFactory
from tdpservice.data_files.models import DataFile, ReparseFileMeta, ShadowDataFile
from tdpservice.data_files.submission_lifecycle import transition_datafile
from tdpservice.email.helpers.data_file import send_data_submitted_email
from tdpservice.log_handler import change_log_filename
from tdpservice.parsers.aggregates import (
    case_aggregates_by_month,
    fra_total_errors,
    total_errors_by_month,
)
from tdpservice.parsers.error_generator import (
    ErrorGeneratorArgs,
    ErrorGeneratorFactory,
    ErrorGeneratorType,
)
from tdpservice.parsers.factory import ParserFactory
from tdpservice.parsers.models import (
    DataFileSummary,
    ParserError,
    ParserErrorCategoryChoices,
    ShadowDataFileSummary,
    ShadowParserError,
)
from tdpservice.parsers.util import DecoderUnknownException, log_parser_exception
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.users.models import AccountApprovalStatusChoices, User

logger = settings.PARSER_LOGGER

GO_PARSER_TASK_NAME = "tdpservice.scheduling.parser_task.go_parse"
GO_PARSER_POST_PARSE_TASK_NAME = "tdpservice.scheduling.parser_task.post_parse"
GO_PARSER_QUEUE = getattr(settings, "GO_PARSER_QUEUE", "go-parser")


@dataclass(frozen=True)
class ParserModelSet:
    """Models and lookup hooks for a parser output table family."""

    data_file_model: type
    summary_model: type
    parser_error_model: type
    record_model_resolver: Callable[[type], type]
    label: str


def queue_go_parse(data_file_id, reparse_id=None):
    """Queue a shadow parse task for the Go parser."""
    try:
        current_app.send_task(
            GO_PARSER_TASK_NAME,
            args=[data_file_id, reparse_id or 0],
            queue=GO_PARSER_QUEUE,
            ignore_result=True,
        )
    except Exception:
        data_file = DataFile.objects.get(id=data_file_id)
        log(
            f"Failed to submit Go parser shadow task for datafile {data_file_id}.",
            logger_context={
                "user_id": data_file.user_id,
                "content_type": DataFile,
                "object_id": data_file.pk,
                "object_repr": repr(data_file),
            },
            level="exception",
        )


def queue_parse(data_file_id, reparse_id=None):
    """Queue production Python parse and companion Go shadow parse tasks."""
    parse.delay(data_file_id, reparse_id=reparse_id)
    if settings.GO_PARSER_SHADOW_MODE:
        queue_go_parse(data_file_id, reparse_id=reparse_id)


def set_reparse_file_meta_model_state(reparse_id, file_meta, is_success):
    """Set ReparseFileMeta fields to indicate a parse failure."""
    if reparse_id:
        file_meta.finished = True
        file_meta.success = is_success
        file_meta.finished_at = timezone.now()
        file_meta.save()


def _shadow_record_model(production_model):
    """Return the Django model for the Go parser shadow copy of a record table."""
    shadow_table_name = f"shadow_{production_model._meta.db_table}"
    for model in apps.get_app_config("search_indexes").get_models():
        if model._meta.db_table == shadow_table_name:
            return model
    raise LookupError(
        f"No shadow model found for table {production_model._meta.db_table}"
    )


def _production_parser_models():
    """Return parser models for production parser output."""
    return ParserModelSet(
        data_file_model=DataFile,
        summary_model=DataFileSummary,
        parser_error_model=ParserError,
        record_model_resolver=lambda production_model: production_model,
        label="production",
    )


def _shadow_parser_models():
    """Return parser models for Go parser shadow output."""
    return ParserModelSet(
        data_file_model=ShadowDataFile,
        summary_model=ShadowDataFileSummary,
        parser_error_model=ShadowParserError,
        record_model_resolver=_shadow_record_model,
        label="shadow",
    )


def _uses_shadow_table(model_or_instance):
    """Return whether a model or instance belongs to a shadow table family."""
    return model_or_instance._meta.db_table.startswith("shadow_")


def _parser_models_for_instance(model_or_instance):
    """Return the model set matching the table family of a model or instance."""
    if _uses_shadow_table(model_or_instance):
        return _shadow_parser_models()
    return _production_parser_models()


def _post_parse_model_sets():
    """Return model sets in the order Go parser output is expected."""
    if settings.GO_PARSER_SHADOW_MODE:
        return (_shadow_parser_models(), _production_parser_models())
    return (_production_parser_models(), _shadow_parser_models())


def _get_post_parse_data_file(data_file_id):
    """Return the DataFile row and table family used by Go parser output."""
    for parser_models in _post_parse_model_sets():
        data_file = parser_models.data_file_model.objects.filter(
            id=data_file_id
        ).first()
        if data_file is not None:
            return data_file, parser_models

    raise DataFile.DoesNotExist(f"No parser data file found for id={data_file_id}")


def _get_summary_status(dfs, data_file, parser_error_model=ParserError):
    """Return DataFileSummary-style status using the selected parser error model."""
    if dfs.status != DataFileSummary.Status.PENDING:
        return dfs.status

    counts = parser_error_model.objects.filter(
        file=data_file, deprecated=False
    ).aggregate(
        total=Count("id"),
        precheck=Count(
            Case(
                When(error_type=ParserErrorCategoryChoices.PRE_CHECK, then=1),
                output_field=IntegerField(),
            )
        ),
        record_precheck=Count(
            Case(
                When(error_type=ParserErrorCategoryChoices.RECORD_PRE_CHECK, then=1),
                output_field=IntegerField(),
            )
        ),
        case_consistency=Count(
            Case(
                When(error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY, then=1),
                output_field=IntegerField(),
            )
        ),
    )

    if counts["precheck"] > 0:
        return DataFileSummary.Status.REJECTED
    if counts["total"] == 0:
        return DataFileSummary.Status.ACCEPTED
    if counts["case_consistency"] > 0 or counts["record_precheck"] > 0:
        return DataFileSummary.Status.PARTIALLY_ACCEPTED
    return DataFileSummary.Status.ACCEPTED_WITH_ERRORS


def update_dfs(
    dfs,
    data_file,
    parser_error_model=None,
    record_model_resolver=None,
):
    """Update DataFileSummary fields using the selected parser output models."""
    parser_models = _parser_models_for_instance(data_file)
    parser_error_model = parser_error_model or parser_models.parser_error_model
    record_model_resolver = record_model_resolver or parser_models.record_model_resolver

    dfs.status = _get_summary_status(dfs, data_file, parser_error_model)

    if data_file.program_type == DataFile.ProgramType.FRA:
        dfs.case_aggregates = fra_total_errors(
            data_file, parser_error_model=parser_error_model
        )
    else:
        if "Case Data" in data_file.section:
            dfs.case_aggregates = case_aggregates_by_month(
                data_file,
                dfs.status,
                parser_error_model=parser_error_model,
                record_model_resolver=record_model_resolver,
            )
        else:
            dfs.case_aggregates = total_errors_by_month(
                data_file,
                dfs.status,
                parser_error_model=parser_error_model,
            )
    dfs.save()


def set_error_report(dfs, error_report):
    """Update DataFileSummary error_report."""
    dfs.error_report = File(
        error_report, name=f"{dfs.datafile.original_filename}_error_report"
    )
    dfs.save()


def _transition_parse_outcome(data_file, dfs):
    """Transition DataFile state based on parse outcome."""
    if dfs.status == DataFileSummary.Status.ACCEPTED:
        transition_datafile(
            data_file,
            SubmissionState.PARSE_COMPLETED,
            note="parsing completed successfully",
        )
    elif dfs.status in (
        DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
        DataFileSummary.Status.PARTIALLY_ACCEPTED,
    ):
        transition_datafile(
            data_file,
            SubmissionState.PARSED_WITH_ERRORS,
            note="parsing completed with errors",
        )
    elif dfs.status == DataFileSummary.Status.REJECTED:
        transition_datafile(
            data_file,
            SubmissionState.PARSE_FAILED,
            note="file rejected during parsing",
        )


def _notify_data_analysts(data_file, dfs, file_meta=None, reparse_id=None):
    """Send submission email to relevant data analysts (initial submissions only)."""
    qs = User.objects.filter(
        stt=data_file.stt,
        account_approval_status=AccountApprovalStatusChoices.APPROVED,
        groups__name="Data Analyst",
    )

    if data_file.program_type == DataFile.ProgramType.FRA:
        qs = qs.filter(user_permissions__codename="has_fra_access")

    recipients = qs.values_list("username", flat=True).distinct()
    if should_send_reparse_notification(dfs, file_meta, reparse_id):
        send_data_submitted_email(
            dfs, recipients, is_reprocessed=(reparse_id is not None)
        )


def _handle_parse_failure(data_file, note):
    """Transition to PARSE_FAILED after parser startup."""
    transition_datafile(
        data_file,
        SubmissionState.PARSE_FAILED,
        note=note,
    )


def _reject_dfs(dfs):
    """Mark a data file summary as rejected if it exists."""
    if dfs is not None:
        dfs.set_status(DataFileSummary.Status.REJECTED)
        dfs.save()


def _finalize_parse(
    data_file,
    dfs,
    parser_error_model=None,
    record_model_resolver=None,
    roll_log=True,
):
    """Generate parse artifacts and refresh DataFileSummary aggregates."""
    parser_models = _parser_models_for_instance(data_file)
    parser_error_model = parser_error_model or parser_models.parser_error_model
    record_model_resolver = record_model_resolver or parser_models.record_model_resolver

    logger.info(
        "%s DataFile parsing finished for file -> %r.",
        parser_models.label.capitalize(),
        data_file,
    )
    if dfs is None:
        return

    error_report_generator = ErrorReportFactory.get_error_report_generator(
        data_file,
        parser_error_model=parser_error_model,
    )
    error_report = error_report_generator.generate()
    set_error_report(dfs, error_report)
    if roll_log:
        logger.handlers[2].doRollover(data_file)
    update_dfs(
        dfs,
        data_file,
        parser_error_model=parser_error_model,
        record_model_resolver=record_model_resolver,
    )


def _finalize_reparse(data_file_id, reparse_id, file_meta, dfs, reparse_success):
    """Update reparse metadata after parsing completes."""
    if reparse_id is None:
        return

    if dfs is None:
        return

    file_meta.num_records_created = dfs.total_number_of_records_created
    file_meta.cat_4_errors_generated = ParserError.objects.filter(
        file_id=data_file_id,
        error_type=ParserErrorCategoryChoices.CASE_CONSISTENCY,
    ).count()
    ReparseMeta.set_total_num_records_post(ReparseMeta.objects.get(pk=reparse_id))
    set_reparse_file_meta_model_state(reparse_id, file_meta, reparse_success)


def _add_unexpected_error(data_file):
    """Persist a user-facing parser error for unexpected failures."""
    generate_error = ErrorGeneratorFactory(data_file).get_generator(
        ErrorGeneratorType.MSG_ONLY_PRECHECK,
        None,
    )
    generator_args = ErrorGeneratorArgs(
        record=None,
        schema=None,
        error_message=(
            "We're sorry, an unexpected error has occurred and the file has been "
            "rejected. Please contact the TDP support team at TANFData@acf.hhs.gov "
            "for further assistance."
        ),
    )
    error = generate_error(generator_args=generator_args)
    error.save()


def should_send_reparse_notification(dfs, file_meta, reparse_id):
    """Return whether a reparse completion email should be sent."""
    if not reparse_id:
        return True

    if file_meta is None:
        return True

    return not (
        file_meta.previous_summary_status == DataFileSummary.Status.ACCEPTED
        and dfs.status == DataFileSummary.Status.ACCEPTED
    )


@shared_task(name="tdpservice.scheduling.parser_task.go_parse")
def go_parse(data_file_id):
    """Register the Go parser task name without executing it in Python."""
    raise RuntimeError(
        f"go_parse for data_file_id={data_file_id} is routed to the Go parser worker "
        "and should not execute in the Python worker"
    )


@shared_task(name=GO_PARSER_POST_PARSE_TASK_NAME)
def post_parse(data_file_id, reparse_id=0, parse_error=None):
    """Finalize Go parser output after every parse attempt."""
    data_file, parser_models = _get_post_parse_data_file(data_file_id)
    dfs, _ = parser_models.summary_model.objects.get_or_create(
        datafile=data_file,
        defaults={"status": DataFileSummary.Status.PENDING},
    )

    if parse_error:
        dfs.status = DataFileSummary.Status.REJECTED
        dfs.save()
        data_file.state = SubmissionState.PARSE_FAILED
        data_file.save(update_fields=["state"])
        logger.error(
            "Go parser %s post-parse received parse_error for data_file_id=%s: %s",
            parser_models.label,
            data_file_id,
            parse_error,
        )
        return

    _finalize_parse(
        data_file,
        dfs,
        parser_error_model=parser_models.parser_error_model,
        record_model_resolver=parser_models.record_model_resolver,
        roll_log=False,
    )
    if not settings.GO_PARSER_SHADOW_MODE:
        file_meta = ReparseFileMeta.objects.get(
            data_file_id=data_file_id, reparse_meta_id=reparse_id
        )
        _finalize_reparse(data_file_id, reparse_id, file_meta, dfs)


@shared_task
def parse(data_file_id, reparse_id=None):
    """Send data file for processing."""
    # passing the data file FileField across redis was rendering non-serializable failures, doing the below lookup
    # to avoid those. I suppose good practice to not store/serializer large file contents in memory when stored in redis
    # for undetermined amount of time.
    dfs = None
    try:
        data_file = DataFile.objects.get(id=data_file_id)
        change_log_filename(logger, data_file)
        logger.info(
            f"\n\n\n __ Starting to {'re-' if reparse_id else ''}parse datafile {data_file.filename}__ \n\n\n"
        )

        file_meta = None
        reparse_success = True
        if reparse_id:
            file_meta = ReparseFileMeta.objects.get(
                data_file_id=data_file_id, reparse_meta_id=reparse_id
            )
            file_meta.started_at = timezone.now()
            file_meta.save()

        transition_datafile(
            data_file,
            SubmissionState.PARSE_STARTED,
            note="parser worker started",
        )

        dfs = DataFileSummary.objects.create(
            datafile=data_file, status=DataFileSummary.Status.PENDING
        )
        parser = ParserFactory.get_instance(
            datafile=data_file,
            dfs=dfs,
            section=data_file.section,
            program_type=data_file.program_type,
            is_program_audit=data_file.is_program_audit,
        )
        parser.parse_and_validate()
        update_dfs(dfs, data_file)

        logger.info(f"Parsing finished for file -> {repr(data_file)}.")

        _transition_parse_outcome(data_file, dfs)
        _notify_data_analysts(data_file, dfs, file_meta, reparse_id)

    except DecoderUnknownException:
        _reject_dfs(dfs)
        _handle_parse_failure(data_file, "decoder unknown exception")
        reparse_success = False
    except DatabaseError as e:
        log_parser_exception(
            data_file,
            f"Encountered Database exception in parser_task.py: \n{e}",
            "error",
        )
        _handle_parse_failure(data_file, "database error during parsing")
        reparse_success = False
    except Exception:
        if dfs is None:
            raise

        _add_unexpected_error(data_file)
        _reject_dfs(dfs)
        log_parser_exception(
            data_file,
            (
                f"Uncaught exception while parsing datafile: {data_file.pk}! Please review the logs to "
                f"see if manual intervention is required."
            ),
            "exception",
        )
        _handle_parse_failure(data_file, "unexpected error during parsing")
        reparse_success = False
    finally:
        _finalize_parse(data_file, dfs)
        _finalize_reparse(data_file_id, reparse_id, file_meta, dfs, reparse_success)
