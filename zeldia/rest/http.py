from __future__ import annotations

import aiohttp
import asyncio

from typing import Sequence

from zeldia.rest.route import Route
from zeldia.exceptions import InvalidRequest, MissingPermission


class HTTPClient:

    __slots__: Sequence[str] = ("_session", "_lock", "token")

    USER_AGENT = "DiscordBot (https://github.com/vedrecide/zeldia, 0.0.1)"

    def __init__(
        self, token: str, session: aiohttp.ClientSession = aiohttp.ClientSession()
    ) -> None:
        self.token = token
        self._session = session
        self._lock = asyncio.Lock()

    async def fetch(
        self,
        route: Route,
        *,
        headers: dict | None = None,
        data: dict | None = None,
        text_response: bool = False,
        return_status: bool = False,
    ) -> dict | str:
        if headers is None:
            headers = {}

        headers = {
            "User-Agent": self.USER_AGENT,
            "Authorization": f"Bot {self.token}",
            **headers,
        }

        async with self._lock:
            async with self._session.request(
                method=route.method, url=route.url, headers=headers, data=data
            ) as res:
                if return_status:
                    return res.status

                if res.status in [200, 201, 204]:
                    if text_response:
                        data = await res.text()
                    else:
                        data = await res.json()

                if res.status == 400:
                    raise InvalidRequest("Bad request - Request performed was invalid.")

                if res.status == 401:
                    raise MissingPermission(
                        "Request not authenticated - Check your API token."
                    )

                if res.status == 403:
                    raise MissingPermission(
                        "Permission not exists - Check your Permissions for API."
                    )

                if res.status == 429:
                    raise InvalidRequest("Too many requests - Slow down your requests.")

                if res.status == 500:
                    raise InvalidRequest(
                        "Internal Server Error - Something went wrong."
                    )

        return data

    async def create_message(self, channel_id: int, content: str) -> None:
        payload = {"content": content}
        await self.fetch(
            Route("POST", f"/channels/{channel_id}/messages"), data=payload
        )
