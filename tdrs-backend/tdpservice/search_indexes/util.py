"""Utility functions and definitions for models."""
from tdpservice.search_indexes.models import fra, ssp, tanf, tribal

MODELS = [
    tanf.TANF_T1,
    tanf.TANF_T2,
    tanf.TANF_T3,
    tanf.TANF_T4,
    tanf.TANF_T5,
    tanf.TANF_T6,
    tanf.TANF_T7,
    ssp.SSP_M1,
    ssp.SSP_M2,
    ssp.SSP_M3,
    ssp.SSP_M4,
    ssp.SSP_M5,
    ssp.SSP_M6,
    ssp.SSP_M7,
    tribal.Tribal_TANF_T1,
    tribal.Tribal_TANF_T2,
    tribal.Tribal_TANF_T3,
    tribal.Tribal_TANF_T4,
    tribal.Tribal_TANF_T5,
    tribal.Tribal_TANF_T6,
    tribal.Tribal_TANF_T7,
    fra.TANF_Exiter1,
]


def count_all_records():
    """Count total number of records in the database."""
    total_num_records = 0
    for model in MODELS:
        total_num_records += model.objects.all().count()
    return total_num_records
