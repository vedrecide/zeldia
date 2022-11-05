import abc
import asyncio
import logging
import time

from typing import Sequence, TYPE_CHECKING

from zeldia.enums.opcodes import OPCodes

if TYPE_CHECKING:
    from zeldia.client import GatewayClient


logger = logging.getLogger(__name__)


class RunnerTrait(abc.ABC):
    last_heartbeat: float

    @abc.abstractmethod
    async def start(self, gateway: "GatewayClient") -> None:
        ...

    @abc.abstractmethod
    def payload(self) -> dict[str, float]:
        ...

    @abc.abstractmethod
    def ack(self) -> None:
        ...


class Runner(RunnerTrait):

    __slots__: Sequence[str] = ("counter", "_ack", "last_heartbeat")

    last_heartbeat: float

    def __init__(self) -> None:
        self.counter = 0
        self._ack: bool = True
        self.last_heartbeat = None

    async def start(self, gateway: "GatewayClient") -> None:
        while True:
            if not self._ack:
                logger.error("Something went wrong, Aborting the process.")
                gateway._close()

            await gateway._socket.send_json(self.payload())
            self._ack = False
            self.last_heartbeat = time.perf_counter()
            await asyncio.sleep(gateway._interval)

    def payload(self) -> dict[str, float]:
        return {"op": OPCodes.HEARTBEAT, "d": self.counter}

    def ack(self) -> None:
        self._ack = True
