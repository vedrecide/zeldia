from __future__ import annotations

import datetime

from typing import final


@final
class Snowflake(int):

    __slots__ = ()

    @property
    def created_at(self) -> datetime.datetime:
        epoch = (self >> 22) / 1000
        epoch += 1420070400000

        return datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc)

    @property
    def internal_worker_id(self) -> int:
        return (self & 0x3E0000) >> 17

    @property
    def internal_process_id(self) -> int:
        return (self & 0x1F000) >> 12

    @property
    def increment(self) -> int:
        return self & 0xFFF
