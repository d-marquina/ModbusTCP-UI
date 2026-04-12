from dataclasses import dataclass

import flet as ft


@dataclass(frozen=True)
class RegisterDefinition:
    address: str
    offset: int
    description: str


REGISTER_DEFINITIONS = [
    RegisterDefinition("40001", 0, "Valor general"),
    RegisterDefinition("40002", 1, "Velocidad"),
    RegisterDefinition("40003", 2, "Luz de proceso"),
    RegisterDefinition("40004", 3, "Pulsador simulado"),
    RegisterDefinition("40005", 4, "Valor general"),
]

REGISTER_BY_OFFSET = {definition.offset: definition for definition in REGISTER_DEFINITIONS}


def register_option(definition: RegisterDefinition) -> ft.dropdown.Option:
    return ft.dropdown.Option(
        key=str(definition.offset),
        text=f"{definition.address} | offset {definition.offset} | {definition.description}",
    )


def register_label(offset: int) -> str:
    definition = REGISTER_BY_OFFSET.get(offset)
    if definition:
        return f"{definition.address} (offset {definition.offset})"
    return f"offset {offset}"


def generic_holding_label(offset: int) -> str:
    return f"{40001 + offset} | offset {offset}"
