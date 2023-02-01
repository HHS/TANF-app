"""A commonly-shared set of definitions for line schemas in datafiles."""

def get_header_schema():
    """Return the schema dictionary for the header record."""
    """DEFINITION SOURCE:
    https://www.acf.hhs.gov/sites/default/files/documents/ofa/transmission_file_header_trailer_record.pdf

    DESCRIPTION		LENGTH	FROM	TO	COMMENT
    Title		    6	1	6	Value	=	HEADER
    YYYYQ	        5	7	11	Value	=	YYYYQ
    Type 	        1	12	12	A=Active;	C=Closed;	G=Aggregate,	S=Stratum
    State Fips	    2	13	14	"2	digit	state	code	000	a	tribe"
    Tribe Code	    3	15	17	"3	digit	tribe	code	000	a	state"
    Program	Type	3	18	20	Value	=	TAN	(TANF)	or	Value	=	SSP	(SSP-MOE)
    Edit Indicator	1	21	21	1=Return	Fatal	&	Warning	Edits	2=Return	Fatal	Edits	only
    Encryption      1	22	22	E=SSN	is	encrypted	Blank	=	SSN	is	not	encrypted
    Update      	1	23	23	N	=	New	data	D	=	Delete	existing	data	U
    QUARTERS:
        Q=1	(Jan-Mar)
        Q=2	(Apr-Jun)
        Q=3	(Jul-Sep)
        Q=4	(Oct-Dec)
    Example:
    HEADERYYYYQTFIPSSP1EN
    """
    header_schema = {
            'title':        {'type': 'string', 'required': True, 'allowed': ['HEADER']},
            'year':         {'type': 'string', 'required': True, 'regex': '^20[0-9]{2}$'},  # 4 digits, starts with 20
            'quarter':      {'type': 'string', 'required': True, 'allowed': ['1', '2', '3', '4']},
            'type':         {'type': 'string', 'required': True, 'allowed': ['A', 'C', 'G', 'S']},
            'state_fips':   {'type': 'string', 'required': True, 'regex': '^[0-9]{2}$'},  # 2 digits
            'tribe_code':   {'type': 'string', 'required': False, 'regex': '^([0-9]{3}|[ ]{3})$'},  # digits or spaces
            'program_type': {'type': 'string', 'required': True, 'allowed': ['TAN', 'SSP']},
            'edit':         {'type': 'string', 'required': True, 'allowed': ['1', '2']},
            'encryption':   {'type': 'string', 'required': True, 'allowed': ['E', ' ']},
            'update':       {'type': 'string', 'required': True, 'allowed': ['N', 'D', 'U']},
        }
    # we're limited to string for all values otherwise we have to cast to int in header and it fails
    # with a raised ValueError instead of in the validator.errors
    return header_schema

def get_trailer_schema():
    """Return the schema dictionary for the trailer record."""
    """DEFINITION SOURCE:
    https://www.acf.hhs.gov/sites/default/files/documents/ofa/transmission_file_header_trailer_record.pdf
    length of 24
    DESCRIPTION LENGTH  FROM    TO  COMMENT
    Title       7       1       7   Value = TRAILER
    Record Count7       8       14  Right Adjusted
    Blank       9       15      23  Value = spaces
    Example:
    'TRAILER0000001         '
    """
    trailer_schema = {
        'title':        {'type': 'string', 'required': True, 'allowed': ['TRAILER']},
        'record_count': {'type': 'string', 'required': True, 'regex': '^[0-9]{7}$'},
        'blank':        {'type': 'string', 'required': True, 'regex': '^[ ]{9}$'},
    }
    return trailer_schema
