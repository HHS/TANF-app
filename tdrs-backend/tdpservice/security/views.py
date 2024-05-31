"""Views for the security app."""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.decorators import user_passes_test
from tdpservice.users.models import User, AccountApprovalStatusChoices
from rest_framework.authtoken.models import Token
from tdpservice.security.utils import token_is_valid

import logging

logger = logging.getLogger(__name__)


def can_get_new_token(user):
    """Check if user can get a new token."""
    return (
        user.is_authenticated
        and user.is_ofa_sys_admin
        and user.account_approval_status == AccountApprovalStatusChoices.APPROVED
    )


@user_passes_test(can_get_new_token, login_url="/login/")
@api_view(["GET"])
def generate_new_token(request):
    """Generate new token for the API user."""
    if request.method == "GET":
        user = User.objects.get(username=request.user)
        token, created = Token.objects.get_or_create(user=user)
        if token_is_valid(token):
            return Response(str(token))
        else:
            token.delete()
            token = Token.objects.create(user=user)
            return Response(str(token))
