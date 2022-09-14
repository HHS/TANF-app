from enum import Enum


class EmailType(Enum):
    ACCESS_REQUEST_SUBMITTED = 'Access Request Submitted'
    DATA_SUBMITTED = 'Data Submitted'
    REQUEST_APPROVED = 'Request Approved'
    REQUEST_DENIED = 'Request Denied'
    INACTIVE_ACCOUNT_10_DAYS = 'Inactive Account (10 days)'
    INACTIVE_ACCOUNT_3_DAYS = 'Inactive Account (3 days)'
    INACTIVE_ACCOUNT_1_DAYS = 'Inactive Account (1 days)'
    ACCOUNT_DEACTIVATED = 'Account is Deactivated'
