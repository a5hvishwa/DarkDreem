# DarkDreem — Cybersecurity Awareness Simulation

A Python-based educational tool that demonstrates how nuisance software and social-engineering attacks can temporarily disrupt a user's experience — all within a **safe, controlled environment**.

## 🎯 Purpose

This is a **proof-of-concept simulation** for cybersecurity awareness training. It helps users understand how disruptive software works by experiencing a harmless, time-limited demonstration.

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate the alert tone (optional — auto-generated on first run)

```bash
python generate_tone.py
```

### 3. Launch the web server

```bash
python server.py
```

### 4. Open the demo

Navigate to **http://localhost:5000** in your browser and click **"Launch Demonstration"**.

## 📁 Project Structure

```
DarkDreem/
├── server.py          # Flask web server with landing page
├── simulation.py      # Full-screen tkinter simulation
├── generate_tone.py   # Synthesized alert tone generator
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## 🔧 How It Works

| Component | Description |
|-----------|-------------|
| **Web Server** (`server.py`) | Serves a styled landing page at `localhost:5000`. Clicking "Launch" triggers the simulation. |
| **Simulation** (`simulation.py`) | Full-screen tkinter overlay with countdown timer, volume ramp, and rotating educational slides. |
| **Tone Generator** (`generate_tone.py`) | Creates a multi-layered alarm WAV file using pure sine wave synthesis (no external audio files). |

## 🛡️ Safety Guarantees

- ✅ **No data collection** — nothing is sent anywhere
- ✅ **No file modification** — your device is untouched
- ✅ **No security bypass** — system controls remain functional
- ✅ **Safe exit** — press `Ctrl+Q` at any time
- ✅ **Auto-terminate** — ends automatically after 2 minutes
- ✅ **Open source** — fully auditable code

## ⌨️ Controls

| Action | Key |
|--------|-----|
| Exit simulation early | `Ctrl + Q` |
| Force quit (OS level) | `Alt + F4` or OS task manager |

## 📚 Learning Outcomes

- Python application development
- Event handling and timers
- Multimedia playback (pygame)
- User interface design (tkinter)
- Web development (Flask)
- Cybersecurity awareness and ethical software development

## ⚖️ Ethical Notice

This project is for **educational purposes only**. It must not be used to:
- Damage devices
- Collect user data
- Prevent device shutdown
- Bypass security controls
- Interfere with normal device operation

---

*Built for cybersecurity awareness training and ethical software development education.*
