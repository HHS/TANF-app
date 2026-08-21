"""Helper functions for sending ETL notification emails."""

from django.conf import settings

from tdpservice.data_files.models import DataFile
from tdpservice.email.email import automated_email, log
from tdpservice.email.email_enums import ETLEmail
from tdpservice.etl.models import ETLArtifact, ETLPipelineRun, ETLQAResult


def send_statistical_weights_run_email(
    pipeline_run: ETLPipelineRun,
    recipients,
) -> None:
    """Send a statistical weights ETL run-completion email."""
    if not recipients:
        return

    context = statistical_weights_email_context(pipeline_run)
    logger_context = _logger_context(pipeline_run)

    log(
        f"Statistical weights run complete; emailing recipients {list(recipients)}",
        logger_context=logger_context,
    )

    automated_email(
        email_path=ETLEmail.STATISTICAL_WEIGHTS_RUN.value,
        recipient_email=recipients,
        subject=context["subject"],
        email_context=context,
        text_message=statistical_weights_text_message(context),
        logger_context=logger_context,
    )


def statistical_weights_email_context(pipeline_run: ETLPipelineRun) -> dict:
    """Return template context for a statistical weights ETL notification."""
    program = _program_label(pipeline_run)
    output = pipeline_run.final_output
    if output is None:
        output = (
            pipeline_run.artifacts.filter(
                key="statistical_weights",
                artifact_role=ETLArtifact.ArtifactRole.FINAL,
            )
            .order_by("id")
            .last()
        )
    run_status = (
        ETLPipelineRun.Status.SUCCEEDED
        if output and output.published
        else pipeline_run.status
    )
    output_version = output.version if output else "unknown"
    row_count = output.row_count if output else 0
    subject = f"{program} Statistical Weights Run: {run_status}"

    return {
        "subject": subject,
        "pipeline_name": f"{program} Statistical Weights",
        "run_id": pipeline_run.id,
        "fiscal_year": pipeline_run.parameters.get("fiscal_year"),
        "program": program,
        "status": run_status,
        "trigger_source": pipeline_run.trigger_source,
        "output_version": output_version,
        "row_count": row_count,
        "run_detail_url": statistical_weights_run_detail_url(pipeline_run),
        "qa_results": _qa_results(pipeline_run),
        "url": settings.FRONTEND_BASE_URL,
    }


def statistical_weights_text_message(context: dict) -> str:
    """Return the plain-text statistical weights notification body."""
    qa_lines = [
        (
            f"- {result['node_id']}: {result['status']}"
            f"{' - ' + result['message'] if result['message'] else ''}"
        )
        for result in context["qa_results"]
    ]
    if not qa_lines:
        qa_lines = ["- No QA results recorded."]

    return "\n".join(
        [
            f"{context['program']} Statistical Weights pipeline run completed.",
            "",
            f"Pipeline: {context['pipeline_name']}",
            f"Run ID: {context['run_id']}",
            f"Fiscal Year: {context['fiscal_year']}",
            f"Program: {context['program']}",
            f"Status: {context['status']}",
            f"Trigger Source: {context['trigger_source']}",
            f"Output Version: {context['output_version']}",
            f"Row Count: {context['row_count']}",
            f"Run Detail: {context['run_detail_url']}",
            "",
            "QA Summary:",
            *qa_lines,
        ]
    )


def statistical_weights_run_detail_url(pipeline_run: ETLPipelineRun) -> str:
    """Return an API URL for ETL run details."""
    return f"{settings.FRONTEND_BASE_URL}/admin/etl/etlpipelinerun/{pipeline_run.id}/change"


def _program_label(pipeline_run: ETLPipelineRun) -> str:
    """Return the statistical weights program label for a run."""
    program = (
        pipeline_run.output_scope.get("program")
        or pipeline_run.parameters.get("program")
        or "unknown"
    )
    if program == DataFile.ProgramType.TRIBAL:
        return "Tribal TANF"
    if program in DataFile.ProgramType.values:
        return DataFile.ProgramType(program).name
    return program


def _qa_results(pipeline_run: ETLPipelineRun) -> list[dict]:
    """Return QA results in a template-friendly shape."""
    return [
        {
            "node_id": result.check_key,
            "status": result.status,
            "message": result.summary
            if result.status in (ETLQAResult.Status.WARNING, ETLQAResult.Status.FAILED)
            else "",
        }
        for result in pipeline_run.qa_results.order_by("id")
    ]


def _logger_context(pipeline_run: ETLPipelineRun) -> dict | None:
    """Return admin-log context when the run has a triggering user."""
    if not pipeline_run.triggered_by_id:
        return None

    return {
        "user_id": pipeline_run.triggered_by_id,
        "object_id": pipeline_run.id,
        "object_repr": str(pipeline_run),
        "content_type": ETLPipelineRun,
    }
