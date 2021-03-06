import orjson
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.utils.translation import gettext as _

from zerver.decorator import REQ, has_request_variables
from zerver.lib.actions import do_add_submessage
from zerver.lib.message import access_message
from zerver.lib.response import json_error, json_success
from zerver.lib.validator import check_int
from zerver.models import UserProfile


# transaction.atomic is required since we use FOR UPDATE queries in access_message.
@transaction.atomic
@has_request_variables
def process_submessage(
    request: HttpRequest,
    user_profile: UserProfile,
    message_id: int = REQ(json_validator=check_int),
    msg_type: str = REQ(),
    content: str = REQ(),
) -> HttpResponse:
    message, user_message = access_message(user_profile, message_id, lock_message=True)

    try:
        orjson.loads(content)
    except orjson.JSONDecodeError:
        return json_error(_("Invalid json for submessage"))

    do_add_submessage(
        realm=user_profile.realm,
        sender_id=user_profile.id,
        message_id=message.id,
        msg_type=msg_type,
        content=content,
    )
    return json_success()
