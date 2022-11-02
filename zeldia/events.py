from __future__ import annotations

from enum import Enum


class Events(str, Enum):
    READY = "READY"
    MESSAGE_CREATE = "MESSAGE_CREATE"
