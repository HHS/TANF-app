"""Set permissions for users."""
from tdpservice.stts.models import STT
from tdpservice.users.models import AccountApprovalStatusChoices
from rest_framework import permissions
from django.db.models import Q, QuerySet
from django.contrib.auth.management import create_permissions
from django.apps import apps
from collections import ChainMap
from copy import deepcopy
from typing import List, Optional, TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)


if TYPE_CHECKING:  # pragma: no cover
    from django.contrib.auth.models import Permission  # pragma: no cover


# Q objects that can be used to query for default permissions
# Ref: https://docs.djangoproject.com/en/3.2/topics/auth/default/#default-permissions # noqa
add_permissions_q = Q(codename__startswith='add_')
change_permissions_q = Q(codename__startswith='change_')
delete_permissions_q = Q(codename__startswith='delete_')
view_permissions_q = Q(codename__startswith='view_')


def create_perms(_apps, *_):
    """Create permissions for all installed apps.

    Intended for use in data migrations that add/edit/remove group permissions.

    This is needed because Django does not actually create any Content Types
    or Permissions until a post_migrate signal is raised after the completion
    of `manage.py migrate`. When a migration is run as part of a set for a
    freshly created database, that signal will not run until all migrations are
    complete - resulting in no permissions for any Group.

    For more info: https://code.djangoproject.com/ticket/29843
    """
    for app_config in _apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=_apps, verbosity=0)
        app_config.models_module = None


def get_permission_ids_for_model(
    app_label: str,
    model_name: str,
    filters: Optional[List[Q]] = None,
    exclusions: Optional[List[Q]] = None
) -> QuerySet['Permission']:
    """Retrieve the permissions associated with a given model.

    Intended for use in data migrations that add/edit/remove group permissions.

    Optionally apply a list of Q objects as filters or exclusions that will be
    chained together via an OR clause to the database.

    For more information about using Q objects, refer to the documentation:
    https://docs.djangoproject.com/en/3.2/ref/models/querysets/#django.db.models.Q # noqa

    :param app_label: the lowercase string name of the Django app
    :param model_name: the lowercase string name of the Model class
    :param filters: a list of Q objects to be applied as a filter clause
    :param exclusions: a list of Q objects to be applied as an exclude clause
    """
    # NOTE: We must use the historical version of the model from `apps` to
    #       assert deterministic behavior in both migrations and runtime code.
    queryset = apps.get_model('auth', 'Permission').objects.filter(
        content_type__app_label=app_label,
        content_type__model=model_name
    )

    # If any filters were supplied then chain them together with OR clauses
    # and apply the complete clause as a `filter` to the DB query.
    if filters:
        query_filters = Q()
        for q_filter in filters:
            query_filters |= q_filter

        queryset = queryset.filter(query_filters)

    # If any exclusions were supplied then chain them together with OR clauses
    # and apply the complete clause as an `exclude` to the DB query.
    if exclusions:
        exclusion_filters = Q()
        for exclusion in exclusions:
            exclusion_filters |= exclusion

        queryset = queryset.exclude(exclusion_filters)

    return queryset.values_list('id', flat=True)


def get_requested_stt(request, view):
    """Get stt from a valid request."""
    request_parameters = ChainMap(
        view.kwargs,
        request.query_params,
        request.data
    )
    return request_parameters.get('stt')


def is_own_region(user, requested_stt):
    """Verify user belongs to the requested region based on the stt in the request."""
    requested_region = (
        STT.objects.get(id=requested_stt).region
        if requested_stt else None
    )
    return bool(
        user.region is not None and
        (requested_region in [None, user.region])
    )


def is_own_stt(user, requested_stt):
    """Verify user belongs to requested STT."""
    user_stt = user.stt.id if hasattr(user, 'stt') else None
    return bool(
        user_stt is not None and
        (requested_stt in [None, str(user_stt)])
    )


