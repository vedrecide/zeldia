from __future__ import annotations

import asyncio
import json
import sys
import zlib
from collections import defaultdict
from typing import Any, Optional, Awaitable, Callable, SupportsInt, TYPE_CHECKING

import aiohttp

from zeldia.enums.opcodes import OPCodes
from zeldia.runner import Runner

if TYPE_CHECKING:
    from zeldia.flags.intents import Intents


API_VERSION = 10

GATEWAY_URL_MAP: dict[bool, str] = {
    True: f"wss://gateway.discord.gg/?v={API_VERSION}&encoding=json&compress=true",
    False: f"wss://gateway.discord.gg/?v={API_VERSION}&encoding=json",
}

EventCallbackT = Callable[..., Awaitable[None]]


class GatewayClient:
    events: dict[str, EventCallbackT]

    _socket: aiohttp.ClientWebSocketResponse
    _interval: float | None

    def __init__(
        self,
        token: str,
        intents: SupportsInt | "Intents" | None = 0,
        zlib_compression: bool = False,
        **options,
    ) -> None:
        self.session = aiohttp.ClientSession()
        self.token = token
        self.intents = intents
        self.compress = zlib_compression
        self.events = defaultdict(list)

        self._socket = None
        self._interval = None
        self._loop = options.pop("loop", asyncio.get_event_loop())
        self._runner = Runner()
        self._buffer = bytearray()
        self._decompressor = zlib.decompressobj()

    def on(self, event: str) -> Callable[[EventCallbackT], EventCallbackT]:
        def register_handler(handler: EventCallbackT) -> EventCallbackT:
            self.events[event].append(handler)

            return handler

        return register_handler

    def once(self, event: str) -> Callable[[EventCallbackT], EventCallbackT]:
        def register_handler(handler: EventCallbackT) -> EventCallbackT:
            async def wrapper(*args, **kwargs) -> None:
                await handler(*args, **kwargs)

                self.off(event, wrapper)

            self.events[event].append(wrapper)

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

    @property
    def _identify_payload(self) -> dict[str, Any]:
        return {
            "op": OPCodes.IDENTIFY,
            "d": {
                "token": self.token,
                # type: ignore fix this
                "intents": self.intents.value,
                "properties": {
                    "os": sys.platform,
                    "browser": "zeldia",
                    "device": "zeldia",
                },
            },
        }

    async def connect(self):
        async with self.session.ws_connect(GATEWAY_URL_MAP[self.compress]) as ws:
            self._socket = ws
            async for msg in self._socket:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self._handle_payload(
                        msg.data if self.compress else json.loads(msg.data)
                    )

    async def _start_heartbeating(self, payload: dict[str, Any]) -> None:
        await self._socket.send_json(self._identify_payload)

        self._interval = payload["d"]["heartbeat_interval"] / 1000
        self._loop.create_task(self._runner.start(self))

    async def _handle_payload(self, raw: str | bytes) -> None:
        if isinstance(raw, bytes):
            self._buffer.extend(raw)
            if len(raw) < 4 or raw[-4:] != b"\x00\x00\xff\xff":
                return

            raw = self._decompressor.decompress(self._buffer).decode("UTF-8")
            self._buffer = bytearray()

        payload = json.loads(raw)

        opcode = payload.get("op")

        if opcode == OPCodes.HEARTBEAT_ACK:
            self._runner.ack()
        elif opcode == OPCodes.HELLO:
            await self._start_heartbeating(payload)
        elif opcode == OPCodes.DISPATCH:
            event = payload.get("t")
            data = payload.get("d")

            await self.emit(event.lower(), data)

    async def close(self, *, code: int = 4000) -> None:
        await self._socket.close(code=code)

    def login(self) -> None:
        try:
            self._loop.run_until_complete(self.connect())
        except KeyboardInterrupt:
            self._loop.run_until_complete(self.close())
