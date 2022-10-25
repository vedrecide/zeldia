import asyncio
import typing
import logging

from zeldia.enums.opcodes import OPCodes


if typing.TYPE_CHECKING:
    from zeldia.gateway import GatewayClient


logger = logging.getLogger(__name__)


class Runner:
    def __init__(self) -> None:
        self.counter = 0
        self._ack: bool = True

    async def start(self, gateway: "GatewayClient") -> None:
        while True:
            if not self._ack:
                logger.error("Something went wrong, Aborting the process.")
                gateway._close()

            await gateway._socket.send_json(self.payload())
            self._ack = False
            await asyncio.sleep(gateway._interval)

    def payload(self) -> dict[str, float]:
        return {"op": OPCodes.HEARTBEAT, "d": self.counter}

    def ack(self) -> None:
        self._ack = True
