from dataclasses import dataclass

import flet as ft

from models import REGISTER_DEFINITIONS, register_option


@dataclass
class DashboardViewControls:
    slider_register: ft.Dropdown
    switch_register: ft.Dropdown
    led_register: ft.Dropdown
    speed_label: ft.Text
    speed_slider: ft.Slider
    pulse_switch: ft.Switch
    led_target_label: ft.Text
    led_icon: ft.Icon
    led_indicator: ft.Container
    feedback_text: ft.Text
    fixed_value_texts: list[ft.Text]
    content: ft.Container


def create_dashboard_view() -> DashboardViewControls:
    slider_register = ft.Dropdown(
        label="Registro del slider",
        value="1",
        options=[register_option(definition) for definition in REGISTER_DEFINITIONS],
        width=280,
    )
    switch_register = ft.Dropdown(
        label="Registro del switch",
        value="3",
        options=[register_option(definition) for definition in REGISTER_DEFINITIONS],
        width=280,
    )
    led_register = ft.Dropdown(
        label="Registro del LED",
        value="2",
        options=[register_option(definition) for definition in REGISTER_DEFINITIONS],
        width=280,
    )
    led_icon = ft.Icon(ft.Icons.LIGHT_MODE, size=30, color=ft.Colors.GREY)
    return DashboardViewControls(
        slider_register=slider_register,
        switch_register=switch_register,
        led_register=led_register,
        speed_label=ft.Text(weight="bold"),
        speed_slider=ft.Slider(min=0, max=100, divisions=100, value=0, expand=True),
        pulse_switch=ft.Switch(),
        led_target_label=ft.Text(),
        led_icon=led_icon,
        led_indicator=ft.Container(
            width=48,
            height=48,
            border_radius=24,
            bgcolor="#1a1a1a",
            border=ft.Border.all(2, ft.Colors.GREY),
            content=led_icon,
            alignment=ft.Alignment(0, 0),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        ),
        feedback_text=ft.Text(color=ft.Colors.AMBER),
        fixed_value_texts=[ft.Text("0", weight="bold", color=ft.Colors.GREEN_ACCENT) for _ in REGISTER_DEFINITIONS],
        content=ft.Container(),
    )


def build_fixed_register_table(value_texts: list[ft.Text]) -> ft.DataTable:
    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Registro")),
            ft.DataColumn(ft.Text("Offset")),
            ft.DataColumn(ft.Text("Descripcion")),
            ft.DataColumn(ft.Text("Valor")),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(definition.address)),
                    ft.DataCell(ft.Text(str(definition.offset))),
                    ft.DataCell(ft.Text(definition.description)),
                    ft.DataCell(value_texts[index]),
                ]
            )
            for index, definition in enumerate(REGISTER_DEFINITIONS)
        ],
    )


def render_dashboard_tab(view: DashboardViewControls) -> None:
    fixed_register_table = build_fixed_register_table(view.fixed_value_texts)
    view.content.content = ft.Column(
        controls=[
            ft.Card(
                content=ft.Container(
                    padding=20,
                    content=ft.Column(
                        controls=[
                            ft.Text("Mapeo de controles", size=18, weight="bold"),
                            ft.ResponsiveRow(
                                controls=[
                                    ft.Container(content=view.slider_register, col={"xs": 12, "md": 4}),
                                    ft.Container(content=view.switch_register, col={"xs": 12, "md": 4}),
                                    ft.Container(content=view.led_register, col={"xs": 12, "md": 4}),
                                ]
                            ),
                        ],
                        spacing=12,
                    ),
                )
            ),
            ft.Card(
                content=ft.Container(
                    padding=20,
                    content=ft.Column(
                        controls=[
                            ft.Text("Dashboard", size=18, weight="bold"),
                            view.pulse_switch,
                            view.speed_label,
                            view.speed_slider,
                            ft.Row(
                                controls=[view.led_indicator, view.led_target_label],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            view.feedback_text,
                        ],
                        spacing=16,
                    ),
                )
            ),
            ft.Card(
                content=ft.Container(
                    padding=20,
                    content=ft.Column(
                        controls=[
                            ft.Text("Mapa base de registros", size=18, weight="bold"),
                            fixed_register_table,
                        ],
                        spacing=12,
                    ),
                )
            ),
        ],
        spacing=18,
        scroll=ft.ScrollMode.ADAPTIVE,
    )
