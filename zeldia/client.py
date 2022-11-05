from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import (
    Optional,
    Awaitable,
    Callable,
    SupportsInt,
    TYPE_CHECKING,
    Sequence,
)

import aiohttp

from zeldia.events import Events
from zeldia.gateway.gateway import Gateway
from zeldia.rest.http import HTTPClient

if TYPE_CHECKING:
    from zeldia.flags.intents import Intents


EventCallbackT = Callable[..., Awaitable[None]]


class GatewayClient:

    __slots__: Sequence[str] = (
        "events",
        "http",
        "gateway",
        "_socket",
        "_interval",
        "_loop",
        "_runner",
        "_buffer",
        "_decompressor",
    )

    events: dict[str, EventCallbackT]

    _socket: aiohttp.ClientWebSocketResponse
    _interval: float | None

    def __init__(
        self,
        token: str,
        intents: SupportsInt | "Intents" | None = 0,
        session: aiohttp.ClientSession = None,
        zlib_compression: bool = False,
        http_client: HTTPClient = None,
        **options,
    ) -> None:
        self.events = defaultdict(list)
        self.gateway = Gateway(
            token=token,
            intents=intents,
            session=aiohttp.ClientSession() if not session else session,
            compress=zlib_compression,
            emitter=self.emit
        )
        self.http = HTTPClient(token) if not http_client else http_client

        self._loop = options.pop("loop", asyncio.get_event_loop())

    def on(self, event: str | Events) -> Callable[[EventCallbackT], EventCallbackT]:
        def register_handler(handler: EventCallbackT) -> EventCallbackT:
            self.events[event.value if isinstance(event, Events) else event].append(
                handler
            )

            return handler

        return register_handler

    def once(self, event: str | Events) -> Callable[[EventCallbackT], EventCallbackT]:
        def register_handler(handler: EventCallbackT) -> EventCallbackT:
            async def wrapper(*args, **kwargs) -> None:
                await handler(*args, **kwargs)

                self.off(event.value if isinstance(event, Events) else event, wrapper)

            self.events[event.value if isinstance(event, Events) else event].append(
                wrapper
            )

            return handler

        return register_handler

    def off(self, event: str, handler: Optional[EventCallbackT] = None) -> None:
        if handler is None:
            self.events[event] = []
        else:
            self.events[event].remove(handler)

    async def emit(self, event: str, *args, **kwargs) -> None:
        for handler in self.events[event]:
            await handler(*args, **kwargs)

    def login(self) -> None:
        try:
            self._loop.run_until_complete(self.gateway.connect())
        except KeyboardInterrupt:
            self._loop.run_until_complete(self.gateway.close())
