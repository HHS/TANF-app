"""Set permissions for users."""
import copy
from collections import ChainMap
from typing import List, Optional, TYPE_CHECKING

from django.apps import apps
from django.db.models import Q, QuerySet
from rest_framework import permissions

if TYPE_CHECKING:
    from django.contrib.auth.models import Permission


# Q objects that can be used to query for default permissions
# Ref: https://docs.djangoproject.com/en/3.2/topics/auth/default/#default-permissions # noqa
add_permissions_q = Q(codename__startswith='add_')
change_permissions_q = Q(codename__startswith='change_')
delete_permissions_q = Q(codename__startswith='delete_')
view_permissions_q = Q(codename__startswith='view_')


def get_permission_ids_for_model(
    app_label: str,
    model_name: str,
    filters: Optional[List[Q]] = None,
    exclusions: Optional[List[Q]] = None
) -> QuerySet['Permission']:
    """Retrieve the permissions associated with a given model.

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


def is_own_stt(request, view):
    """Verify user belongs to requested STT."""
    # Depending on the request, the STT could be found in three different places
    # so we will merge all together and just do one check
    request_parameters = ChainMap(
        view.kwargs,
        request.query_params,
        request.data
    )
    requested_stt = request_parameters.get('stt')
    user_stt = request.user.stt_id if hasattr(request.user, 'stt_id') else None

    return bool(
        user_stt is not None and
        (requested_stt in [None, str(user_stt)])
    )


def is_in_group(user, group_name):
    """Take a user and a group name, and returns `True` if the user is in that group."""
    return user.groups.filter(name=group_name).exists()


class IsUser(permissions.BasePermission):
    """Object-level permission to only allow owners of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        """Check if user has required permissions."""
        return obj == request.user


class IsAdmin(permissions.BasePermission):
    """Permission for admin-only views."""

    def has_object_permission(self, request, view, obj):
        """Check if a user is admin or superuser."""
        return request.user.is_authenticated and request.user.is_admin

    def has_permission(self, request, view):
        """Check if a user is admin or superuser."""
        return request.user.is_authenticated and request.user.is_admin


class IsOFAAdmin(permissions.BasePermission):
    """Permission for OFA Analyst only views."""

    def has_permission(self, request, view):
        """Check if a user is a OFA Admin."""
        return is_in_group(request.user, "OFA Admin")


class IsDataAnalyst(permissions.BasePermission):
    """Permission for Data Analyst only views."""

    def has_permission(self, request, view):
        """Check if a user is a data analyst."""
        return is_in_group(request.user, "Data Analyst")


class DjangoModelCRUDPermissions(permissions.DjangoModelPermissions):
    """TODO."""

    def __init__(self):
        # Use deepcopy to prevent overwriting the parent class perms_map
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


class DataFilePermissions(DjangoModelCRUDPermissions):
    """Permission for data file downloads & uploads."""

    def has_permission(self, request, view):
        """Check if a user has permission to view data files."""
        has_permission = super().has_permission(request, view)

        # Data Analysts are limited to only data files for their designated STT
        if has_permission and request.user.is_data_analyst:
            has_permission = is_own_stt(request, view)

        return has_permission

    def has_object_permission(self, request, view, obj):
        """Check if a user can interact with a specific file, based on STT.

        This is used in cases where we call .get_object() to retrieve a data_file
        and do not have the STT available in the request, ie. data file was
        requested for download via the ID of the data_file. This is not called
        on POST requests (creating new data_files) or for a list of data_files.
        """
        # Data Analysts can only see files uploaded for their designated STT
        if request.user.is_data_analyst:
            user_stt = (
                request.user.stt_id
                if hasattr(request.user, 'stt_id')
                else None
            )
            return user_stt == obj.stt_id

        return super().has_object_permission(request, view, obj)
