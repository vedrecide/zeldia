from __future__ import annotations

import attrs


@attrs.define(kw_only=True, slots=True, repr=True)
class User:
    id: int  # TODO: Change this to Snowflake
    username: str
    discriminator: str
    avatar: str | None
    bot: bool | None
    system: bool | None
    mfa_enabled: bool | None
    banner: str | None
    accent_color: int | None
    locale: str | None
    verified: bool | None
    email: str | None
    flags: int | None
    premium_type: int | None
    public_flags: int | None
