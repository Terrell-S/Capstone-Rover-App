import flet as ft


def main(page: ft.Page):
    page.title = "Rover Dashboard"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START

    # Sample state for the current rover page
    rover_status = ft.Text("OK", size=20, weight=ft.FontWeight.BOLD)
    battery_level = ft.Text("88%", size=20, weight=ft.FontWeight.BOLD)
    location = ft.Text("Lat: 37.421, Lon: -122.084", size=14)
    last_contact = ft.Text("2025-11-03 10:12 UTC", size=12)

    # Small helper for info cards
    def data_card(title: str, widget: ft.Control):
        return ft.Card(
            elevation=4,
            content=ft.Container(
                padding=12,
                border_radius=10,
                content=ft.Column([
                    ft.Text(title, size=14, color=ft.Colors.GREY_600),
                    ft.Container(height=8),
                    widget,
                ])
            )
        )

    # Sample incidents for the logs page
    sample_incidents = [
        {"time": "2025-10-31 09:12", "summary": "Leak detected", "severity": "medium"},
        {"time": "2025-10-29 21:03", "summary": "Manual Search Engaged", "severity": "low"},
        {"time": "2025-10-20 14:22", "summary": "Temperature spike", "severity": "high"},
    ]

    # Views
    def view_main():
        return ft.View(
            "/",
            controls=[
                ft.AppBar(title=ft.Text("Rover Dashboard"), center_title=True),
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Current Rover Info", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(height=8),
                                ft.Text("View live status and telemetry", size=12),
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            margin=10,
                            padding=10,
                            alignment=ft.alignment.center,
                            bgcolor=ft.Colors.BLUE_50,
                            width=240,
                            height=140,
                            border_radius=10,
                            ink=True,
                            on_click=lambda e: page.go("/current"),
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Past Logged Incidents", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(height=8),
                                ft.Text("Browse historical incidents", size=12),
                            ], alignment=ft.MainAxisAlignment.CENTER),
                            margin=10,
                            padding=10,
                            alignment=ft.alignment.center,
                            bgcolor=ft.Colors.GREEN_50,
                            width=240,
                            height=140,
                            border_radius=10,
                            ink=True,
                            on_click=lambda e: page.go("/logs"),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
        )

    def view_current():
        return ft.View(
            "/current",
            controls=[
                ft.AppBar(
                    title=ft.Text("Current Rover Info"),
                    center_title=True,
                    # Avoid using ft.icons for maximum compatibility across flet versions
                    leading=ft.TextButton("Back", on_click=lambda e: page.go("/")),
                ),
                ft.Container(
                    padding=20,
                    expand=True,
                    content=ft.Column([
                        data_card("Connection Status", rover_status),
                        ft.Row([
                            data_card("Battery", battery_level),
                            ft.Container(width=12),
                            data_card("Last Contact", last_contact),
                        ], alignment=ft.MainAxisAlignment.START),
                        data_card("Location", location),
                        ft.Container(height=12),
                        ft.ElevatedButton("Refresh", on_click=lambda e: page.update()),
                    ], spacing=12),
                ),
            ],
        )

    def view_logs():
        # build a list of incident cards
        incident_cards = []
        for inc in sample_incidents:
            incident_cards.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Column([
                            ft.Text(inc["time"], size=12, color=ft.Colors.GREY_600),
                            ft.Text(inc["summary"], size=14, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Severity: {inc['severity']}", size=12),
                        ])
                    )
                )
            )

        return ft.View(
            "/logs",
            controls=[
                ft.AppBar(
                    title=ft.Text("Logged Incidents"),
                    center_title=True,
                    # Use a text button instead of icon to avoid AttributeError on some flet installs
                    leading=ft.TextButton("Back", on_click=lambda e: page.go("/")),
                ),
                ft.Container(
                    padding=20,
                    expand=True,
                    content=ft.Column([
                        ft.Text("Incident History", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(height=12),
                        ft.Column(incident_cards, spacing=8),
                    ]),
                ),
            ],
        )

    # route change handler
    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(view_main())
        elif page.route == "/current":
            page.views.append(view_current())
        elif page.route == "/logs":
            page.views.append(view_logs())
        else:
            page.views.append(view_main())
        page.update()

    page.on_route_change = route_change
    # initialize
    page.go(page.route or "/")


if __name__ == "__main__":
    ft.app(target=main)