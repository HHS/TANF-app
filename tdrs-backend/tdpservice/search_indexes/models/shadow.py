"""Django-managed shadow models for Go parser output tables."""

from django.db import models

from tdpservice.common.shadow_models import create_shadow_model
from tdpservice.search_indexes.models.fra import TANF_Exiter1
from tdpservice.search_indexes.models.program_audit import (
    ProgramAudit_T1,
    ProgramAudit_T2,
    ProgramAudit_T3,
)
from tdpservice.search_indexes.models.ssp import (
    SSP_M1,
    SSP_M2,
    SSP_M3,
    SSP_M4,
    SSP_M5,
    SSP_M6,
    SSP_M7,
)
from tdpservice.search_indexes.models.tanf import (
    TANF_T1,
    TANF_T2,
    TANF_T3,
    TANF_T4,
    TANF_T5,
    TANF_T6,
    TANF_T7,
)
from tdpservice.search_indexes.models.tribal import (
    Tribal_TANF_T1,
    Tribal_TANF_T2,
    Tribal_TANF_T3,
    Tribal_TANF_T4,
    Tribal_TANF_T5,
    Tribal_TANF_T6,
    Tribal_TANF_T7,
)


def _shadow_record_model(name, source_model, db_table):
    return create_shadow_model(
        name,
        source_model,
        db_table,
        app_label="search_indexes",
        module=__name__,
        foreign_key_overrides={
            "datafile": models.ForeignKey(
                "data_files.ShadowDataFile",
                blank=True,
                help_text="The parent shadow file from which this record was created.",
                null=True,
                on_delete=models.CASCADE,
                related_name="+",
            ),
        },
    )


ShadowTANF_T1 = _shadow_record_model(
    "ShadowTANF_T1", TANF_T1, "shadow_search_indexes_tanf_t1"
)
ShadowTANF_T2 = _shadow_record_model(
    "ShadowTANF_T2", TANF_T2, "shadow_search_indexes_tanf_t2"
)
ShadowTANF_T3 = _shadow_record_model(
    "ShadowTANF_T3", TANF_T3, "shadow_search_indexes_tanf_t3"
)
ShadowTANF_T4 = _shadow_record_model(
    "ShadowTANF_T4", TANF_T4, "shadow_search_indexes_tanf_t4"
)
ShadowTANF_T5 = _shadow_record_model(
    "ShadowTANF_T5", TANF_T5, "shadow_search_indexes_tanf_t5"
)
ShadowTANF_T6 = _shadow_record_model(
    "ShadowTANF_T6", TANF_T6, "shadow_search_indexes_tanf_t6"
)
ShadowTANF_T7 = _shadow_record_model(
    "ShadowTANF_T7", TANF_T7, "shadow_search_indexes_tanf_t7"
)

ShadowSSP_M1 = _shadow_record_model(
    "ShadowSSP_M1", SSP_M1, "shadow_search_indexes_ssp_m1"
)
ShadowSSP_M2 = _shadow_record_model(
    "ShadowSSP_M2", SSP_M2, "shadow_search_indexes_ssp_m2"
)
ShadowSSP_M3 = _shadow_record_model(
    "ShadowSSP_M3", SSP_M3, "shadow_search_indexes_ssp_m3"
)
ShadowSSP_M4 = _shadow_record_model(
    "ShadowSSP_M4", SSP_M4, "shadow_search_indexes_ssp_m4"
)
ShadowSSP_M5 = _shadow_record_model(
    "ShadowSSP_M5", SSP_M5, "shadow_search_indexes_ssp_m5"
)
ShadowSSP_M6 = _shadow_record_model(
    "ShadowSSP_M6", SSP_M6, "shadow_search_indexes_ssp_m6"
)
ShadowSSP_M7 = _shadow_record_model(
    "ShadowSSP_M7", SSP_M7, "shadow_search_indexes_ssp_m7"
)

ShadowTribal_TANF_T1 = _shadow_record_model(
    "ShadowTribal_TANF_T1",
    Tribal_TANF_T1,
    "shadow_search_indexes_tribal_tanf_t1",
)
ShadowTribal_TANF_T2 = _shadow_record_model(
    "ShadowTribal_TANF_T2",
    Tribal_TANF_T2,
    "shadow_search_indexes_tribal_tanf_t2",
)
ShadowTribal_TANF_T3 = _shadow_record_model(
    "ShadowTribal_TANF_T3",
    Tribal_TANF_T3,
    "shadow_search_indexes_tribal_tanf_t3",
)
ShadowTribal_TANF_T4 = _shadow_record_model(
    "ShadowTribal_TANF_T4",
    Tribal_TANF_T4,
    "shadow_search_indexes_tribal_tanf_t4",
)
ShadowTribal_TANF_T5 = _shadow_record_model(
    "ShadowTribal_TANF_T5",
    Tribal_TANF_T5,
    "shadow_search_indexes_tribal_tanf_t5",
)
ShadowTribal_TANF_T6 = _shadow_record_model(
    "ShadowTribal_TANF_T6",
    Tribal_TANF_T6,
    "shadow_search_indexes_tribal_tanf_t6",
)
ShadowTribal_TANF_T7 = _shadow_record_model(
    "ShadowTribal_TANF_T7",
    Tribal_TANF_T7,
    "shadow_search_indexes_tribal_tanf_t7",
)

ShadowProgramAudit_T1 = _shadow_record_model(
    "ShadowProgramAudit_T1",
    ProgramAudit_T1,
    "shadow_search_indexes_programaudit_t1",
)
ShadowProgramAudit_T2 = _shadow_record_model(
    "ShadowProgramAudit_T2",
    ProgramAudit_T2,
    "shadow_search_indexes_programaudit_t2",
)
ShadowProgramAudit_T3 = _shadow_record_model(
    "ShadowProgramAudit_T3",
    ProgramAudit_T3,
    "shadow_search_indexes_programaudit_t3",
)

ShadowTANF_Exiter1 = _shadow_record_model(
    "ShadowTANF_Exiter1",
    TANF_Exiter1,
    "shadow_search_indexes_tanf_exiter1",
)
