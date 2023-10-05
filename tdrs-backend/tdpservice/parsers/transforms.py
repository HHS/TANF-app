"""Collection of functions used in Fields."""

from .util import transform_to_months, month_to_int

def calendar_quarter_to_rpt_month_year(month_index):
    """Transform calendar year and quarter to RPT_MONTH_YEAR."""
    def transform(value, **kwargs):
        value = str(value)
        year = value[:4]
        quarter = f"Q{value[-1]}"
        month = transform_to_months(quarter)[month_index]
        return f"{year}{month_to_int(month)}"
    return transform

def tanf_ssn_decryption_func(value, **kwargs):
    """Decrypt TANF SSN value."""
    if kwargs.get("is_encrypted", False):
        decryption_dict = {"@": "1", "9": "2", "Z": "3", "P": "4", "0": "5",
                           "#": "6", "Y": "7", "B": "8", "W": "9", "T": "0"}
        decryption_table = str.maketrans(decryption_dict)
        return value.translate(decryption_table)
    return value

def ssp_ssn_decryption_func(value, **kwargs):
    """Decrypt SSP SSN value."""
    if kwargs.get("is_encrypted", False):
        decryption_dict = {"@": "1", "9": "2", "Z": "3", "P": "4", "0": "5",
                           "#": "6", "Y": "7", "B": "8", "W": "9", "T": "0"}
        decryption_table = str.maketrans(decryption_dict)
        return value.translate(decryption_table)
    return value
