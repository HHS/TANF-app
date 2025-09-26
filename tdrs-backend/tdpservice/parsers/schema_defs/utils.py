"""Utility functions for parsing."""

import logging

from tdpservice.data_files.models import DataFile
from tdpservice.parsers import schema_defs

logger = logging.getLogger(__name__)


class ProgramManager:
    """Container class to map schemas based on program and section."""

    # TANF schemas
    tan_active_schemas = {
        "T1": schema_defs.tanf.t1,
        "T2": schema_defs.tanf.t2,
        "T3": schema_defs.tanf.t3,
    }
    tan_active_audit_schemas = {
        "T1": schema_defs.program_audit.t1,
        "T2": schema_defs.program_audit.t2,
        "T3": schema_defs.program_audit.t3,
    }
    tan_closed_schemas = {
        "T4": schema_defs.tanf.t4,
        "T5": schema_defs.tanf.t5,
    }
    tan_agg_schemas = {
        "T6": schema_defs.tanf.t6,
    }
    tan_strat_schemas = {
        "T7": schema_defs.tanf.t7,
    }

    # Tribal schemas
    tribal_active_schemas = {
        "T1": schema_defs.tribal_tanf.t1,
        "T2": schema_defs.tribal_tanf.t2,
        "T3": schema_defs.tribal_tanf.t3,
    }
    tribal_closed_schemas = {
        "T4": schema_defs.tribal_tanf.t4,
        "T5": schema_defs.tribal_tanf.t5,
    }
    tribal_agg_schemas = {
        "T6": schema_defs.tribal_tanf.t6,
    }
    tribal_strat_schemas = {
        "T7": schema_defs.tribal_tanf.t7,
    }

    # SSP schemas
    ssp_active_schemas = {
        "M1": schema_defs.ssp.m1,
        "M2": schema_defs.ssp.m2,
        "M3": schema_defs.ssp.m3,
    }
    ssp_closed_schemas = {
        "M4": schema_defs.ssp.m4,
        "M5": schema_defs.ssp.m5,
    }
    ssp_agg_schemas = {
        "M6": schema_defs.ssp.m6,
    }
    ssp_strat_schemas = {
        "M7": schema_defs.ssp.m7,
    }

    # FRA schemas
    fra_work_outcomes_tanf_exiters = {"TE1": schema_defs.fra.te1}

    # Program Audit schemas
    program_audit_schemas = {
        "T1": schema_defs.program_audit.t1,
        "T2": schema_defs.program_audit.t2,
        "T3": schema_defs.program_audit.t3,
    }

    @classmethod
    def get_section(cls, program_type: str, section_abbrev: str):
        """Get full section name given the program type and section abbreviation used in the datafile."""
        match program_type:
            case (
                DataFile.ProgramType.TANF
                | DataFile.ProgramType.SSP
                | DataFile.ProgramType.TRIBAL
            ):
                match section_abbrev:
                    case "A":
                        return DataFile.Section.ACTIVE_CASE_DATA
                    case "C":
                        return DataFile.Section.CLOSED_CASE_DATA
                    case "G":
                        return DataFile.Section.AGGREGATE_DATA
                    case "S":
                        return DataFile.Section.STRATUM_DATA

    @classmethod
    def get_schema(
        cls, program_type: str, section: DataFile.Section | str, record_type: str
    ):
        """Get specific schema."""
        schemas = cls.get_schemas(program_type, section)
        return schemas.get(record_type, None)

    @classmethod
    def get_schemas(
        cls,
        program_type: str,
        section: DataFile.Section | str,
        is_program_audit: bool = False,
    ):
        """Get all schemas for a program type and section."""
        print("program_type")
        print(program_type)
        match program_type:
            case DataFile.ProgramType.TANF:
                match section:
                    case DataFile.Section.ACTIVE_CASE_DATA | "A":
                        if is_program_audit:
                            return cls.tan_active_audit_schemas
                        return cls.tan_active_schemas
                    case DataFile.Section.CLOSED_CASE_DATA | "C":
                        return cls.tan_closed_schemas
                    case DataFile.Section.AGGREGATE_DATA | "G":
                        return cls.tan_agg_schemas
                    case DataFile.Section.STRATUM_DATA | "S":
                        return cls.tan_strat_schemas
            case DataFile.ProgramType.SSP:
                match section:
                    case DataFile.Section.ACTIVE_CASE_DATA | "A":
                        return cls.ssp_active_schemas
                    case DataFile.Section.CLOSED_CASE_DATA | "C":
                        return cls.ssp_closed_schemas
                    case DataFile.Section.AGGREGATE_DATA | "G":
                        return cls.ssp_agg_schemas
                    case DataFile.Section.STRATUM_DATA | "S":
                        return cls.ssp_strat_schemas
            case DataFile.ProgramType.TRIBAL:
                match section:
                    case DataFile.Section.ACTIVE_CASE_DATA | "A":
                        return cls.tribal_active_schemas
                    case DataFile.Section.CLOSED_CASE_DATA | "C":
                        return cls.tribal_closed_schemas
                    case DataFile.Section.AGGREGATE_DATA | "G":
                        return cls.tribal_agg_schemas
                    case DataFile.Section.STRATUM_DATA | "S":
                        return cls.tribal_strat_schemas
            case DataFile.ProgramType.FRA:
                match section:
                    case DataFile.Section.FRA_WORK_OUTCOME_TANF_EXITERS:
                        return cls.fra_work_outcomes_tanf_exiters
                    case DataFile.Section.FRA_SECONDRY_SCHOOL_ATTAINMENT:
                        return {}
                    case DataFile.Section.FRA_SUPPLEMENT_WORK_OUTCOMES:
                        return {}
            case "Program Audit":
                return cls.program_audit_schemas
