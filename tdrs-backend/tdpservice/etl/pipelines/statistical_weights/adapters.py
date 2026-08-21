"""Program adapters for the statistical weights pipeline."""

from dataclasses import dataclass

from tdpservice.data_files.models import DataFile
from tdpservice.search_indexes.models.ssp import SSP_M1, SSP_M6, SSP_M7
from tdpservice.search_indexes.models.tanf import TANF_T1, TANF_T6, TANF_T7
from tdpservice.search_indexes.models.tribal import (
    Tribal_TANF_T1,
    Tribal_TANF_T6,
    Tribal_TANF_T7,
)


@dataclass(frozen=True)
class ProgramAdapter:
    """Program-specific parsed models and field names for one weights run."""

    program_type: str
    active_model: type
    aggregate_model: type
    stratum_model: type
    aggregate_case_count_field: str
    active_label: str
    aggregate_label: str
    stratum_label: str

    def active_queryset(self, datafile_ids: list[int]):
        """Return active-case rows in scope for this program."""
        return self.active_model.objects.filter(datafile_id__in=datafile_ids)

    def aggregate_queryset(self, datafile_ids: list[int]):
        """Return aggregate rows in scope for this program."""
        return self.aggregate_model.objects.filter(datafile_id__in=datafile_ids)

    def stratum_queryset(self, datafile_ids: list[int]):
        """Return stratum rows in scope for this program."""
        return self.stratum_model.objects.filter(datafile_id__in=datafile_ids)

    @staticmethod
    def normalize_code(value) -> str:
        """Normalize STT and stratum codes for joins with legacy integer SQL."""
        if value is None:
            return ""

        try:
            return str(int(value))
        except (TypeError, ValueError):
            return str(value).strip()


PROGRAM_ADAPTERS = {
    DataFile.ProgramType.TANF: ProgramAdapter(
        program_type=DataFile.ProgramType.TANF,
        active_model=TANF_T1,
        aggregate_model=TANF_T6,
        stratum_model=TANF_T7,
        aggregate_case_count_field="NUM_FAMILIES",
        active_label="T1",
        aggregate_label="T6",
        stratum_label="T7",
    ),
    DataFile.ProgramType.SSP: ProgramAdapter(
        program_type=DataFile.ProgramType.SSP,
        active_model=SSP_M1,
        aggregate_model=SSP_M6,
        stratum_model=SSP_M7,
        aggregate_case_count_field="SSPMOE_FAMILIES",
        active_label="M1",
        aggregate_label="M6",
        stratum_label="M7",
    ),
    DataFile.ProgramType.TRIBAL: ProgramAdapter(
        program_type=DataFile.ProgramType.TRIBAL,
        active_model=Tribal_TANF_T1,
        aggregate_model=Tribal_TANF_T6,
        stratum_model=Tribal_TANF_T7,
        aggregate_case_count_field="NUM_FAMILIES",
        active_label="T1",
        aggregate_label="T6",
        stratum_label="T7",
    ),
}


def adapter_for_program(program_type: str) -> ProgramAdapter:
    """Return the configured adapter for an exact DataFile program type."""
    try:
        return PROGRAM_ADAPTERS[program_type]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported statistical weights program: {program_type}"
        ) from exc
