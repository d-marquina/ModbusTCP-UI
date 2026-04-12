from dataclasses import dataclass

import flet as ft


@dataclass
class TableViewControls:
    start_field: ft.TextField
    count_field: ft.TextField
    load_button: ft.FilledButton
    feedback_text: ft.Text
    rows_column: ft.Column
    content: ft.Container
    value_labels: dict[int, ft.Text]
    inputs: dict[int, ft.TextField]


def create_table_view(default_start: int, default_count: int) -> TableViewControls:
    return TableViewControls(
        start_field=ft.TextField(label="Offset inicial", value=str(default_start), width=140),
        count_field=ft.TextField(label="Cantidad", value=str(default_count), width=120),
        load_button=ft.FilledButton("Cargar", icon=ft.Icons.REFRESH),
        feedback_text=ft.Text(color=ft.Colors.AMBER),
        rows_column=ft.Column(spacing=10, scroll=ft.ScrollMode.ADAPTIVE, height=360),
        content=ft.Container(),
        value_labels={},
        inputs={},
    )


def render_table_tab(view: TableViewControls) -> None:
    view.content.content = ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("Tabla", size=18, weight="bold"),
                    ft.Text("Selecciona qué registros mostrar y escribe el nuevo valor presionando Enter."),
                    ft.ResponsiveRow(
                        controls=[
                            ft.Container(content=view.start_field, col={"xs": 12, "sm": 4, "md": 3}),
                            ft.Container(content=view.count_field, col={"xs": 12, "sm": 4, "md": 2}),
                            ft.Container(content=view.load_button, col={"xs": 12, "sm": 4, "md": 3}),
                        ]
                    ),
                    view.feedback_text,
                    view.rows_column,
                ],
                spacing=12,
            ),
        )
    )
