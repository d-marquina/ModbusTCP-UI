import flet as ft
from pyModbusTCP.client import ModbusClient

from backends.modbus_backend import AppMode, ModbusBackend


class ClientBackend(ModbusBackend):
    mode = AppMode.CLIENT

    def __init__(self, host: str, port: int):
        super().__init__(host, port)
        self.client = ModbusClient(host=host, port=port, auto_open=False, auto_close=False)

    @property
    def action_label(self) -> str:
        return "Conectar" if not self.is_active() else "Desconectar"

    @property
    def status_text(self) -> str:
        if self.is_active():
            return f"Cliente conectado a {self.host}:{self.port}"
        return "Cliente desconectado"

    @property
    def status_color(self) -> str:
        return ft.Colors.GREEN if self.is_active() else ft.Colors.GREY

    def activate(self) -> tuple[bool, str]:
        if self.is_active():
            self.deactivate()
            return True, "Cliente desconectado"
        if not self.client.open():
            return False, f"No se pudo conectar a {self.host}:{self.port}"
        return True, self.status_text

    def deactivate(self) -> None:
        self.client.close()

    def is_active(self) -> bool:
        return self.client.is_open

    def read_holding_registers(self, address: int, count: int) -> list[int] | None:
        if not self.is_active():
            return None
        return self.client.read_holding_registers(address, count)

    def write_holding_register(self, address: int, value: int) -> bool:
        if not self.is_active():
            return False
        return bool(self.client.write_single_register(address, value))
