# HDM Cattle Management — Windows Software

This packages the app as a normal Windows program. The person using it does **not**
need Python or Streamlit installed. It runs as a real desktop program: the app
appears in its **own native window** (no browser, no address bar, no tabs), and
there is **no Deploy button or Streamlit menu**. Closing the window quits the program.

## Files

| File | Purpose |
|------|---------|
| `cattlemanagementapp.py` | The app itself. |
| `requirements.txt` | Python packages for the app. |
| `requirements-windows.txt` | Extra Windows-only package (`pywebview`) for the native window. |
| `run_desktop.py` | Launcher: runs the server hidden and shows the native window. |
| `build_windows.spec` | PyInstaller recipe that turns everything into an `.exe`. |
| `installer.iss` | Inno Setup script that wraps the `.exe` into an installer (asks for the passkey). |
| `cattle.ico` | The application icon (cattle logo). |
| `.github/workflows/build-windows.yml` | Builds the `.exe` **and** the installer on GitHub. |

## Build it on GitHub (recommended)

1. Add all files to the repository root, keeping `.github/workflows/build-windows.yml`
   at that exact path.
2. Open the **Actions** tab → **Build Windows App** → **Run workflow**
   (or push a tag like `v1.0.0`).
3. When it finishes, download the **Artifacts**:
   - **HDMCattle-installer** → `HDMCattleSetup.exe` (the installer), and
   - **HDMCattle-portable-windows** → a zip you can unzip and run without installing.
4. Run `HDMCattleSetup.exe`, enter the passkey `hdmpasskey_passkeyhdm` when asked,
   and finish. It installs to Program Files with Start-menu and desktop shortcuts.

## How it behaves when installed

- Opens in its **own native window** (taskbar entry, cattle icon) using the WebView2
  engine built into Windows 10/11 — no browser, no address bar, no tabs. Closing the
  window shuts the app down.
- The Deploy button and Streamlit menu are hidden.
- Data is stored in `%LOCALAPPDATA%\HDM Cattle Management\cattle.db`, so it survives
  reinstalls. Back it up by copying that file.
- Runs fully offline.
- **Fallbacks:** if the native window can't start, it opens a standalone Edge/Chrome
  app window; if neither is present, the default browser — so the app always opens.

## Building on a Windows machine yourself (optional)

Requires Python 3.11 and Inno Setup 6.

```bat
pip install -r requirements.txt
pip install -r requirements-windows.txt
pip install pyinstaller==6.11.1
pyinstaller build_windows.spec --noconfirm --clean
iscc installer.iss
```

Produces `dist\HDMCattle\HDMCattle.exe` and `Output\HDMCattleSetup.exe`.

## Notes

- If Windows SmartScreen warns about an unsigned app, choose **More info → Run anyway**.
- The passkey is `hdmpasskey_passkeyhdm`; only its hash is embedded in the installer.
