from __future__ import annotations

import attrs
import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zeldia.models.user import User
    from zeldia.models.thread import ThreadMetadata, ThreadMember
    from zeldia.models.snowflake import Snowflake


@attrs.define(kw_only=True, slots=True, repr=True)
class Overwrite:
    id: Snowflake
    type: int
    allow: str
    deny: str


# Have to reimplement this into different type of channels...
@attrs.define(kw_only=True, slots=True, repr=True)
class Channel:
    id: int  # TODO: Change this to Snowflake
    type: int
    guild_id: int | None  # TODO: Change this to Snowflake | None
    position: int | None
    permission_overwrites: list[Overwrite] | None
    name: str | None
    topic: str | None
    nsfw: bool | None
    last_message_id: int | None  # TODO: Change this to Snowflake | None
    bitrate: int | None
    user_limit: int | None
    rate_limit_per_user: int | None
    recipents: list[User]
    icon: str | None
    owner_id: int | None  # TODO: Change this to Snowflake | None
    application_id: int | None  # TODO: Change this to Snowflake | None
    parent_id: int | None  # TODO: Change this to Snowflake | None
    last_pin_timestamp: datetime.datetime | None
    rtc_region: str | None
    video_quality_mode: int | None
    message_count: int | None
    member_count: int | None
    thread_metadata: ThreadMetadata
    member: ThreadMember
    default_auto_archive_duration: int
    permissions: str | None
    flags: int | None
    total_message_sent: int | None
    available_tags: list[object]  # TODO: Change this to list[Tag]
    applied_tags: list[int]  # TODO: Change this to list[Snowflake]
    default_reaction_emoji: object | None  # TODO: Change this to DefaultReaction | None
    default_thread_rate_limit_per_user: int | None
    default_sort_order: int | None
