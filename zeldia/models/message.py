from __future__ import annotations

import attrs
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zeldia.enums.interaction import InteractionType


@attrs.define(kw_only=True, slots=True, repr=True)
class MessageReference:
    message_id: int | None = None  # TODO: Change this to Snowflake
    channel_id: int | None = None  # TODO: Change this to Snowflake
    guild_id: int | None = None  # TODO: Change this to Snow
    fail_if_not_exists: bool | None = None


@attrs.define(kw_only=True, slots=True, repr=True)
class MessageInteraction:
    id: int  # TODO: Change this to Snowflake
    type: InteractionType
    name: str
    user: object  # TODO: Change this to User
    member: object | None  # TODO: Change this to Member | None


@attrs.define(kw_only=True, slots=True, repr=True)
class Message:
    id: int  # TODO: Change this to Snowflake
    channel_id: int  # TODO: Change this to Snowflake
    author: object  # TODO: Change this to User
    content: str | None
    timestamp: datetime.datetime
    edited_timestamp: datetime.datetime | None
    tts: bool
    mention_everyone: bool
    mentions: list[object]  # TODO: Change this to list[User]
    mention_roles: list[int]  # TODO: Change this to list[Snowflake]
    mention_channels: list[object]  # TODO: Change this to list[ChannelMention]
    attachments: list[object]  # TODO: Change this to list[Attachment]
    embeds: list[object]  # TODO: Change this to list[Embed]
    reactions: list[object]  # TODO: Change this to list[Reaction]
    nonce: int | str | None
    pinned: bool
    webhook_id: int | None  # TODO: Change this to Snowflake | None
    type: int
    activity: object  # TODO: Change this to Activity
    application: object  # TODO: Change this to Application
    application_id: int  # TODO: Change this to Snowflake
    message_reference: MessageReference | None
    flags: int | None
    referenced_message: "Message" | None
    interaction: MessageInteraction | None
    thread: object | None  # TODO: Change this to Channel | None
    components: list[object] | None  # TODO: Change this to list[Component]
    sticker_items: list[object] | None  # TODO: Change this to list[MessageStickerItem]
    stickers: list[object] | None  # TODO: Change this to list[Sticker] | None
    position: int | None
