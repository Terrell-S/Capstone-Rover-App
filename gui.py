import os, time, threading, mapping, json
import flet as ft
import networking as nt
from datetime import datetime
from typing import Dict
try:
    # when package-importing (if the project is installed as a package)
    from . import auth as firebase_auth  # type: ignore
except Exception:
    # when running as a script, use top-level import
    import auth as firebase_auth

lock = threading.Lock()
def update_handler(channel: nt.WiFiChannel, page: ft.Page, values: dict, log: ft.Column, refresh: int=2, controls: dict=None):
    '''
    python is not pass by reference for some reason
    so need to use list, dict, etc 

    periodically requests update from rover
    thread function so it doesn't block GUI
    '''
    update_rqst = nt.Request('update')
    backoff = 1.0
    while True:
        try:
            if not channel.has_client:
                # No client connected — show listening / disconnected state
                with lock:
                    values['connection_status'] = 'Listening'
                    values['mode_status'] = values.get('mode_status', '~')
                    values['battery_level'] = values.get('battery_level', '~')
                    values['last_contact'] = values.get('last_contact', 'check log')
                    if controls:
                        controls['connection_status'].value = values['connection_status']
                        controls['mode_status'].value = values['mode_status']
                        controls['battery_level'].value = values['battery_level']
                        controls['last_contact'].value = values['last_contact']
                page.update()
                # lightweight backoff before checking again
                time.sleep(backoff)
                continue

            # We have a client — attempt to exchange update messages
            with lock:
                values['connection_status'] = 'Connected'
                if controls and 'connection_status' in controls:
                    controls['connection_status'].value = 'Connected'
                page.update()

            try:
                channel.send_message(update_rqst)
                msg = channel.recieve_message()
            except Exception as net_exc:
                # networking layer signaled a problem (e.g. client disconnected)
                with lock:
                    values['connection_status'] = 'No connection'
                    if controls and 'connection_status' in controls:
                        controls['connection_status'].value = values['connection_status']
                page.update()
                # small sleep to allow `WiFiChannel` accept loop to recover
                time.sleep(1.0)
                continue

            # Successful receive -> update UI state
            with lock:
                values['mode_status'] = getattr(msg, 'mode', values.get('mode_status', '~'))
                values['battery_level'] = getattr(msg, 'battery', values.get('battery_level', '~'))
                values['last_contact'] = datetime.now().strftime("%Y-%m-%d %H:%M")

                if controls:
                    if 'mode_status' in controls:
                        controls['mode_status'].value = values['mode_status']
                    if 'battery_level' in controls:
                        controls['battery_level'].value = values['battery_level']
                    if 'last_contact' in controls:
                        controls['last_contact'].value = values['last_contact']

                # handle message types as before (alert/log)
                if getattr(msg, 'type', None) == 'alert':
                    time_log = datetime.now().strftime("%Y-%m-%d %H:%M")
                    indicent_type = 'Leak Detected'
                    summary = "Rover has detected an alert condition."
                    new_card = ft.Card(content=ft.Container(padding=12, content=ft.Column([
                        ft.Text(time_log, size=16, color=ft.Colors.GREY_600),
                        ft.Text(indicent_type, size=22, weight=ft.FontWeight.BOLD),
                        ft.Text(summary, size=16),
                    ])))
                    log.controls.insert(0, new_card)

                elif getattr(msg, 'type', None) == 'log':
                    now = datetime.now()
                    time_log = now.strftime("%Y-%m-%d %H:%M")
                    time_safe = now.strftime("%Y-%m-%d-%H_%M")
                    indicent_type = 'Leak Report'
                    summary = f"TTD: {msg.data.get('TTD', 'N/A')}s, DTS: {msg.data.get('DTS', 'N/A')}m"
                    motor_data = json.loads(msg.data.get('motor_data','[]'))
                    map_filename = f"leak_map_{time_safe}.png" #change later to be in log folder
                    mapping.make_map(motor_data, map_filename)
                    new_card = ft.Card(content=ft.Container(padding=12, content=ft.Column([
                        ft.Text(time_log, size=16, color=ft.Colors.GREY_600),
                        ft.Text(indicent_type, size=22, weight=ft.FontWeight.BOLD),
                        ft.Text(summary, size=16),
                        ft.Image(src=map_filename, width=500),
                    ])))
                    log.controls.insert(0, new_card)

            # normal refresh interval
            time.sleep(refresh)

        except Exception as exc:
            # Catch-all to avoid thread dying; surface status and continue
            with lock:
                values['connection_status'] = 'Error'
                if controls and 'connection_status' in controls:
                    controls['connection_status'].value = 'Error'
            print("update_handler unexpected error:", repr(exc))
            page.update()
            time.sleep(1.0)

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
    update_channel = nt.WiFiChannel(5000)
    
    # control object initialization
    connection_status = ft.Text(updates['connection_status'], size=20, weight=ft.FontWeight.BOLD)
    mode_status = ft.Text(updates['mode_status'], size=20, weight=ft.FontWeight.BOLD)
    battery_level = ft.Text(updates['battery_level'], size=20, weight=ft.FontWeight.BOLD)
    last_contact = ft.Text(updates['last_contact'], size=12)

    controls = {
        'connection_status': connection_status,
        'mode_status': mode_status,
        'battery_level': battery_level,
        'last_contact': last_contact,
    }

    #flutter object to have changable list
    #holds card object for each incident
    incident_list_column = ft.Column([], spacing=8)

    #flutter built in thread handler
    page.run_thread(update_handler, update_channel, page, updates, incident_list_column, 2, controls)


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
        time_log = datetime.now().strftime("%Y-%m-%d %H:%M")
        indicent_type = 'User Logout'
        summary = f"User {state['user_email']} signed out."
        new_card = ft.Card(content=ft.Container(padding=12, content=ft.Column([
                ft.Text(time_log, size=16, color=ft.Colors.GREY_600),
                ft.Text(indicent_type, size=22, weight=ft.FontWeight.BOLD),
                ft.Text(summary, size=16),
            ])))
        incident_list_column.controls.insert(0, new_card)
 
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
                                ft.Text("Current Rover Info", size=24, weight=ft.FontWeight.BOLD),
                                ft.Container(height=8),
                                ft.Text("View live status and robot control", size=20),
                            ], alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            margin=10,
                            padding=10,
                            alignment=ft.alignment.center,
                            bgcolor=ft.Colors.BLUE_50,
                            width=440,
                            height=340,
                            border_radius=10,
                            ink=True,
                            on_click=lambda e: page.go("/current"),
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Event Log", size=24, weight=ft.FontWeight.BOLD),
                                ft.Container(height=8),
                                ft.Text("Browse reports and system event information", size=20),
                            ], alignment=ft.MainAxisAlignment.CENTER,horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            margin=10,
                            padding=10,
                            alignment=ft.alignment.center,
                            bgcolor=ft.Colors.GREEN_50,
                            width=440,
                            height=340,
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
        return ft.View(
            "/logs",
            controls=[
                app_bar("Logged Events", leading=ft.TextButton("Back", on_click=lambda e: page.go("/"))),
                ft.Container(
                    padding=20,
                    expand=True,
                    content=ft.Column([
                        ft.Text("Event History", size=18, weight=ft.FontWeight.BOLD),
                        ft.Container(height=12),
                        incident_list_column,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
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

        def _friendly_error_message(exc: Exception) -> str:
            """Turn auth exceptions into user-friendly messages.

            The `auth` helpers raise `RuntimeError` with strings like
            "Firebase error: EMAIL_NOT_FOUND" or
            "Firebase error: WEAK_PASSWORD : Password should be at least 6 characters".
            Map common codes to clearer text for users and fall back to a generic
            explanation for network/other errors.
            """
            msg = str(exc or "")
            # explicit missing key
            if "Missing Firebase API key" in msg:
                return "Internal configuration error: missing Firebase API key."
            # firebase REST errors are prefixed
            if msg.startswith("Firebase error:"):
                raw = msg.split(":", 1)[1].strip()
                # common Firebase error codes -> friendly messages
                mapping = {
                    "INVALID_LOGIN_CREDENTIALS": "Invalid email or password.",
                    "EMAIL_NOT_FOUND": "No account found with that email.",
                    "INVALID_PASSWORD": "Incorrect password. Please try again.",
                    "USER_DISABLED": "This account has been disabled.",
                    "EMAIL_EXISTS": "An account with that email already exists.",
                    "WEAK_PASSWORD": "Password is too weak. Use at least 6 characters.",
                    "OPERATION_NOT_ALLOWED": "This operation is not allowed.",
                    "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Try again later.",
                }
                # If the raw value contains a known code, return mapping
                for code, friendly in mapping.items():
                    if code in raw:
                        return friendly
                # If there's a colon-separated detail, attempt to show it nicely
                if ":" in raw:
                    code, detail = [p.strip() for p in raw.split(":", 1)]
                    return f"{code}: {detail}"
                # fallback: return the raw message
                return raw
            if msg.startswith("Network error:"):
                return "Network error: could not reach authentication service. Check your connection."
            # final fallback: return the original text
            return msg

        def on_sign_in(e):
            key = api_key_field.value.strip()
            email_val = email.value.strip()
            pw_val = password.value
            if not (key and email_val and pw_val):
                set_message("Please provide email and password.")
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

                #current login tracking in log
                time_log = datetime.now().strftime("%Y-%m-%d %H:%M")
                indicent_type = 'User Login'
                summary = f"User {state['user_email']} signed in."
                new_card = ft.Card(content=ft.Container(padding=12, content=ft.Column([
                        ft.Text(time_log, size=16, color=ft.Colors.GREY_600),
                        ft.Text(indicent_type, size=22, weight=ft.FontWeight.BOLD),
                        ft.Text(summary, size=16),
                    ])))
                incident_list_column.controls.insert(0, new_card)
                page.update()
                page.go("/")
            except Exception as exc:
                set_message(_friendly_error_message(exc))

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
                set_message(_friendly_error_message(exc))

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