class IsApprovedPermission(permissions.DjangoModelPermissions):
    """Generic permission class ensuring a user has been assigned a group and is approved."""

    def has_permission(self, request, view):
        """Return True if the user has been assigned a group and is approved."""
        logging.debug(f"{self.__class__.__name__}: {request} ; {view}")
        return (request.user.groups.first() is not None and
                request.user.account_approval_status == AccountApprovalStatusChoices.APPROVED)


class DjangoModelCRUDPermissions(permissions.DjangoModelPermissions):
    """The request is authorized using `django.contrib.auth` permissions.

    See: https://docs.djangoproject.com/en/dev/topics/auth/#permissions

    It ensures that the user is authenticated, and has the appropriate
    `view`/`add`/`change`/`delete` permissions on the model.

    This permission can only be applied against view classes that
    provide a `.queryset` attribute.
    """

    def __init__(self):
        # Use deepcopy to prevent overwriting the parent class perms_map
        self.perms_map = deepcopy(self.perms_map)
        # We also want to check for the `view` permission for GET requests.
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class DataFilePermissions(DjangoModelCRUDPermissions):
    """Permission for data file downloads & uploads."""

    def has_permission(self, request, view):
        """Check if a user has the relevant Model Permissions for DataFile.

        Certain groups may also have additional constraints applied here, that
        cannot be determined by the base permissions alone. For example, a
        Data Analyst will only have permission to files within their STT and a
        Regional Manager will only have permission to files within their region.
        """
        logging.debug(f"{self.__class__.__name__}: {request} ; {view}")

        # Checks for existence of `data_files.view_datafile` Permission
        has_permission = super().has_permission(request, view)

        # Data Analysts are limited to only data files for their designated STT
        # Regional Staff are limited to only files for their designated Region
        if has_permission and (
            request.user.is_data_analyst or
            request.user.is_regional_staff
        ):
            perms_function = (
                is_own_region if request.user.is_regional_staff else is_own_stt
            )
            has_permission = perms_function(
                request.user,
                get_requested_stt(request, view)
            )

        return has_permission

    def has_object_permission(self, request, view, obj):
        """
        Check if a user can interact with a specific file, based on STT.

        This is used in cases where we call .get_object() to retrieve a data_file
        and do not have the STT available in the request, ie. data file was
        requested for download via the ID of the data_file. This is not called
        on POST requests (creating new data_files) or for a list of data_files.
        """
        # Data Analysts can only see files uploaded for their designated STT
        if request.user.is_data_analyst:
            user_stt = (
                request.user.stt.id
                if hasattr(request.user, 'stt')
                else None
            )
            return user_stt == obj.stt_id

        # Regional Staff can only see files uploaded for their designated Region
        if request.user.is_regional_staff:
            user_region = (
                request.user.region.id
                if hasattr(request.user, 'region')
                else None
            )
            return user_region == obj.stt.region.id

        return super().has_object_permission(request, view, obj)


class UserPermissions(DjangoModelCRUDPermissions):
    """Permission to allow modifying records related to the User's account."""

    def has_permission(self, request, view):
        """Check if user has permission to User related resources."""
        # NOTE: There are currently no uses of this permission that don't deal
        #       with object permissions on an individual instance.
        #       If this is added to an additional viewset in the future that
        #       implements the `list` view.action we will need to check model
        #       permissions directly using super().has_permission for that
        #       action only. In that case actions dealing with individual
        #       object permissions will need to be passed through this function
        #       by returning True.

        return True

    def has_object_permission(self, request, view, obj):
        """
        Check if the object being modified belongs to the user.

        Alternatively, check if the user is an admin and grant permission.
        """
        # Regional Staff can only see files uploaded for their designated Region
        if request.user.groups.filter(name="OFA Regional Staff").exists():
            user_region = (
                request.user.region.id
                if hasattr(request.user, 'region')
                else None
            )
            return user_region == obj.stt.region_id

        # Check if user is an admin
        is_admin = request.user.groups.filter(name__in=["OFA System Admin", "OFA Admin"]).exists()
        return obj == request.user or is_admin
