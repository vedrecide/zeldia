from __future__ import annotations

import attrs

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zeldia.rest.http import HTTPClient
    from zeldia.models.snowflake import Snowflake
    from zeldia.enums.channel_type import ChannelType


@attrs.define(kw_only=True, slots=True, repr=True)
class BaseChannel:
    http_client: HTTPClient
    id: Snowflake
    type: ChannelType
