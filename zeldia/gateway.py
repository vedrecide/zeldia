import aiohttp
import json
import typing as t
import asyncio
import sys
import zlib

from zeldia.enums.opcodes import OPCodes
from zeldia.runner import Runner


if t.TYPE_CHECKING:
    from zeldia.flags.intents import Intents


API_VERSION = 10
GATEWAY_URL_1 = f"wss://gateway.discord.gg/?v={API_VERSION}&encoding=json"
GATEWAY_URL_2 = f"wss://gateway.discord.gg/?v={API_VERSION}&encoding=json&compress=true"


class GatewayClient:
    def __init__(
        self,
        token: str,
        intents: t.Union[t.SupportsInt, "Intents"],
        zlib_compression: bool,
        **options,
    ) -> None:
        # Public fields
        self.session = aiohttp.ClientSession()
        self.token = token
        self.intents = intents
        self.compress = zlib_compression

        # Private fields
        self._socket: aiohttp.ClientWebSocketResponse = None
        self._interval: float = None
        self._loop = options.pop("loop", asyncio.get_event_loop())
        self._runner = Runner()
        self._buffer = bytearray()
        self._decompressor = zlib.decompressobj()

    @property
    def _identify_payload(self) -> dict[str, t.Any]:
        return {
            "op": OPCodes.IDENTIFY,
            "d": {
                "token": self.token,
                "intents": self.intents,
                "properties": {
                    "os": sys.platform,
                    "browser": "zeldia",
                    "device": "zeldia",
                },
            },
        }

    async def _connect(self):
        async with self.session.ws_connect(
            GATEWAY_URL_2 if self.compress else GATEWAY_URL_1
        ) as ws:
            self._socket = ws
            async for msg in self._socket:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self._handle_payload(
                        msg.data if self.session else json.loads(msg.data)
                    )

    async def _start_heartbeating(self, data: dict[str, t.Any]) -> None:
        await self._socket.send_json(self._identify_payload)
        self._interval = data["heartbeat_interval"] / 1000
        self._loop.create_task(self._runner.start(self))

    async def _handle_payload(self, payload: t.Union[dict[str, t.Any], bytes]) -> None:
        if isinstance(payload, bytes):
            self._buffer.extend(payload)
            if len(payload) < 4 or payload[-4:] != b"\x00\x00\xff\xff":
                return

            payload = self.__decompressor.decompress(self._buffer).decode("UTF-8")
            self._buffer = bytearray()

        opcode = json.loads(payload).get("op") if self.compress else payload.get("op")
        data = json.loads(payload).get("d") if self.compress else payload.get("d")

        if opcode == OPCodes.HELLO:
            await self._start_heartbeating(data)
        elif opcode == OPCodes.HEARTBEAT_ACK:
            self._runner.ack()

    async def _close(self, *, code: int = 4000) -> None:
        await self._socket.close(code=code)

    def login(self) -> None:
        try:
            self._loop.run_until_complete(self._connect())
        except KeyboardInterrupt:
            self._loop.run_until_complete(self._close())
