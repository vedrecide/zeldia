from __future__ import annotations

import asyncio
import json
import sys
import zlib
from typing import Any, Awaitable, Callable, SupportsInt, TYPE_CHECKING

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


class GatewayClient:
    events: dict[str, list[Callable[..., Awaitable]]]

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
        self.events = {}

        self._socket = None
        self._interval = None
        self._loop = options.pop("loop", asyncio.get_event_loop())
        self._runner = Runner()
        self._buffer = bytearray()
        self._decompressor = zlib.decompressobj()

    def listen(self, event_name: str):
        def inner(function):
            self.events[event_name] = self.events.get(event_name, []) + [function]
            return function

        return inner

    async def emit(self, event_name, *args, **kwargs):
        for function in self.events.get(event_name, []):
            await function(*args, **kwargs)

    def off(self, event_name, function):
        self.events.get(event_name, []).remove(function)

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

    async def _connect(self):
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

    async def _close(self, *, code: int = 4000) -> None:
        await self._socket.close(code=code)

    def login(self) -> None:
        try:
            self._loop.run_until_complete(self._connect())
        except KeyboardInterrupt:
            self._loop.run_until_complete(self._close())
