from __future__ import annotations

import attrs
import datetime


@attrs.define(kw_only=True, slots=True, repr=True)
class ThreadMetadata:
    archived: bool
    auto_archive_duration: int
    archive_timestamp: datetime.datetime
    locked: bool
    invitable: bool | None
    create_timestamp: datetime.datetime | None


@attrs.define(kw_only=True, slots=True, repr=True)
class ThreadMember:
    id: int | None  # TODO: Change this to Snowflake | None
    user_id: int | None  # TODO: Change this to Snowflake | None
    join_timestamp: datetime.datetime
    flags: int
