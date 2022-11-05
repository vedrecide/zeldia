from __future__ import annotations

from typing import Any

from zeldia.models.message import Message


def payload_to_message(payload: dict[str, Any]) -> Message:
    return Message(
        id=payload.get("id"),
        channel_id=payload.get("channel_id"),
        author=payload.get("author"),
        content=payload.get("content"),
        timestamp=payload.get("timestamp"),
        edited_timestamp=payload.get("edited_timestamp", None),
        tts=payload.get("tts"),
        mention_everyone=payload.get("mention_everyone"),
        mentions=payload.get("mentions"),
        mention_roles=payload.get("mention_roles"),
        mention_channels=payload.get("mention_channels"),
        attachments=payload.get("attachments"),
        embeds=payload.get("embeds"),
        reactions=payload.get("reactions"),
        nonce=payload.get("nonce", None),
        pinned=payload.get("pinned"),
        webhook_id=payload.get("webhook_id", None),
        type=payload.get("type"),
        activity=payload.get("activity"),
        application=payload.get("application"),
        application_id=payload.get("application_id"),
        message_reference=payload.get("message_reference", None),
        flags=payload.get("flags", None),
        referenced_message=payload.get("referenced_message", None),
        interaction=payload.get("interaction", None),
        thread=payload.get("thread", None),
        components=payload.get("components", None),
        sticker_items=payload.get("sticker_items", None),
        stickers=payload.get("stickers", None),
        position=payload.get("position", None),
    )
