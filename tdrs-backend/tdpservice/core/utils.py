"""Core utility classes and functions."""

import logging
from django.contrib.admin.models import LogEntry, ContentType, CHANGE


logger = logging.getLogger()


class ReadOnlyAdminMixin:
    """Mixin to enforce read-only models in Django Admin.

    e.g. => class LogEntryAdmin(ReadOnlyAdminMixin, admin.ModelAdmin)
    This mixin must be first in the param list due to the way Python
    handles Method Order Resolution for multiple inheritance.
    """

    def has_add_permission(self, request):
        """Deny all add permissions."""
        return False

    def has_change_permission(self, request, obj=None):
        """Deny all change permissions."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Deny all delete permissions."""
        return False


def log(msg, logger_context={}, level='info'):
    """Create a log in the terminal and django admin console, for email tasks."""
    log_func = logger.info

    match level:
        case 'info':
            log_func = logger.info
        case 'warn':
            log_func = logger.warn
        case 'error':
            log_func = logger.error
        case 'critical':
            log_func = logger.critical
        case 'exception':
            log_func = logger.exception

    log_func(msg)

    if logger_context:
        LogEntry.objects.log_action(
            user_id=logger_context.get('user_id'),
            change_message=msg,
            action_flag=logger_context.get('action_flag', CHANGE),
            content_type_id=ContentType.objects.get_for_model(logger_context.get('content_type', LogEntry)).pk,
            object_id=logger_context.get('object_id', None),
            object_repr=logger_context.get('object_repr', '')
        )
