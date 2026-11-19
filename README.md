# SignalSpeak

**Hands-free computer control for people with ALS, using an ordinary webcam.**

Built for the QEC 2026 ALS hackathon.

**[⬇ Download for Windows](https://github.com/cooplaxx73/QEC---2026/releases/latest/download/SignalSpeak-windows.zip)** · [Quick start](#quick-start) · [Demo walkthrough](#demo-walkthrough) · [How it works](#how-it-works)

---

## What it is

ALS gradually takes away the ability to move, speak and type, and it does so differently in every person. Dedicated eye-tracking hardware exists, but it is expensive. SignalSpeak runs on a normal laptop with its built-in camera, and it adapts to the movements each person still has.

The patient looks at the screen to move the cursor and closes their eyes for half a second to click. A caregiver can adjust the settings from a phone dashboard as the disease progresses, and receives the patient's calls for help.

SignalSpeak has three parts:

| Part | Who uses it | What it does |
|---|---|---|
| **Desktop app** (`desktop/`) | The patient | Moves the cursor with the eyes or head, clicks with a face movement, types with an on-screen keyboard |
| **Website** (`public/`) | Patient and caregiver | Accounts, sign-in, privacy consent, linking a caregiver to a patient, and the app download |
| **Phone dashboard** (`public/companion/`) | The caregiver | Changes the patient's settings remotely, receives calls for help, shows the activity log |

A small Node.js server (`server.mjs`) connects them. For the demo, everything runs on one laptop.

## Features

- **Eye pointing.** Look where you want the cursor to go. A 13-dot calibration learns how your eyes map to the screen.
- **Click with a held movement.** A half-second blink clicks, so normal blinking and reading never do. A short beep confirms each click.
- **Ability test.** In about 95 seconds, the app asks for five face movements (close eyes, raise eyebrows, open mouth, smile, pucker lips) and four head turns. It scores each one for reliability, speed, accidental triggering and fatigue, then suggests the best click movement.
- **Head pointing.** If the test shows good head movement, the cursor can follow the face instead of the eyes. A webcam measures head direction far more precisely than eye direction, so the cursor is steadier.
- **Lean to zoom.** Leaning towards the screen enlarges the area around the cursor, so small targets are easy to hit.
- **Minimal overlay.** Only four large buttons stay on screen: Call Caregiver, Keyboard, Settings and Notifications.
- **Dark-room help.** If the camera picture gets too dark, the screen brightens and a white border lights the face.
- **Caregiver control with consent.** The patient approves each caregiver, can revoke access at any time, and decides whether activity is logged.
- **Two logs.** A progression log helps track motor changes over months. An audit log records every caregiver change.
- **The mouse always wins.** A helper can move the real mouse at any time and eye control lets go. F8 pauses, F9 quits.

## Quick start

Choose the setup that matches what you want to do.

### A. Try the desktop app (Windows, no setup)

Needs Windows 10 or 11 and a webcam.

1. Download **[SignalSpeak-windows.zip](https://github.com/cooplaxx73/QEC---2026/releases/latest/download/SignalSpeak-windows.zip)** (about 165 MB) and unzip it.
2. Open the `SignalSpeak` folder and double-click **SignalSpeak.exe**. Keep the folder together; the app needs its `_internal` folder.
3. If Windows shows "Windows protected your PC", choose **More info → Run anyway**. The prototype is not code-signed.
4. On first launch, choose **Use offline** (or sign in, see B).
5. Look at each dot to calibrate. Then look to move the cursor and close both eyes for half a second to click.

Offline, nothing leaves the computer. Settings, the activity log and pairing are saved in the app folder.

### B. Full system with accounts and caregiver dashboard

Needs [Node.js 22 or newer](https://nodejs.org) [12]. There are no Node packages to install.

```sh
node scripts/package-desktop.mjs
node server.mjs
```

- Website: http://localhost:3000
- Phone dashboard (shown in the laptop's browser): http://localhost:3000/app/

Create a patient account on the website, then start **SignalSpeak.exe** and sign in with it in the "Connect to your account" window. The server address is already filled in (`http://127.0.0.1:3000`). Your password is used once and not saved; the app keeps a device token in `device.json`.

To pair later, or with a different account, double-click **Pair with account.bat** in the app folder. Keep the server running while you use the caregiver features.

`package-desktop.mjs` builds the optional Python source ZIP offered on the website's Download page.

### C. Run the desktop app from Python source

For development, or on macOS and Linux. Needs Python 3.11 (MediaPipe does not support every newer version) and a webcam.

```sh
cd desktop
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python connect.py               # optional: pair with a patient account
python main.py
```

The first run downloads the face model (about 4 MB). To try the overlay with a normal mouse, without a webcam or server, run `python preview_overlay.py`.

## Demo walkthrough

1. Start the server (setup B) and open the website.
2. Create a patient account. Accept the privacy notice and choose whether to enable activity logging.
3. Copy the patient ID from My account. Sign out, create a caregiver account and request a connection with that ID.
4. Sign back in as the patient and accept the connection. To be signed in as both at once, use a private window for one of them.
5. Download and start the desktop app, sign in as the patient, and calibrate by looking at the dots.
6. Open **Settings → Ability test** on the desktop and run the test. Choose the suggested click movement and pointing method.
7. Open `/app/` as the caregiver and select the patient. Change a setting, or press **Run ability test on desktop**. The desktop announces each change.
8. On the desktop, press the phone button to call the caregiver. The request appears in the dashboard.
9. Revoke the connection on the website to remove the caregiver's access.

## Controls

| Action | How |
|---|---|
| Move the cursor | Look where you want it to go, or turn your head if head pointing is on |
| Click | Close both eyes for about half a second, or use the movement the ability test chose |
| Zoom | Look at a target and lean towards the screen. Sit back, then click in the zoomed view |
| Type | Press the keyboard button and use the on-screen keyboard |
| Call for help | Press the phone button |
| Pause eye control | F8 (for a helper) |
| Use the real mouse | Just move it. Eye control returns 2 seconds after the mouse stops |
| Quit | F9, or Settings → Turn off |

## How it works

1. **Seeing the face.** Each webcam frame goes through Google's MediaPipe Face Landmarker [1], [2]. It returns 478 points on the face [3], including the centre of each iris, plus 52 scores for facial movements (such as "left eye closed") and a matrix giving the direction of the head.
2. **Calibration.** The patient looks at (or points their nose at) 13 dots. For each dot the program records ten numbers describing the eyes and head. A ridge regression [4], which is a line fit that resists noise, learns how those numbers map to a position on the screen. The fit is checked by hiding one dot at a time and predicting it.
3. **Moving the cursor.** Each new frame gives a predicted screen position. A filter holds the cursor steady while the patient rests on a spot and lets it jump quickly when they look elsewhere. The cursor then glides to that position about 120 times a second.
4. **Clicking.** The chosen movement must be held briefly. For a blink that is about half a second, so normal blinks never click. The click lands where the patient was looking just before the movement began.
5. **Staying connected.** The desktop is paired once with the patient's account. It then loads saved settings from the server, receives changes from the caregiver, and sends calls for help.

File-by-file details are in [`desktop/README.md`](desktop/README.md).

## Privacy and data

- Camera frames are processed on the patient's computer. They are never saved and never sent.
- Activity logging is off unless the patient turns it on. Only the patient can change this.
- With logging on, the log holds action types, timings, estimated gaze samples and click positions. It never holds typed text, screenshots or video.
- Every settings change is recorded in an audit log under the account that made it.
- Passwords are stored as salted scrypt hashes. The desktop authenticates with a separate device token, never the password.
- The integrated demo does not transmit video or audio.
- Accounts and care data are stored in a local `data/` folder, which Git ignores.

## Project status

**Working:** the Windows app download, accounts and sign-in, consent, caregiver linking and revocation, desktop pairing, remote settings, eye and head pointing, click by blink or another movement, the ability test, lean-to-zoom, on-screen keyboard, automatic screen brightness in dark rooms, activity log with charts and export, and calls for help.

**Not done:** video and audio calls (switched off), a code-signed installer, a macOS app, real-phone networking over HTTPS, production-grade identity, and account deletion.

**Known limits:** webcam eye tracking is accurate to roughly 3 to 7% of the screen width, which is why targets are large and zoom exists. Accuracy depends on lighting and on the laptop's camera. Head pointing needs neck movement. This is a prototype and not a medical device.

## Development

### Tests

```sh
node --test
cd desktop
python -m unittest discover -s tests -v
```

The Python tests use made-up face data, so they need no camera.

### Building the Windows app

From `desktop/`, inside the virtual environment (setup C):

```sh
pip install pyinstaller
python build_exe.py
```

This creates `desktop/dist/SignalSpeak-windows.zip` with `SignalSpeak.exe`, the face model built in, a **Pair with account.bat** shortcut and a short READ ME. The recipe is in `desktop/signalspeak.spec`. Upload the zip to a GitHub release so the Download links keep working.

### Repository layout

| Path | Contents |
|---|---|
| `desktop/` | The patient app (Python), its tests and the Windows build recipe |
| `public/` | The website |
| `public/companion/` | The phone dashboard |
| `server.mjs`, `care-api.mjs`, `telemetry.mjs` | The account and care server (Node.js) |
| `scripts/` | Packs the desktop source for the website's Download page |
| `test/` | Server tests |

## References

[1] Google. (n.d.). *Face landmark detection guide (MediaPipe Face Landmarker)*. Google AI Edge. https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker

[2] Lugaresi, C., Tang, J., Nash, H., McClanahan, C., Uboweja, E., Hays, M., Zhang, F., Chang, C.-L., Yong, M. G., Lee, J., Chang, W.-T., Hua, W., Georg, M., & Grundmann, M. (2019). *MediaPipe: A framework for building perception pipelines*. arXiv:1906.08172. https://arxiv.org/abs/1906.08172

[3] Kartynnik, Y., Ablavatski, A., Grishchenko, I., & Grundmann, M. (2019). *Real-time facial surface geometry from monocular video on mobile GPUs*. arXiv:1907.06724. https://arxiv.org/abs/1907.06724

[4] Hoerl, A. E., & Kennard, R. W. (1970). Ridge regression: Biased estimation for nonorthogonal problems. *Technometrics, 12*(1), 55–67. https://doi.org/10.1080/00401706.1970.10488634

[5] Bradski, G. (2000). The OpenCV library. *Dr. Dobb's Journal of Software Tools*. https://opencv.org

[6] Harris, C. R., Millman, K. J., van der Walt, S. J., et al. (2020). Array programming with NumPy. *Nature, 585*, 357–362. https://doi.org/10.1038/s41586-020-2649-2

[7] The Qt Company. *Qt for Python (PySide6)* [Software, LGPL]. https://doc.qt.io/qtforpython-6/

[8] Palmér, M. *pynput* [Software, LGPL]. https://pynput.readthedocs.io

[9] Bhat, N. M. *pyttsx3* [Software, MPL 2.0]. https://pyttsx3.readthedocs.io

[10] Crozzers. *screen-brightness-control* [Software, MIT]. https://github.com/Crozzers/screen_brightness_control

[11] Reitz, K. *Requests* [Software, Apache 2.0]. https://requests.readthedocs.io

[12] OpenJS Foundation. *Node.js* [Software]. https://nodejs.org

[13] PyInstaller Development Team. *PyInstaller* [Software, GPL with bootloader exception]. https://pyinstaller.org

OpenCV [5] reads the webcam, NumPy [6] does the calibration maths, PySide6 [7] draws the windows, pynput [8] sends clicks and key presses, pyttsx3 [9] reads text aloud, screen-brightness-control [10] adjusts brightness, Requests [11] talks to the server, and PyInstaller [13] packages the Windows app.

## Team and attribution

Original phone interface: teammate's `app` branch. Original eye tracking and desktop program: teammate's `action-implementation` branch. Website and integration: `web` and `codex/integrated-demo` branches. Each source file names the libraries it uses and the AI assistance involved.

## AI Tools Acknowledgement

The following AI tools were used to assist with brainstorming, code development, debugging, and documentation. The team reviewed and tested the results.

- **OpenAI.** (2026). *ChatGPT* [Large language model]. https://chatgpt.com/
- **OpenAI.** (2026). *Codex* [AI coding agent]. https://openai.com/codex/
- **Anthropic.** (2026). *Claude* [Large language model]. https://claude.ai/
- **Anthropic.** (2026). *Claude Code* [AI coding agent]. https://claude.com/claude-code
