import flet as ft
from pyModbusTCP.server import ModbusServer

from backends.modbus_backend import AppMode, ModbusBackend


class ServerBackend(ModbusBackend):
    mode = AppMode.SERVER

    def __init__(self, host: str, port: int):
        super().__init__(host, port)
        self.server = ModbusServer(host=host, port=port, no_block=True)

    @property
    def action_label(self) -> str:
        return "Iniciar servidor" if not self.is_active() else "Detener servidor"

    @property
    def status_text(self) -> str:
        if self.is_active():
            return f"Servidor activo en {self.host}:{self.port}"
        return "Servidor detenido"

    @property
    def status_color(self) -> str:
        return ft.Colors.GREEN if self.is_active() else ft.Colors.GREY

    def activate(self) -> tuple[bool, str]:
        if self.is_active():
            self.deactivate()
            return True, "Servidor detenido"
        self.server.start()
        return True, self.status_text

    def deactivate(self) -> None:
        if self.is_active():
            self.server.stop()

    def is_active(self) -> bool:
        return self.server.is_run

    def read_holding_registers(self, address: int, count: int) -> list[int] | None:
        return self.server.data_bank.get_holding_registers(address, count)

    def write_holding_register(self, address: int, value: int) -> bool:
        return bool(self.server.data_bank.set_holding_registers(address, [value]))
