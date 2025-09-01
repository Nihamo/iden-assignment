import json
import os
from typing import Dict, Any
from playwright.sync_api import BrowserContext, Page
from config import Config

class SessionManager:
    def _init_(self, context: BrowserContext):
        self.context = context
        self.session_file = Config.SESSION_FILE

    def save_session(self) -> None:
        """Save current sessionStorage and cookies to a file."""
        try:
            pages = self.context.pages
            if not pages:
                print("No pages found to save session data.")
                return

            page = pages[0]
            storage_str = page.evaluate("() => JSON.stringify(sessionStorage)")
            cookies = self.context.cookies()

            session_data = {
                "session_storage": json.loads(storage_str) if storage_str else {},
                "cookies": cookies
            }

            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(session_data, f, indent=2)

            print(" Session saved successfully.")
        except Exception as e:
            print(f" Error saving session: {e}")

    def load_session(self) -> bool:
        """Load sessionStorage and cookies from the session file."""
        if not os.path.exists(self.session_file):
            print(" Session file does not exist.")
            return False

        try:
            with open(self.session_file, "r", encoding="utf-8") as f:
                session_data = json.load(f)

            cookies = session_data.get("cookies", [])
            session_storage = session_data.get("session_storage", {})

            if cookies:
                self.context.add_cookies(cookies)

            def apply_session_storage(page: Page):
                for key, value in session_storage.items():
                    safe_key = key.replace("'", "\\'")
                    safe_value = value.replace("'", "\\'")
                    page.evaluate(f"sessionStorage.setItem('{safe_key}', '{safe_value}')")

            self.context.on("page", apply_session_storage)

            print(" Session loaded successfully.")
            return True

        except Exception as e:
            print(f" Error loading session: {e}")
            return False

    def session_exists(self) -> bool:
        """Check if the session file exists."""
        return os.path.isfile(self.session_file)

    def clear_session(self) -> None:
        """Delete the saved session file."""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
                print(" Session cleared.")
            else:
                print(" No session file to delete.")
        except Exception as e:
            print(f" Error clearing session: {e}")
