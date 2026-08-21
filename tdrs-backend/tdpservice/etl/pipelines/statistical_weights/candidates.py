"""Candidate row construction for statistical weights."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from tdpservice.etl.pipelines.statistical_weights.adapters import adapter_for_program


@dataclass(frozen=True)
class WeightCandidate:
    """Computed statistical weight candidate row."""

    fiscal_year: int
    reporting_month: int
    program: str
    section: str
    stt_code: str
    stratum: str
    case_count: int
    cases: int
    weight: Decimal


class WeightCandidateBuilder:
    """Build statistical weight candidate rows."""

    def __init__(self, *, section: str):
        """Initialize candidate construction for the statistical weights section."""
        self.section = section

    def build(
        self,
        fiscal_year: int,
        s1_rows: list[dict],
        s3_rows: list[dict],
        s4_rows: list[dict],
        program_type: str,
    ) -> list[WeightCandidate]:
        """Build final statistical weight candidates."""
        adapter_for_program(program_type)
        s3_cases_by_pair = {
            (row["stt_code"], row["reporting_month"]): row["case_count"]
            for row in s3_rows
        }
        s4_cases_by_stratum = {
            (row["stt_code"], row["reporting_month"], row["stratum"]): row["cases"]
            for row in s4_rows
        }

        candidates: list[WeightCandidate] = []
        for row in s1_rows:
            case_count = row["case_count"]
            if case_count <= 0:
                continue

            s4_cases = s4_cases_by_stratum.get(
                (row["stt_code"], row["reporting_month"], row["stratum"])
            )
            s3_cases = s3_cases_by_pair.get((row["stt_code"], row["reporting_month"]))
            source_cases = s4_cases if s4_cases is not None else s3_cases
            if not source_cases:
                continue

            cases = max(case_count, int(source_cases))
            if cases <= 0:
                continue

            weight = (Decimal(cases) / Decimal(case_count)).quantize(
                Decimal("0.0001"), rounding=ROUND_HALF_UP
            )
            candidates.append(
                WeightCandidate(
                    fiscal_year=fiscal_year,
                    reporting_month=row["reporting_month"],
                    program=program_type,
                    section=self.section,
                    stt_code=row["stt_code"],
                    stratum=row["stratum"],
                    case_count=case_count,
                    cases=cases,
                    weight=weight,
                )
            )

        return candidates
