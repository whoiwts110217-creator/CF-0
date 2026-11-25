# Set up the CF-0 relay on the HP

This is the one setup for the public CF-0 relay. Double-click `SETUP_CF0.bat`. It is safe to run again. It does not delete your files, the local database, or a token you already saved.

A real run on the HP PC is unverified until you run it there and see the result yourself.

## What you need

- You are at the HP, signed in as yourself. The schedule runs only while you are signed in. It does not ask for an administrator password.
- The PC can reach the internet.
- Python 3.10 or newer, with the `py` launcher, and Git. If either is missing, the setup window tries to install it and tells you the official download page if that fails. You do not need to buy anything. The relay uses only the Python standard library.

If you previously paused `CavemanFocusCF0Relay` for maintenance, this setup turns that one task back on. It does not turn on `CavemanFocusCF0FastLane` or `CavemanFocusSupervisor`.

## Steps

1. Get a copy of this repository that contains `SETUP_CF0.bat` (download the ZIP, or use a folder you already have).
2. Double-click `SETUP_CF0.bat`. Leave the window open.
3. The script downloads or updates CF-0 in this folder:

   `C:\Users\<your Windows name>\CavemanFocus\CF-0`

   If that folder already exists and is not this repository, the script stops and deletes nothing. Move that folder aside and run the setup again.
4. It creates the relay database the first time. The usual file is:

   `C:\Users\<your Windows name>\.caveman_focus_relay\relay.sqlite3`
5. It asks for a GitHub token so the HP can post receipts. Typing is hidden. Press Enter with nothing typed to skip. You can run the setup again later and enter the token then.
6. It registers one Windows scheduled task, `CavemanFocusCF0Relay`, using the existing installer: every 5 minutes, current user, only while signed in, limited rights, one run at a time, each run limited to 3 minutes.
7. It runs a local `hp_status` check. That check does not open Notepad and does not send a job to GitHub.
8. Read the PASS/FAIL summary. `OVERALL PASS` means each required step passed. A skipped token is allowed: the relay still polls, and receipts stay on the PC.

Run `SETUP_CF0.bat` again any time. A later run updates the same folder, keeps the database, reuses a saved token without asking again, and refreshes the same task.

## The GitHub token

Reading the public queue does not need a token. Posting a receipt to GitHub does.

Create a **fine-grained** personal access token:

https://github.com/settings/personal-access-tokens/new

- Repository access: **only** `whoiwts110217-creator/CF-0`. No other repository.
- Permission: **Contents: Read and write**. GitHub applies that to the whole repository, not only the receipts folder.

Do not paste the token into chat, email, an issue, or any file in the repository.

The setup encrypts it with Windows DPAPI for your Windows user and stores it here:

`%LOCALAPPDATA%\CavemanFocus\CF0Relay\write_token.dpapi`

That is the same file the existing relay wrapper decrypts. It is not plain text. The scheduled task does not read Windows Credential Manager; it loads this DPAPI file into `CF_RELAY_GITHUB_TOKEN` only while that one poll is running, then clears it. This is how the relay authenticates today.

The first time you enter a token, setup posts one small public write-check receipt before it trusts the token. If GitHub rejects the token, nothing is saved and the task still polls without posting.

To type a different token later, delete that encrypted file on the PC (it is not the token text) and run setup again. Do not send the file to anyone. To revoke access, delete the token on GitHub's website.

## Remove the schedule

This removes `CavemanFocusCF0Relay` only. The database, the token, and the repository folder stay.

Open Command Prompt in the folder that contains `SETUP_CF0.bat` and run:

```bat
SETUP_CF0.bat -Uninstall
```

## After it says PASS

The HP must be on and you must be signed in. Within about five minutes the task polls `command_queue/inbox/` on `main`.

Make a fresh job so the clock is valid. From the CF-0 folder:

```bat
py -3 relay\cf_public_relay.py make-job --action ping
```

The printed JSON has an `id`. Save it as `command_queue/inbox/<id>.json` and commit that file to `main` before it expires (two hours). `args` must be `{}`. Do not put notes, names, or secrets in the file.

A ping receipt looks like `{"pong": true, "protocol": 1}` inside `command_queue/receipts/<id>.json` when the token is saved. If you skipped the token, the result is only in the local SQLite file, not on GitHub.

To open Notepad, do the same with:

```bat
py -3 relay\cf_public_relay.py make-job --action open_notepad
```

Commit `command_queue/inbox/<id>.json` the same way. On Windows the relay starts `notepad.exe` with no arguments taken from the job. The receipt says `"launched": true` and `"detail": "process_started_not_visual_confirmation"` when the process start succeeds. That detail means the process was started. It is not a photograph of the screen. A real run on the HP PC is unverified until you see Notepad yourself. The old `relay\INSTALL_NOTEPAD_CONTROL.ps1` still refuses to install anything; you do not need it.

`relay/health/latest.json` is a separate optional health report. It is not the command receipt. The health on/off files are in `archive/launchers/` and should be double-clicked from the installed copy in `CavemanFocus\CF-0` after the token is saved.

## Older launchers

The previous root `.bat` files were moved to `archive/launchers/`. They were not deleted. They still call the same scripts. Use `SETUP_CF0.bat` for the relay. The private HP Bridge is a different task (`CavemanFocusHPBridge`); its old double-click files are in that same archive folder.
