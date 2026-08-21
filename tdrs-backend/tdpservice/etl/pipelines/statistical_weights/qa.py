"""QA checks for statistical weights."""

from tdpservice.data_files.models import DataFile
from tdpservice.etl.models import ETLQAResult
from tdpservice.etl.pipelines.base import NodeResult
from tdpservice.etl.pipelines.statistical_weights.adapters import adapter_for_program
from tdpservice.etl.pipelines.statistical_weights.candidates import WeightCandidate
from tdpservice.stts.models import STT


class StatisticalWeightsQA:
    """Run statistical weights QA checks and persist their results."""

    def run(
        self,
        *,
        pipeline_run,
        program: str,
        s1_rows: list[dict],
        s3_rows: list[dict],
        s4_rows: list[dict],
        candidates: list[WeightCandidate],
    ) -> NodeResult:
        """Persist statistical weights QA results."""
        adapter = adapter_for_program(program)
        review_month = self.review_month(s1_rows, s3_rows, s4_rows)

        ETLQAResult.objects.filter(pipeline_run=pipeline_run).delete()

        self.create_result(
            pipeline_run,
            "weights_row_counts",
            ETLQAResult.Status.PASSED,
            "Captured statistical weights row counts.",
            {
                "s1": len(s1_rows),
                "s3": len(s3_rows),
                "s4": len(s4_rows),
                "candidate_output": len(candidates),
            },
        )

        s1_present, s3_present, s4_present = self.present_stt_codes(
            review_month=review_month,
            s1_rows=s1_rows,
            s3_rows=s3_rows,
            s4_rows=s4_rows,
        )
        required_codes = self.required_stt_codes(program)
        stratum_codes = self.stratum_stt_codes(program)
        missing_payload = {
            "review_month": review_month,
            "s1_missing": sorted(required_codes - s1_present),
            "s3_missing": sorted(required_codes - s3_present),
            "s4_missing": sorted(stratum_codes - s4_present),
        }
        missing_count = sum(
            len(values)
            for values in missing_payload.values()
            if isinstance(values, list)
        )
        self.create_result(
            pipeline_run,
            "weights_missing_stts",
            ETLQAResult.Status.WARNING if missing_count else ETLQAResult.Status.PASSED,
            f"Found {missing_count} missing STT entries for review month.",
            missing_payload,
        )

        pair_mismatches = self.active_aggregate_pair_mismatches(s1_rows, s3_rows)
        self.create_result(
            pipeline_run,
            "weights_active_aggregate_pair_mismatch",
            ETLQAResult.Status.WARNING
            if pair_mismatches
            else ETLQAResult.Status.PASSED,
            "Found "
            f"{len(pair_mismatches)} {adapter.active_label}/{adapter.aggregate_label} "
            "pair mismatches.",
            {"mismatches": self.tuple_payload(pair_mismatches)},
        )

        stratum_mismatches = self.active_stratum_mismatches(
            s1_rows=s1_rows,
            s4_rows=s4_rows,
            stratum_codes=stratum_codes,
        )
        self.create_result(
            pipeline_run,
            "weights_active_stratum_mismatch",
            ETLQAResult.Status.WARNING
            if stratum_mismatches
            else ETLQAResult.Status.PASSED,
            "Found "
            f"{len(stratum_mismatches)} {adapter.active_label}/{adapter.stratum_label} "
            "stratum mismatches.",
            {"mismatches": self.tuple_payload(stratum_mismatches)},
        )

        return NodeResult(
            output_row_count=4,
            metadata={"program": program, "review_month": review_month},
        )

    def review_month(self, *datasets: list[dict]) -> int | None:
        """Return the highest reporting month present in QA datasets."""
        reporting_months = [
            row["reporting_month"]
            for dataset in datasets
            for row in dataset
            if row.get("reporting_month")
        ]
        return max(reporting_months) if reporting_months else None

    def present_stt_codes(
        self,
        *,
        review_month: int | None,
        s1_rows: list[dict],
        s3_rows: list[dict],
        s4_rows: list[dict],
    ) -> tuple[set[int], set[int], set[int]]:
        """Return present active, aggregate, and stratum STT codes."""
        if not review_month:
            return set(), set(), set()

        s1_present = {
            int(row["stt_code"])
            for row in s1_rows
            if row["reporting_month"] == review_month and row["stt_code"].isdigit()
        }
        s3_present = {
            int(row["stt_code"])
            for row in s3_rows
            if row["reporting_month"] == review_month and row["stt_code"].isdigit()
        }
        s4_present = {
            int(row["stt_code"])
            for row in s4_rows
            if row["reporting_month"] == review_month and row["stt_code"].isdigit()
        }
        return s1_present, s3_present, s4_present

    def required_stt_codes(self, program_type: str) -> set[int]:
        """Return STT codes expected for active and aggregate rows."""
        if program_type == DataFile.ProgramType.TRIBAL:
            return self.numeric_stt_codes(STT.objects.filter(type=STT.EntityType.TRIBE))
        queryset = STT.objects.filter(
            type__in=[
                STT.EntityType.STATE,
                STT.EntityType.TERRITORY,
            ]
        )
        if program_type == DataFile.ProgramType.SSP:
            queryset = queryset.filter(ssp=True)
        return self.numeric_stt_codes(queryset)

    def stratum_stt_codes(self, program_type: str) -> set[int]:
        """Return STT codes expected for stratum rows."""
        if program_type == DataFile.ProgramType.TRIBAL:
            return self.numeric_stt_codes(STT.objects.filter(type=STT.EntityType.TRIBE))
        queryset = STT.objects.filter(sample=True)
        if program_type == DataFile.ProgramType.SSP:
            queryset = queryset.filter(ssp=True)
        return self.numeric_stt_codes(queryset)

    def numeric_stt_codes(self, queryset) -> set[int]:
        """Return numeric STT codes from an STT queryset."""
        codes = (
            queryset.exclude(stt_code__isnull=True)
            .exclude(stt_code="")
            .values_list("stt_code", flat=True)
        )
        return {int(code) for code in codes if str(code).isdigit()}

    def active_aggregate_pair_mismatches(
        self,
        s1_rows: list[dict],
        s3_rows: list[dict],
    ) -> list[tuple]:
        """Return active/aggregate STT-month pair mismatches."""
        s1_pairs = {(row["stt_code"], row["reporting_month"]) for row in s1_rows}
        s3_pairs = {(row["stt_code"], row["reporting_month"]) for row in s3_rows}
        return sorted(s1_pairs.symmetric_difference(s3_pairs))

    def active_stratum_mismatches(
        self,
        *,
        s1_rows: list[dict],
        s4_rows: list[dict],
        stratum_codes: set[int],
    ) -> list[tuple]:
        """Return active/stratum STT-month-stratum mismatches."""
        stratum_code_strings = {str(code) for code in stratum_codes}
        s1_strata = {
            (row["stt_code"], row["reporting_month"], row["stratum"])
            for row in s1_rows
            if row["stt_code"] in stratum_code_strings
        }
        s4_strata = {
            (row["stt_code"], row["reporting_month"], row["stratum"])
            for row in s4_rows
            if row["stt_code"] in stratum_code_strings
        }
        return sorted(s1_strata.symmetric_difference(s4_strata))

    def create_result(
        self,
        pipeline_run,
        check_key,
        status,
        summary,
        payload,
        blocking=False,
    ):
        """Persist one QA result."""
        return ETLQAResult.objects.create(
            pipeline_run=pipeline_run,
            check_key=check_key,
            status=status,
            summary=summary,
            result_payload=payload,
            blocking=blocking,
        )

    def tuple_payload(self, values: list[tuple]) -> list[list]:
        """Convert tuple sets to JSON-stable list payloads."""
        return [list(value) for value in values]
