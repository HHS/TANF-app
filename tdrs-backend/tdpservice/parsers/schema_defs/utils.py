from .. import schema_defs
from tdpservice.data_files.models import DataFile
import logging

logger = logging.getLogger(__name__)

def get_schema_options(program, section, query=None, model=None, model_name=None):
    """Centralized function to return the appropriate schema for a given program, section, and query.

    TODO: need to rework this docstring as it is outdated hence the weird ';;' for some of them.

    @param program: the abbreviated program type (.e.g, 'TAN')
    @param section: the section of the file (.e.g, 'A');; or ACTIVE_CASE_DATA
    @param query: the query for section_names (.e.g, 'section', 'models', etc.)
    @return: the appropriate references (e.g., ACTIVE_CASE_DATA or {t1,t2,t3}) ;; returning 'A'
    """
    schema_options = {
        'TAN': {
            'A': {
                'section': DataFile.Section.ACTIVE_CASE_DATA,
                'models': {
                    'T1': schema_defs.tanf.t1,
                    'T2': schema_defs.tanf.t2,
                    'T3': schema_defs.tanf.t3,
                }
            },
            'C': {
                'section': DataFile.Section.CLOSED_CASE_DATA,
                'models': {
                    'T4': schema_defs.tanf.t4,
                    'T5': schema_defs.tanf.t5,
                }
            },
            'G': {
                'section': DataFile.Section.AGGREGATE_DATA,
                'models': {
                    'T6': schema_defs.tanf.t6,
                }
            },
            'S': {
                'section': DataFile.Section.STRATUM_DATA,
                'models': {
                    'T7': schema_defs.tanf.t7,
                }
            }
        },
        'SSP': {
            'A': {
                'section': DataFile.Section.SSP_ACTIVE_CASE_DATA,
                'models': {
                    'M1': schema_defs.ssp.m1,
                    'M2': schema_defs.ssp.m2,
                    'M3': schema_defs.ssp.m3,
                }
            },
            'C': {
                'section': DataFile.Section.SSP_CLOSED_CASE_DATA,
                'models': {
                    'M4': schema_defs.ssp.m4,
                    'M5': schema_defs.ssp.m5,
                }
            },
            'G': {
                'section': DataFile.Section.SSP_AGGREGATE_DATA,
                'models': {
                    'M6': schema_defs.ssp.m6,
                }
            },
            'S': {
                'section': DataFile.Section.SSP_STRATUM_DATA,
                'models': {
                    'M7': schema_defs.ssp.m7,
                }
            }
        },
        'Tribal TAN': {
            'A': {
                'section': DataFile.Section.TRIBAL_ACTIVE_CASE_DATA,
                'models': {
                    'T1': schema_defs.tribal_tanf.t1,
                    'T2': schema_defs.tribal_tanf.t2,
                    'T3': schema_defs.tribal_tanf.t3,
                }
            },
            'C': {
                'section': DataFile.Section.TRIBAL_CLOSED_CASE_DATA,
                'models': {
                    'T4': schema_defs.tribal_tanf.t4,
                    'T5': schema_defs.tribal_tanf.t5,
                }
            },
            'G': {
                'section': DataFile.Section.TRIBAL_AGGREGATE_DATA,
                'models': {
                    'T6': schema_defs.tribal_tanf.t6,
                }
            },
            'S': {
                'section': DataFile.Section.TRIBAL_STRATUM_DATA,
                'models': {
                    'T7': schema_defs.tribal_tanf.t7,
                }
            },
        },
    }

    if query == "text":
        for prog_name, prog_dict in schema_options.items():
            for sect, val in prog_dict.items():
                if val['section'] == section:
                    return {'program_type': prog_name, 'section': sect}
        raise ValueError("Model not found in schema_defs")
    elif query == "section":
        return schema_options.get(program, {}).get(section, None)[query]
    elif query == "models":
        links = schema_options.get(program, {}).get(section, None)

        # if query is not chosen or wrong input, return all options
        # query = 'models', model = 'T1'
        models = links.get(query, links)

        if model_name is None:
            return models
        elif model_name not in models.keys():
            logger.debug(f"Model {model_name} not found in schema_defs")
            return []  # intentionally trigger the error_msg for unknown record type
        else:
            return models.get(model_name, models)


'''
text -> section YES
text -> models{} YES
text -> model YES
datafile -> model
    ^ section -> program -> model
datafile -> text
model -> text YES
section -> text

text**: input string from the header/file
'''

def get_program_models(str_prog, str_section):
    """Return the models dict for a given program and section."""
    return get_schema_options(program=str_prog, section=str_section, query='models')

def get_program_model(str_prog, str_section, str_model):
    """Return singular model for a given program, section, and name."""
    return get_schema_options(program=str_prog, section=str_section, query='models', model_name=str_model)

def get_section_reference(str_prog, str_section):
    """Return the named section reference for a given program and section."""
    return get_schema_options(program=str_prog, section=str_section, query='section')

def get_text_from_df(df):
    """Return the short-hand text for program, section for a given datafile."""
    return get_schema_options("", section=df.section, query='text')

def get_schema(line, section, program_type):
    """Return the appropriate schema for the line."""
    line_type = line[0:2]
    return get_schema_options(program_type, section, query='models', model_name=line_type)
