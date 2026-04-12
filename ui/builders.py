import flet as ft


def build_mode_tabs(server_content: ft.Control, client_content: ft.Control) -> ft.Tabs:
    return ft.Tabs(
        content=ft.Column(
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Servidor", icon=ft.Icons.DNS),
                        ft.Tab(label="Cliente", icon=ft.Icons.LINK),
                    ],
                    scrollable=False,
                    indicator_color=ft.Colors.BLUE_300,
                    label_color=ft.Colors.BLUE_200,
                    unselected_label_color=ft.Colors.GREY,
                ),
                ft.Container(
                    height=280,
                    content=ft.TabBarView(
                        controls=[server_content, client_content],
                    ),
                ),
            ],
            tight=True,
        ),
        length=2,
        selected_index=0,
    )


def build_bottom_tabs(table_content: ft.Control, dashboard_content: ft.Control) -> ft.Tabs:
    return ft.Tabs(
        content=ft.Column(
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Tabla", icon=ft.Icons.TABLE_ROWS),
                        ft.Tab(label="Dashboard", icon=ft.Icons.SPACE_DASHBOARD),
                    ],
                    scrollable=False,
                    indicator_color=ft.Colors.GREEN_300,
                    label_color=ft.Colors.GREEN_200,
                    unselected_label_color=ft.Colors.GREY,
                ),
                ft.Container(
                    height=640,
                    content=ft.TabBarView(
                        controls=[table_content, dashboard_content],
                    ),
                ),
            ],
            tight=True,
        ),
        length=2,
        selected_index=0,
    )


def build_connection_card(
    title: str,
    description: str,
    host_field: ft.Control,
    port_field: ft.Control,
    action_button: ft.Control,
    status_text: ft.Control,
    feedback_text: ft.Control,
) -> ft.Card:
    return ft.Card(
        content=ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text(title, size=18, weight="bold"),
                    ft.Text(description),
                    ft.ResponsiveRow(
                        controls=[
                            ft.Container(content=host_field, col={"xs": 12, "sm": 12, "md": 5}),
                            ft.Container(content=port_field, col={"xs": 12, "sm": 6, "md": 3}),
                            ft.Container(content=action_button, col={"xs": 12, "sm": 6, "md": 4}),
                        ]
                    ),
                    status_text,
                    feedback_text,
                ],
                spacing=12,
            ),
        )
    )
