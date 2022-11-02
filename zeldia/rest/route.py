from __future__ import annotations

import typing as t


class Route:
    BASE_URL = f"https://discord.com/api/v10"

    def __init__(
        self, method: t.Literal["GET", "POST", "PUT", "DELETE", "PATCH"], path: str
    ) -> None:
        self.method = method.upper()
        self.path = path

    @property
    def base_url(self) -> str:
        return self.BASE_URL

    @base_url.setter
    def base_url(self, url: str) -> None:
        self.BASE_URL = url

    @property
    def url(self) -> str:
        return self.base_url + self.path
