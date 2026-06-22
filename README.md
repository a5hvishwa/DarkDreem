# DarkDreem — Cybersecurity Awareness Simulation

A multi-platform educational tool that demonstrates how nuisance software and social-engineering attacks can temporarily disrupt a user's experience. This repository contains three distinct versions of the simulation:

1. **Desktop Simulation** (Python/Tkinter)
2. **Web Simulation** (HTML/JS/Flask)
3. **Android Native App** (Java/Android SDK)

## 🎯 Purpose

This is a **proof-of-concept simulation** for cybersecurity awareness training. It helps users understand how disruptive software works by experiencing a harmless, time-limited demonstration.

---

## 🚀 Quick Start

### 1. Web Version (Cross-Platform)
The web version runs in any browser and uses aggressive social engineering (a fake alert screen) to bypass browser auto-play restrictions.

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the Flask web server
python web_server.py

# 3. Share the simulation using localhost.run (in a new terminal)
ssh -o StrictHostKeyChecking=no -R 80:localhost:5000 nokey@localhost.run
```
Share the generated `*.lhr.life` link with any device.

### 2. Android Native App
The Android version demonstrates OS-level aggressive persistence by locking the screen, maxing the volume, and disabling the back button.

```bash
# Build the APK using Gradle wrapper
cd android-app
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
./gradlew assembleDebug
```
The APK will be generated at: `android-app/app/build/outputs/apk/debug/app-debug.apk`. 
You can install it via ADB: `adb install -r path/to/app-debug.apk` or download it directly from the web server at `/download.html`.

### 3. Desktop Version (Windows/Linux)
A full-screen Python/Tkinter simulation that demonstrates aggressive desktop takeover techniques.

```bash
# 1. Generate the alert tone (required first time)
python generate_tone.py

# 2. Run the simulation
python simulation.py
```

---

## 📁 Project Structure

```
DarkDreem/
├── web/                   # Web interface (index.html, download.html)
├── web_server.py          # Flask server to host the web interface
├── android-app/           # Android Native App source code
├── simulation.py          # Desktop tkinter simulation
├── generate_tone.py       # Synthesized alert tone generator
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## 🛡️ Safety Guarantees

- ✅ **No data collection** — nothing is sent anywhere.
- ✅ **No file modification** — your device is untouched.
- ✅ **Auto-terminate** — ends automatically after 2 minutes.

## ⌨️ Desktop Controls

| Action | Key |
|--------|-----|
| Exit desktop simulation early | `Ctrl + Q` |
| Force quit (OS level) | `Alt + F4` or OS task manager |

## ⚖️ Ethical Notice

This project is for **educational purposes only**. It must not be used to damage devices, collect user data, or interfere with normal device operation without consent.

Please Don't use missuse of this project
