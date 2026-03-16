"""
Run this script daily to refresh your Kite access token.
It will open the login page in your browser, then update .env automatically.

Usage:
    python scripts/get_token.py
"""

import os
import re
import webbrowser
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(ENV_PATH)


def update_env(key: str, value: str):
    """Replace a key's value in the .env file."""
    content = ENV_PATH.read_text()
    pattern = rf"^{key}=.*$"
    new_line = f"{key}={value}"
    if re.search(pattern, content, flags=re.MULTILINE):
        content = re.sub(pattern, new_line, content, flags=re.MULTILINE)
    else:
        content += f"\n{new_line}"
    ENV_PATH.write_text(content)


def main():
    api_key = os.getenv("KITE_API_KEY")
    api_secret = os.getenv("KITE_API_SECRET")

    if not api_key or not api_secret:
        print("ERROR: KITE_API_KEY and KITE_API_SECRET must be set in .env")
        return

    login_url = f"https://kite.trade/connect/login?api_key={api_key}&v=3"

    print("\n=== Kite Access Token Generator ===\n")
    print(f"Opening login page in your browser...")
    webbrowser.open(login_url)

    print("\nAfter logging in, you will be redirected to a URL like:")
    print("  https://yourapp.com/?request_token=XXXXXXXX&status=success")
    print("\nCopy the 'request_token' value from that URL.\n")

    request_token = input("Paste your request_token here: ").strip()

    try:
        from kiteconnect import KiteConnect
    except ImportError:
        print("ERROR: Run 'pip install kiteconnect' first.")
        return

    try:
        kite = KiteConnect(api_key=api_key)
        session = kite.generate_session(request_token, api_secret=api_secret)
        access_token = session["access_token"]

        update_env("KITE_ACCESS_TOKEN", access_token)

        print(f"\nSuccess! Access token saved to .env")
        print(f"KITE_ACCESS_TOKEN={access_token}")
    except Exception as e:
        print(f"\nERROR: Failed to generate token — {e}")


if __name__ == "__main__":
    main()
