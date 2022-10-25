import asyncio
import time
import typing

from zeldia.enums.opcodes import OPCodes


if typing.TYPE_CHECKING:
    from zeldia.gateway import GatewayClient


class Runner:
    def __init__(self) -> None:
        self.counter = 0
        self._ack: float = 0

    async def start(self, gateway: "GatewayClient") -> None:
        while True:
            await gateway._socket.send_json(self.payload())
            self._ack = time.perf_counter()
            await asyncio.sleep(gateway._interval)

    def payload(self) -> dict[str, float]:
        return {"op": OPCodes.HEARTBEAT, "d": self.counter}
