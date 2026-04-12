from enum import Enum

import flet as ft


class AppMode(str, Enum):
    SERVER = "server"
    CLIENT = "client"


class ModbusBackend:
    mode: AppMode

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    @property
    def action_label(self) -> str:
        raise NotImplementedError

    @property
    def status_text(self) -> str:
        raise NotImplementedError

    @property
    def status_color(self) -> str:
        raise NotImplementedError

    def activate(self) -> tuple[bool, str]:
        raise NotImplementedError

    def deactivate(self) -> None:
        raise NotImplementedError

    def is_active(self) -> bool:
        raise NotImplementedError

    def read_holding_registers(self, address: int, count: int) -> list[int] | None:
        raise NotImplementedError

    def write_holding_register(self, address: int, value: int) -> bool:
        raise NotImplementedError
