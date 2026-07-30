"""
Desktop launcher for the HDM Cattle Management & Inventory System.

Bundled into a Windows executable with PyInstaller (see build_windows.spec).
It runs as a proper installed program — NOT a browser:

  * The Streamlit server runs as a hidden background process.
  * The app is shown in a NATIVE application window (pywebview, using the WebView2
    engine that ships with Windows 10/11) — no browser, no address bar, no tabs.
  * Closing the window quits the whole program (the background server is stopped).
  * If the native window layer is unavailable on a machine, it automatically falls
    back to a standalone Edge/Chrome "app" window, then to the default browser, so
    the app always opens.

The database lives in the user's local app-data folder so it survives updates.
No Python installation is required on the target computer.
"""
import os
import sys
import time
import socket
import shutil
import subprocess
import webbrowser
from pathlib import Path

APP_TITLE = "HDM Cattle Management"


def _resource(rel: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def _free_port(start: int = 8501, tries: int = 50) -> int:
    for port in range(start, start + tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return start


def _skip_first_run_prompt() -> None:
    try:
        cred = Path.home() / ".streamlit" / "credentials.toml"
        if not cred.exists():
            cred.parent.mkdir(parents=True, exist_ok=True)
            cred.write_text('[general]\nemail = ""\n', encoding="utf-8")
    except Exception:
        pass


def _wait_for_server(port: int, timeout: float = 60.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.4)
    return False


# ── The background server process ────────────────────────────────────────────
def _run_server() -> None:
    """Runs in the CHILD process: start the Streamlit server (blocking)."""
    port = int(os.environ.get("CATTLE_PORT", "8501"))
    os.environ["CATTLE_DESKTOP"] = "1"
    os.environ["STREAMLIT_SERVER_PORT"] = str(port)
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "localhost"
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
    os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
    os.environ["STREAMLIT_SERVER_TOOLBAR_MODE"] = "minimal"
    os.environ["STREAMLIT_SERVER_MAX_UPLOAD_SIZE"] = "500"
    os.environ["STREAMLIT_THEME_BASE"] = "light"

    script = _resource("cattlemanagementapp.py")
    sys.argv = [
        "streamlit", "run", script,
        "--server.port", str(port),
        "--server.address", "localhost",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false",
        "--global.developmentMode", "false",
    ]
    from streamlit.web import cli as stcli
    sys.exit(stcli.main())


def _spawn_server(port: int) -> subprocess.Popen:
    """Launch this same program again as a hidden server process."""
    env = os.environ.copy()
    env["CATTLE_SERVER"] = "1"
    env["CATTLE_PORT"] = str(port)
    if getattr(sys, "frozen", False):
        cmd = [sys.executable]                       # re-run the packaged .exe
    else:
        cmd = [sys.executable, os.path.abspath(__file__)]   # dev: re-run this script
    flags = 0x08000000 if os.name == "nt" else 0     # CREATE_NO_WINDOW
    return subprocess.Popen(cmd, env=env, creationflags=flags)


# ── The window (native first, then fall-backs) ───────────────────────────────
def _show_native_window(url: str) -> bool:
    """Open a real native application window. Returns True if it ran (and has since
    been closed), False if the native layer is unavailable."""
    try:
        import webview
    except Exception:
        return False
    # Enable file downloads so the Save As dialog appears when the user clicks a
    # download button (PDF invoices, backups, CSVs). Supported on pywebview 5.x;
    # ignored safely on versions that predate the setting.
    try:
        webview.settings["ALLOW_DOWNLOADS"] = True
    except Exception:
        pass
    try:
        try:
            webview.create_window(APP_TITLE, url, width=1360, height=880,
                                  min_size=(960, 640))
        except TypeError:
            webview.create_window(APP_TITLE, url, width=1360, height=880)
        webview.start(private_mode=False)
        return True
    except TypeError:
        try:
            webview.start()
            return True
        except Exception:
            return False
    except Exception:
        return False


def _find_chromium() -> str:
    pf = os.environ.get("PROGRAMFILES", r"C:\Program Files")
    pfx86 = os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")
    local = os.environ.get("LOCALAPPDATA", "")
    for path in (
        os.path.join(pfx86, r"Microsoft\Edge\Application\msedge.exe"),
        os.path.join(pf, r"Microsoft\Edge\Application\msedge.exe"),
        os.path.join(pf, r"Google\Chrome\Application\chrome.exe"),
        os.path.join(pfx86, r"Google\Chrome\Application\chrome.exe"),
        os.path.join(local, r"Google\Chrome\Application\chrome.exe"),
    ):
        if path and os.path.exists(path):
            return path
    for name in ("msedge", "chrome", "chromium"):
        found = shutil.which(name)
        if found:
            return found
    return ""


def _show_app_window(url: str) -> bool:
    """Fall-back: a standalone chrome-less Edge/Chrome window; blocks until closed."""
    browser = _find_chromium()
    if not browser:
        return False
    profile = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "HDM Cattle Management" / "window"
    profile.mkdir(parents=True, exist_ok=True)
    try:
        proc = subprocess.Popen([
            browser, f"--app={url}", f"--user-data-dir={profile}",
            "--no-first-run", "--no-default-browser-check", "--window-size=1360,880",
        ])
    except Exception:
        return False
    proc.wait()
    return True


# ── Entry point ──────────────────────────────────────────────────────────────
def main() -> None:
    # Child process: just run the server.
    if os.environ.get("CATTLE_SERVER") == "1":
        _run_server()
        return

    # Parent process: set up data location, start the server, show the window.
    appdata = os.environ.get("LOCALAPPDATA") or str(Path.home())
    db_dir = Path(appdata) / "HDM Cattle Management"
    db_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("CATTLE_DB_PATH", str(db_dir / "cattle.db"))

    _skip_first_run_prompt()

    port = _free_port(8501)
    url = f"http://localhost:{port}"
    server = _spawn_server(port)
    _wait_for_server(port, timeout=60.0)

    try:
        if _show_native_window(url):
            pass                       # native window opened and was closed
        elif _show_app_window(url):
            pass                       # standalone app window closed
        else:
            webbrowser.open(url)       # last resort: default browser
            server.wait()
    finally:
        try:
            server.terminate()
        except Exception:
            pass
        os._exit(0)


if __name__ == "__main__":
    main()
