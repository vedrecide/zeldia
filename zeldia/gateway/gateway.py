from __future__ import annotations

import aiohttp
import asyncio
import json
import time
import sys
import zlib

from typing import Any, Sequence, Callable, Awaitable, TYPE_CHECKING

from zeldia.gateway.runner import Runner
from zeldia.enums.opcodes import OPCodes
from zeldia.flags.intents import Intents
from zeldia.converters import payload_to_message

if TYPE_CHECKING:
    from zeldia.models.message import Message
    

GATEWAY_URL_MAP: dict[bool, str] = {
    True: "wss://gateway.discord.gg/?v=10&encoding=json&compress=true",
    False: "wss://gateway.discord.gg/?v=10&encoding=json",
}

class Gateway:

    __slots__: Sequence[str] = (
        "token",
        "intents",
        "session",
        "compress",
        "emitter",
        "_socket",
        "_interval",
        "_loop",
        "_runner",
        "_latency",
        "_buffer",
        "_decompressor",
    )

    _socket: aiohttp.ClientWebSocketResponse
    _interval: float | None
    _latency: float

    def __init__(
        self,
        token: str,
        intents: Intents,
        emitter: Callable[[str, Any], Awaitable[None]],
        session: aiohttp.ClientSession | None = None,
        compress: bool | None = None,
        **options,
    ) -> None:
        self.token = token
        self.intents = intents
        self.session = aiohttp.ClientSession if not session else session
        self.compress = compress if compress else False
        self.emitter = emitter

        self._socket = None
        self._interval = None
        self._loop = options.pop("loop", asyncio.get_event_loop())
        self._runner = Runner()
        self._latency = 0
        self._buffer = bytearray()
        self._decompressor = zlib.decompressobj()

    @property
    def latency(self) -> float:
        return self._latency

    @property
    def identify_payload(self) -> dict[str, Any]:
        return {
            "op": OPCodes.IDENTIFY,
            "d": {
                "token": self.token,
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
                    await self.handle_payload(
                        msg.data if self.compress else json.loads(msg.data)
                    )

    async def start_heartbeating(self, payload: dict[str, Any]):
        await self._socket.send_json(self.identify_payload)

        self._interval = payload["d"]["heartbeat_interval"] / 1000
        self._loop.create_task(self._runner.start(self))

    def convert_to_model(self, event_name: str, payload: dict[str, Any]) -> "Message":
        if event_name == "MESSAGE_CREATE":
            return payload_to_message(payload)

    async def handle_payload(self, raw: str | bytes):
        if isinstance(raw, bytes):
            self._buffer.extend(raw)
            if len(raw) < 4 or raw[-4:] != b"\x00\x00\xff\xff":
                return

            raw = self._decompressor.decompress(self._buffer).decode("UTF-8")
            self._buffer = bytearray()

        payload = json.loads(raw)

        opcode = payload.get("op")

        if opcode == OPCodes.HEARTBEAT_ACK:
            self._latency = time.perf_counter() - self._runner.last_heartbeat
            self._runner.ack()
        elif opcode == OPCodes.HELLO:
            await self.start_heartbeating(payload)
        elif opcode == OPCodes.DISPATCH:
            event = payload.get("t")
            data = payload.get("d")

            await self.emitter(event.lower(), self.convert_to_model(event, data))

    async def close(self, *, code: int = 4000):
        await self._socket.close(code=code)
