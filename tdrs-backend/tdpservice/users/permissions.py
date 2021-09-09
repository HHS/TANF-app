"""Set permissions for users."""
from collections import ChainMap
from copy import deepcopy
from typing import List, Optional, TYPE_CHECKING

from django.apps import apps
from django.db.models import Q, QuerySet
from rest_framework import permissions

if TYPE_CHECKING:  # pragma: no cover
    from django.contrib.auth.models import Permission  # pragma: no cover


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

def get_requested_stt(request, view):
    request_parameters = ChainMap(
        view.kwargs,
        request.query_params,
        request.data
    )
    return request_parameters.get('stt')


def is_own_region(user, requested_stt):
    """Verify user belongs to the requested region based on the stt in the request."""
    user_region = (
        Region.objects.get(id=user.region.id)
    )
    requested_region  = (
        apps.get_model('stts', 'STT')
        .objects.get(id=requested_stt).region
    )
    return user_region == requested_region

def is_own_stt(user, requested_stt):
    """Verify user belongs to requested STT."""
    user_stt = user.stt_id if hasattr(user, 'stt_id') else None
    return bool(
        user_stt is not None and
        (requested_stt in [None, str(user_stt)])
    )

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
        # Checks for existence of `data_files.view_datafile` Permission
        has_permission = super().has_permission(request, view)

        # Data Analysts are limited to only data files for their designated STT
        if has_permission and request.user.is_data_analyst:
            has_permission = is_own_stt(request, view)

        if request.user.groups.filter(name="OFA Regional Staff").exists():
            has_permission = is_own_region(request, view)

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

        # TODO: Add a conditional for Regional manager
        # https://github.com/raft-tech/TANF-app/issues/1052

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
        """Check if the object being modified belongs to the user.

        Alternatively, check if the user has been granted Model Permissions.
        """
        # If the user has the relevant model permission that will also allow
        # access to individual objects
        has_model_permission = super().has_permission(request, view)

        # TODO: Add conditional to assert regional manager can only interact
        #       with user records in their respective region.

        return obj == request.user or has_model_permission
