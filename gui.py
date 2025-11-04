import os
import flet as ft
import networking as nt
import time 
from datetime import datetime
from typing import Dict

# import auth module with a plain import so running `python gui.py` works
try:
    # when package-importing (if the project is installed as a package)
    from . import auth as firebase_auth  # type: ignore
except Exception:
    # when running as a script, use top-level import
    import auth as firebase_auth

def update_handler(channel: nt.WiFiChannel, values: dict, log: list, refresh: int=2):
    '''
    python is not pass by reference for some reason
    so need to use list, dict, etc 
    
    periodically requests update from rover
    thread function so it doesn't bloack GUI
    '''
    update_rqst = nt.Request('update')
    while True:
        if channel.has_client:
            channel.send_message(update_rqst)
            msg = channel.recieve_message() #response type
            values['connection_status'] = 'Connected'
            values['mode_status'] = msg.mode
            values['battery_level'] = msg.battery
            values['last_contact'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        time.sleep(refresh)

def main(page: ft.Page):
    page.title = "Rover Dashboard"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START

    '''
    Data is changed here by threads, and is only read by gui containers
    '''
    updates = {
        "connection_status": "No connection",
        "mode_status": "~",
        "battery_level": "~",
        "last_contact": "check log",
    }
    update_channel = nt.WiFiChannel(9000)
    # Sample state for the current rover page
    connection_status = ft.Text(updates['connection_status'], size=20, weight=ft.FontWeight.BOLD)
    mode_status = ft.Text(updates['mode_status'], size=20, weight=ft.FontWeight.BOLD)
    battery_level = ft.Text(updates['bettery_level'], size=20, weight=ft.FontWeight.BOLD)
    last_contact = ft.Text(updates['last_contact'], size=12)

    # Sample incidents for the logs page
    sample_incidents = [
        {"time": "2025-10-31 09:12", "summary": "Leak detected", "severity": "medium"},
        {"time": "2025-10-29 21:03", "summary": "Manual Search Engaged", "severity": "low"},
        {"time": "2025-10-20 14:22", "summary": "Temperature spike", "severity": "high"},
    ]

    # small state container so closures can mutate
    state: Dict[str, object] = {
        "is_authenticated": False,
        "id_token": None,
        "api_key": "AIzaSyDpOuS0q81RadjUZp9JNILVcOJJzdynv_Q",
        #"api_key": os.getenv("FIREBASE_API_KEY", ""),
        "user_email": None,
    }

    # logout helper (clears in-memory auth state)
    def on_logout(e=None):
        state["is_authenticated"] = False
        state["id_token"] = None
        state["user_email"] = None
        # send user back to login
        page.go("/login")
        page.update()

    # AppBar factory that shows the signed-in user's email on the right
    def app_bar(title_text: str, leading=None):
        actions = []
        if state.get("is_authenticated"):
            email = state.get("user_email") or ""
            # show email and a small logout button
            actions.append(ft.Text(email, size=12))
            actions.append(ft.Container(width=12))
            actions.append(ft.TextButton("Logout", on_click=on_logout))
        return ft.AppBar(title=ft.Text(title_text), center_title=True, leading=leading, actions=actions)

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


    # Views
    def view_main():
        return ft.View(
            "/",
            controls=[
                app_bar("Rover Dashboard"),
                ft.Container(height=20),
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Current Rover Info", size=16, weight=ft.FontWeight.BOLD),
                                ft.Container(height=8),
                                ft.Text("View live status and robot control", size=12),
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
                app_bar("Current Rover Info", leading=ft.TextButton("Back", on_click=lambda e: page.go("/"))),
                ft.Container(
                    padding=20,
                    expand=True,
                    content=ft.Column([
                        data_card("Connection Status", connection_status),
                        data_card("Current Mode", mode_status),
                        ft.Row([
                            data_card("Battery", battery_level),
                            ft.Container(width=12),
                            data_card("Last Contact", last_contact),
                        ], alignment=ft.MainAxisAlignment.START),
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
                app_bar("Logged Incidents", leading=ft.TextButton("Back", on_click=lambda e: page.go("/"))),
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

    # Login view
    def view_login():
        email = ft.TextField(label="Email", width=360)
        password = ft.TextField(label="Password", password=True, can_reveal_password=True, width=360)
        api_key_field = ft.TextField(label="Firebase API Key (or set FIREBASE_API_KEY env var)", value=state["api_key"], width=560)
        message = ft.Text("", color=ft.Colors.RED)

        def set_message(msg: str, color=ft.Colors.RED):
            message.value = msg
            message.color = color
            page.update()

        def on_sign_in(e):
            key = api_key_field.value.strip()
            email_val = email.value.strip()
            pw_val = password.value
            if not (key and email_val and pw_val):
                set_message("Please provide API key, email and password.")
                return
            try:
                resp = firebase_auth.sign_in_with_email_and_password(key, email_val, pw_val)
                # store token in state
                state["is_authenticated"] = True
                state["id_token"] = resp.get("idToken")
                # store the signed-in user's email for display
                state["user_email"] = resp.get("email", email_val)
                state["api_key"] = key
                set_message("Signed in successfully.", color=ft.Colors.GREEN)
                page.go("/")
            except Exception as exc:
                set_message(str(exc))

        def on_sign_up(e):
            key = api_key_field.value.strip()
            email_val = email.value.strip()
            pw_val = password.value
            if not (key and email_val and pw_val):
                set_message("Please provide API key, email and password.")
                return
            try:
                resp = firebase_auth.sign_up_with_email_and_password(key, email_val, pw_val)
                state["is_authenticated"] = True
                state["id_token"] = resp.get("idToken")
                # store the created user's email for display
                state["user_email"] = resp.get("email", email_val)
                state["api_key"] = key
                set_message("Account created and signed in.", color=ft.Colors.GREEN)
                page.go("/")
            except Exception as exc:
                set_message(str(exc))

        return ft.View(
            "/login",
            controls=[
                ft.AppBar(title=ft.Text("Sign in"), center_title=True),
                ft.Container(
                    padding=20,
                    expand=True,
                    content=ft.Column([
                        ft.Text("Please sign in to access the Rover Dashboard", size=14),
                        ft.Container(height=12),
                        #api_key_field,
                        email,
                        password,
                        ft.Row([
                            ft.ElevatedButton("Sign in", on_click=on_sign_in),
                            ft.ElevatedButton("Sign up", on_click=on_sign_up),
                        ], spacing=12),
                        ft.Container(height=8),
                        message,
                    ], spacing=8),
                ),
            ],
        )

    # route change handler
    def route_change(route):
        page.views.clear()
        # if not authenticated, force login view
        if not state.get("is_authenticated", False) and page.route != "/login":
            page.views.append(view_login())
            page.go("/login")
            page.update()
            return

        if page.route == "/":
            page.views.append(view_main())
        elif page.route == "/current":
            page.views.append(view_current())
        elif page.route == "/logs":
            page.views.append(view_logs())
        elif page.route == "/login":
            page.views.append(view_login())
        else:
            page.views.append(view_main())
        page.update()

    page.on_route_change = route_change
    # initialize
    # if FIREBASE_API_KEY env var is present, prefill the field; otherwise user will enter it
    page.go(page.route or ("/login" if not state["is_authenticated"] else "/"))


if __name__ == "__main__":
    ft.app(target=main)