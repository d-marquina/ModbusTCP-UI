import asyncio

import flet as ft
from backends import AppMode, ClientBackend, ModbusBackend, ServerBackend
from models import REGISTER_DEFINITIONS, generic_holding_label, register_label
from ui import (
    build_bottom_tabs,
    build_connection_card,
    build_mode_tabs,
    create_dashboard_view,
    create_table_view,
    render_dashboard_tab,
    render_table_tab,
)


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 5020
DEFAULT_TABLE_START = 0
DEFAULT_TABLE_COUNT = 8
MAX_TABLE_COUNT = 16


def main(page: ft.Page):
    page.title = "Modbus TCP Control Center"
    page.window_width = 880
    page.window_height = 960
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.ADAPTIVE

    server_backend = ServerBackend(DEFAULT_HOST, DEFAULT_PORT)
    client_backend = ClientBackend(DEFAULT_HOST, DEFAULT_PORT)
    active_register_values: dict[int, int] = {definition.offset: 0 for definition in REGISTER_DEFINITIONS}
    is_internal_sync = False

    server_host = ft.TextField(label="Host local", value=DEFAULT_HOST, width=220)
    server_port = ft.TextField(label="Puerto", value=str(DEFAULT_PORT), width=140)
    client_host = ft.TextField(label="IP o host remoto", value=DEFAULT_HOST, width=220)
    client_port = ft.TextField(label="Puerto", value=str(DEFAULT_PORT), width=140)

    server_status = ft.Text()
    server_feedback = ft.Text(color=ft.Colors.AMBER)
    client_status = ft.Text()
    client_feedback = ft.Text(color=ft.Colors.AMBER)

    server_button = ft.FilledButton(width=210, color=ft.Colors.WHITE)
    client_button = ft.FilledButton(width=210, color=ft.Colors.WHITE)

    dashboard_view = create_dashboard_view()
    table_view = create_table_view(DEFAULT_TABLE_START, DEFAULT_TABLE_COUNT)

    top_server_content = ft.Container()
    top_client_content = ft.Container()
    bottom_table_content = table_view.content
    bottom_dashboard_content = dashboard_view.content

    top_tabs = build_mode_tabs(top_server_content, top_client_content)
    bottom_tabs = build_bottom_tabs(bottom_table_content, bottom_dashboard_content)

    def active_mode() -> AppMode:
        return AppMode.SERVER if top_tabs.selected_index == 0 else AppMode.CLIENT

    def active_backend() -> ModbusBackend:
        return server_backend if active_mode() == AppMode.SERVER else client_backend

    def mapping_offset(control: ft.Dropdown) -> int:
        return int(control.value or "0")

    def parse_endpoint(host_field: ft.TextField, port_field: ft.TextField, feedback: ft.Text) -> tuple[str, int] | None:
        host = (host_field.value or "").strip()
        if not host:
            feedback.value = "Ingresa un host valido"
            feedback.color = ft.Colors.RED
            page.update()
            return None
        try:
            port = int((port_field.value or "").strip())
        except ValueError:
            feedback.value = "El puerto debe ser numerico"
            feedback.color = ft.Colors.RED
            page.update()
            return None
        if port < 1 or port > 65535:
            feedback.value = "El puerto debe estar entre 1 y 65535"
            feedback.color = ft.Colors.RED
            page.update()
            return None
        return host, port

    def parse_table_range() -> tuple[int, int] | None:
        try:
            start = int((table_view.start_field.value or "").strip())
            count = int((table_view.count_field.value or "").strip())
        except ValueError:
            table_view.feedback_text.value = "Offset inicial y cantidad deben ser numericos"
            table_view.feedback_text.color = ft.Colors.RED
            page.update()
            return None
        if start < 0:
            table_view.feedback_text.value = "El offset inicial no puede ser negativo"
            table_view.feedback_text.color = ft.Colors.RED
            page.update()
            return None
        if count < 1 or count > MAX_TABLE_COUNT:
            table_view.feedback_text.value = f"La cantidad debe estar entre 1 y {MAX_TABLE_COUNT}"
            table_view.feedback_text.color = ft.Colors.RED
            page.update()
            return None
        return start, count

    def rebuild_server_backend(host: str, port: int) -> None:
        nonlocal server_backend
        server_backend.deactivate()
        server_backend = ServerBackend(host, port)

    def rebuild_client_backend(host: str, port: int) -> None:
        nonlocal client_backend
        client_backend.deactivate()
        client_backend = ClientBackend(host, port)

    def set_dashboard_feedback(message: str, color: str = ft.Colors.AMBER) -> None:
        dashboard_view.feedback_text.value = message
        dashboard_view.feedback_text.color = color

    def apply_led_state(value: int) -> None:
        if value == 1:
            dashboard_view.led_indicator.bgcolor = ft.Colors.YELLOW_ACCENT
            dashboard_view.led_icon.color = ft.Colors.BLACK
        else:
            dashboard_view.led_indicator.bgcolor = "#1a1a1a"
            dashboard_view.led_icon.color = ft.Colors.GREY

    def refresh_mapping_labels() -> None:
        slider_offset = mapping_offset(dashboard_view.slider_register)
        switch_offset = mapping_offset(dashboard_view.switch_register)
        led_offset = mapping_offset(dashboard_view.led_register)
        dashboard_view.speed_label.value = (
            f"Slider -> {register_label(slider_offset)}: {active_register_values.get(slider_offset, 0)}"
        )
        dashboard_view.pulse_switch.label = f"Switch -> {register_label(switch_offset)}"
        dashboard_view.led_target_label.value = f"LED monitorea {register_label(led_offset)}"

    def sync_dashboard_from_values() -> None:
        nonlocal is_internal_sync
        is_internal_sync = True
        try:
            for index, definition in enumerate(REGISTER_DEFINITIONS):
                dashboard_view.fixed_value_texts[index].value = str(active_register_values.get(definition.offset, 0))
            dashboard_view.speed_slider.value = active_register_values.get(mapping_offset(dashboard_view.slider_register), 0)
            dashboard_view.pulse_switch.value = active_register_values.get(mapping_offset(dashboard_view.switch_register), 0) == 1
            apply_led_state(active_register_values.get(mapping_offset(dashboard_view.led_register), 0))
            refresh_mapping_labels()
        finally:
            is_internal_sync = False

    def update_fixed_registers(values: list[int]) -> None:
        for definition, value in zip(REGISTER_DEFINITIONS, values):
            active_register_values[definition.offset] = value
        sync_dashboard_from_values()

    def reset_active_values() -> None:
        for definition in REGISTER_DEFINITIONS:
            active_register_values[definition.offset] = 0
        sync_dashboard_from_values()

    def refresh_enabled_state() -> None:
        enabled = active_backend().is_active()
        dashboard_view.speed_slider.disabled = not enabled
        dashboard_view.pulse_switch.disabled = not enabled
        table_view.load_button.disabled = not enabled
        if not enabled:
            set_dashboard_feedback("Activa la conexion de la pestaña superior para escribir registros", ft.Colors.AMBER)
        page.update()

    def refresh_table_values() -> None:
        backend = active_backend()
        if not backend.is_active():
            return
        table_range = parse_table_range()
        if not table_range:
            return
        start, count = table_range
        values = backend.read_holding_registers(start, count)
        if not values:
            table_view.feedback_text.value = "No se pudieron leer los registros de la tabla"
            table_view.feedback_text.color = ft.Colors.RED
            page.update()
            return
        for offset, value in enumerate(values, start=start):
            label = table_view.value_labels.get(offset)
            if label is not None:
                label.value = str(value)
            if offset in active_register_values:
                active_register_values[offset] = value
        sync_dashboard_from_values()

    def build_table_view() -> None:
        table_view.rows_column.controls.clear()
        table_view.value_labels.clear()
        table_view.inputs.clear()

        table_range = parse_table_range()
        if not table_range:
            return
        start, count = table_range

        for offset in range(start, start + count):
            current_value = ft.Text("-", width=90, color=ft.Colors.GREEN_ACCENT)
            new_value = ft.TextField(
                label="Nuevo valor",
                width=170,
                hint_text="Presiona Enter",
            )
            table_view.value_labels[offset] = current_value
            table_view.inputs[offset] = new_value

            def on_submit(e: ft.ControlEvent, target_offset: int = offset) -> None:
                backend = active_backend()
                if not backend.is_active():
                    table_view.feedback_text.value = "Activa la conexion de la pestaña superior primero"
                    table_view.feedback_text.color = ft.Colors.AMBER
                    page.update()
                    return
                try:
                    parsed_value = int((table_view.inputs[target_offset].value or "").strip())
                except ValueError:
                    table_view.feedback_text.value = f"Valor invalido para {generic_holding_label(target_offset)}"
                    table_view.feedback_text.color = ft.Colors.RED
                    page.update()
                    return
                if backend.write_holding_register(target_offset, parsed_value):
                    table_view.feedback_text.value = f"{generic_holding_label(target_offset)} escrito con {parsed_value}"
                    table_view.feedback_text.color = ft.Colors.GREEN
                    table_view.value_labels[target_offset].value = str(parsed_value)
                    active_register_values[target_offset] = parsed_value
                    sync_dashboard_from_values()
                else:
                    table_view.feedback_text.value = f"No se pudo escribir {generic_holding_label(target_offset)}"
                    table_view.feedback_text.color = ft.Colors.RED
                page.update()

            new_value.on_submit = on_submit

            table_view.rows_column.controls.append(
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(content=ft.Text(generic_holding_label(offset)), col={"xs": 12, "sm": 5, "md": 5}),
                        ft.Container(content=current_value, col={"xs": 12, "sm": 2, "md": 2}),
                        ft.Container(content=new_value, col={"xs": 12, "sm": 5, "md": 5}),
                    ]
                )
            )

    def render_top_connection_tabs() -> None:
        server_button.content = ft.Text(server_backend.action_label)
        server_button.icon = ft.Icons.STOP if server_backend.is_active() else ft.Icons.PLAY_ARROW
        server_button.bgcolor = ft.Colors.RED_700 if server_backend.is_active() else ft.Colors.BLUE_700
        server_status.value = server_backend.status_text
        server_status.color = server_backend.status_color

        client_button.content = ft.Text(client_backend.action_label)
        client_button.icon = ft.Icons.LINK_OFF if client_backend.is_active() else ft.Icons.LINK
        client_button.bgcolor = ft.Colors.GREY_700 if client_backend.is_active() else ft.Colors.GREEN_700
        client_status.value = client_backend.status_text
        client_status.color = client_backend.status_color

        top_server_content.content = build_connection_card(
            title="Modo servidor",
            description="Expone un servidor Modbus TCP local para que otros clientes se conecten.",
            host_field=server_host,
            port_field=server_port,
            action_button=server_button,
            status_text=server_status,
            feedback_text=server_feedback,
        )

        top_client_content.content = build_connection_card(
            title="Modo cliente",
            description="Se conecta a un servidor Modbus TCP externo usando la IP y puerto indicados.",
            host_field=client_host,
            port_field=client_port,
            action_button=client_button,
            status_text=client_status,
            feedback_text=client_feedback,
        )

        refresh_enabled_state()

    def render_bottom_tabs() -> None:
        render_table_tab(table_view)
        render_dashboard_tab(dashboard_view)

    def handle_server_toggle(e: ft.ControlEvent) -> None:
        endpoint = parse_endpoint(server_host, server_port, server_feedback)
        if not endpoint:
            return
        host, port = endpoint
        if host != server_backend.host or port != server_backend.port:
            rebuild_server_backend(host, port)
        success, message = server_backend.activate()
        server_feedback.value = message
        server_feedback.color = ft.Colors.GREEN if success else ft.Colors.RED
        if success and not server_backend.is_active():
            server_feedback.color = ft.Colors.AMBER
        if active_mode() == AppMode.SERVER and not server_backend.is_active():
            reset_active_values()
        render_top_connection_tabs()
        if active_mode() == AppMode.SERVER and server_backend.is_active():
            refresh_table_values()

    def handle_client_toggle(e: ft.ControlEvent) -> None:
        endpoint = parse_endpoint(client_host, client_port, client_feedback)
        if not endpoint:
            return
        host, port = endpoint
        if host != client_backend.host or port != client_backend.port:
            rebuild_client_backend(host, port)
        success, message = client_backend.activate()
        client_feedback.value = message
        client_feedback.color = ft.Colors.GREEN if success else ft.Colors.RED
        if success and not client_backend.is_active():
            client_feedback.color = ft.Colors.AMBER
        if active_mode() == AppMode.CLIENT and not client_backend.is_active():
            reset_active_values()
        render_top_connection_tabs()
        if active_mode() == AppMode.CLIENT and client_backend.is_active():
            refresh_table_values()

    def write_register(address: int, value: int) -> None:
        if is_internal_sync:
            return
        backend = active_backend()
        if not backend.is_active():
            set_dashboard_feedback("Activa la conexion de la pestaña superior primero", ft.Colors.AMBER)
            page.update()
            return
        if backend.write_holding_register(address, value):
            set_dashboard_feedback(f"Escritura correcta en {register_label(address)}", ft.Colors.GREEN)
            active_register_values[address] = value
            sync_dashboard_from_values()
            refresh_table_values()
        else:
            set_dashboard_feedback(f"No se pudo escribir {register_label(address)}", ft.Colors.RED)
        page.update()

    def handle_top_tab_change(e: ft.ControlEvent) -> None:
        render_top_connection_tabs()
        backend = active_backend()
        values = backend.read_holding_registers(0, len(REGISTER_DEFINITIONS)) if backend.is_active() else None
        if values and len(values) == len(REGISTER_DEFINITIONS):
            update_fixed_registers(values)
            set_dashboard_feedback("")
            refresh_table_values()
        else:
            reset_active_values()

    def handle_bottom_tab_change(e: ft.ControlEvent) -> None:
        render_bottom_tabs()
        page.update()

    def handle_slider_change(e: ft.ControlEvent) -> None:
        write_register(mapping_offset(dashboard_view.slider_register), int(e.control.value))

    def handle_switch_change(e: ft.ControlEvent) -> None:
        write_register(mapping_offset(dashboard_view.switch_register), 1 if e.control.value else 0)

    def handle_mapping_change(e: ft.ControlEvent) -> None:
        sync_dashboard_from_values()
        page.update()

    def handle_table_load(e: ft.ControlEvent) -> None:
        build_table_view()
        refresh_table_values()
        table_view.feedback_text.value = f"Rango cargado desde offset {table_view.start_field.value}"
        table_view.feedback_text.color = ft.Colors.GREEN
        page.update()

    server_button.on_click = handle_server_toggle
    client_button.on_click = handle_client_toggle
    top_tabs.on_change = handle_top_tab_change
    bottom_tabs.on_change = handle_bottom_tab_change
    dashboard_view.speed_slider.on_change = handle_slider_change
    dashboard_view.pulse_switch.on_change = handle_switch_change
    dashboard_view.slider_register.on_change = handle_mapping_change
    dashboard_view.switch_register.on_change = handle_mapping_change
    dashboard_view.led_register.on_change = handle_mapping_change
    table_view.load_button.on_click = handle_table_load

    page.add(
        ft.Column(
            controls=[
                ft.Text("Modbus TCP Control Center", size=28, weight="bold", color=ft.Colors.BLUE_200),
                ft.Text(
                    "Arriba eliges el modo Modbus. Abajo alternas entre vista tabular y dashboard.",
                    color=ft.Colors.GREY,
                ),
                top_tabs,
                bottom_tabs,
            ],
            spacing=18,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )
    )

    render_top_connection_tabs()
    build_table_view()
    render_bottom_tabs()
    reset_active_values()

    async def refresh_loop():
        while True:
            try:
                backend = active_backend()
                if backend.is_active():
                    values = backend.read_holding_registers(0, len(REGISTER_DEFINITIONS))
                    if values and len(values) == len(REGISTER_DEFINITIONS):
                        update_fixed_registers(values)
                        refresh_table_values()
                        if dashboard_view.feedback_text.value == "Activa la conexion de la pestaña superior para escribir registros":
                            set_dashboard_feedback("")
                        page.update()
                await asyncio.sleep(0.3)
            except Exception as exc:
                set_dashboard_feedback(f"Error de refresco: {exc}", ft.Colors.RED)
                page.update()
                await asyncio.sleep(1.0)

    page.run_task(refresh_loop)


if __name__ == "__main__":
    ft.run(main)
