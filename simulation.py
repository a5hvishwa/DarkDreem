"""
simulation.py — Cybersecurity Awareness Simulation (Core Application)

A full-screen tkinter application that simulates a "hacked system" screen
with fake data exfiltration for educational purposes.

Features:
  - Scary "YOUR SYSTEM HAS BEEN HACKED" full-screen overlay
  - Fake data transfer progress bars (contacts, photos, passwords, etc.)
  - Scrolling file extraction log
  - Audio alarm at max volume (system volume enforced)
  - Safe exit via Ctrl+Q | Auto-terminates after 2 minutes
"""

import tkinter as tk
from tkinter import font as tkfont
import threading
import subprocess
import random
import time
import math
import os
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEMO_DURATION_SECONDS = 120          # 2 minutes
VOLUME_START = 1.0                   # 100% from start
VOLUME_END = 1.0                     # Stay at 100%
SYSTEM_VOL_START = 100               # System volume 100% from start
SYSTEM_VOL_END = 100                 # Stay at 100%
SAFE_EXIT_COMBO = "<Control-q>"      # Ctrl+Q to exit early
AUDIO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alert_tone.wav")

# Color palette — hacker/threat aesthetic
BG_COLOR = "#050508"
ACCENT_RED = "#ff0033"
ACCENT_DARK_RED = "#cc0022"
ACCENT_GREEN = "#00ff41"           # matrix green
ACCENT_AMBER = "#ffb000"
TEXT_PRIMARY = "#ffffff"
TEXT_DIM = "#555555"
PANEL_BG = "#0c0c12"
CARD_BG = "#111118"
BAR_BG = "#1a1a22"
BORDER_COLOR = "#1e1e2a"

# Fake data categories for the "exfiltration" progress bars
DATA_CATEGORIES = [
    {"name": "📱 Contacts & Phone Numbers", "size": "2,847 entries",  "speed": 0.65},
    {"name": "📸 Photos & Videos",          "size": "14.2 GB",       "speed": 0.42},
    {"name": "🔑 Saved Passwords",          "size": "347 accounts",  "speed": 0.85},
    {"name": "💬 Messages & Chat Logs",     "size": "23,491 msgs",   "speed": 0.55},
    {"name": "💳 Banking & Payment Data",   "size": "12 cards",      "speed": 0.78},
    {"name": "📂 Documents & Files",        "size": "8.7 GB",        "speed": 0.38},
]

# Fake file paths for the scrolling extraction log
FAKE_FILES = [
    "/storage/emulated/0/DCIM/Camera/IMG_{}.jpg",
    "/data/data/com.whatsapp/databases/msgstore.db",
    "/data/data/com.google.android.gm/databases/EmailProvider.db",
    "/storage/emulated/0/Documents/tax_return_2025.pdf",
    "/data/data/com.android.chrome/app_chrome/Default/Login Data",
    "/storage/emulated/0/Download/bank_statement_{}.pdf",
    "/data/data/com.facebook.katana/databases/threads_db2",
    "/storage/emulated/0/Pictures/Screenshots/Screenshot_{}.png",
    "/data/data/com.android.providers.contacts/databases/contacts2.db",
    "/storage/emulated/0/Documents/passport_scan.pdf",
    "/data/data/com.instagram.android/databases/direct.db",
    "/storage/emulated/0/DCIM/Camera/VID_{}.mp4",
    "/data/data/com.google.android.apps.photos/databases/gphotos0.db",
    "/storage/emulated/0/Documents/resume_2025.docx",
    "/data/data/com.snapchat.android/databases/main.db",
    "/data/data/com.android.vending/databases/library.db",
    "/storage/emulated/0/Download/salary_slip_{}.pdf",
    "/data/data/com.google.android.apps.maps/databases/gmm_myplaces.db",
    "/data/data/com.tencent.mm/MicroMsg/EnMicroMsg.db",
    "/storage/emulated/0/Documents/medical_records.pdf",
    "/data/data/com.paypal.android.p2pmobile/databases/PayPal.db",
    "/data/data/com.amazon.mShop.android/databases/UserData.db",
    "/storage/emulated/0/Notes/personal_notes.txt",
    "/data/data/org.telegram.messenger/files/cache/dialogs.dat",
    "/storage/emulated/0/DCIM/Camera/IMG_{}_HDR.jpg",
    "/data/system/users/0/accounts.db",
    "/data/data/com.uber.driver/databases/trips.db",
    "/storage/emulated/0/Download/credit_report_{}.pdf",
    "/data/data/com.zhiliaoapp.musically/databases/video.db",
    "/data/misc/wifi/WifiConfigStore.xml",
]


# ---------------------------------------------------------------------------
# System Volume Enforcer
# ---------------------------------------------------------------------------

class SystemVolumeEnforcer:
    """
    Continuously forces the system (hardware) volume to max.
    Uses amixer (ALSA) and pactl (PulseAudio/PipeWire).
    """

    def __init__(self):
        self._stop = threading.Event()
        self._target_pct = 100
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._enforce_loop, daemon=True)
        self._thread.start()

    def set_target(self, pct: int):
        self._target_pct = max(0, min(100, pct))

    def _enforce_loop(self):
        while not self._stop.is_set():
            vol = self._target_pct
            try:
                subprocess.run(
                    ["amixer", "set", "Master", f"{vol}%"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2
                )
            except Exception:
                pass
            try:
                subprocess.run(
                    ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{vol}%"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2
                )
            except Exception:
                pass
            try:
                subprocess.run(
                    ["amixer", "set", "Master", "unmute"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2
                )
                subprocess.run(
                    ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2
                )
            except Exception:
                pass
            self._stop.wait(0.3)

    def stop(self):
        self._stop.set()
        try:
            subprocess.run(
                ["amixer", "set", "Master", "50%"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2
            )
            subprocess.run(
                ["pactl", "set-sink-volume", "@DEFAULT_SINK@", "50%"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2
            )
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Audio Player
# ---------------------------------------------------------------------------

class AudioPlayer:
    """Handles audio playback."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self._mixer_ready = False
        self._stop_flag = threading.Event()

    def start(self):
        try:
            import pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=2048)
            pygame.mixer.music.load(self.filepath)
            pygame.mixer.music.set_volume(1.0)
            pygame.mixer.music.play(loops=-1)
            self._mixer_ready = True
        except Exception as e:
            print(f"[Audio] Could not start playback: {e}")

    def set_volume(self, vol: float):
        if not self._mixer_ready:
            return
        try:
            import pygame
            pygame.mixer.music.set_volume(max(0.0, min(1.0, vol)))
        except Exception:
            pass

    def stop(self):
        self._stop_flag.set()
        if not self._mixer_ready:
            return
        try:
            import pygame
            pygame.mixer.music.fadeout(500)
            time.sleep(0.6)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Main Simulation Window
# ---------------------------------------------------------------------------

class SimulationApp:
    """Full-screen 'hacked system' simulation."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("")
        self.root.configure(bg=BG_COLOR)

        # Full-screen & topmost
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self._ignore)

        # Safe exit binding (Ctrl+Q)
        self.root.bind(SAFE_EXIT_COMBO, lambda e: self._shutdown())
        self.root.bind("<Control-Q>", lambda e: self._shutdown())

        # Block all other keyboard shortcuts
        for key in [
            "<Alt-Tab>", "<Alt-F4>", "<Alt-F2>", "<Alt-F1>",
            "<Super_L>", "<Super_R>", "<Meta_L>", "<Meta_R>",
            "<Escape>", "<Alt-Escape>", "<Control-Alt-Delete>",
            "<Alt-F9>", "<Alt-F10>", "<Alt-F11>",
            "<Control-Alt-t>", "<Control-Alt-l>",
            "<F11>", "<F4>",
        ]:
            try:
                self.root.bind(key, lambda e: "break")
            except Exception:
                pass

        # Screen dimensions
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        # State
        self.remaining = DEMO_DURATION_SECONDS
        self.audio = AudioPlayer(AUDIO_FILE)
        self.vol_enforcer = SystemVolumeEnforcer()
        self._running = True
        self._start_time = None

        # Progress tracking for each data category
        self.progress_values = [0.0] * len(DATA_CATEGORIES)
        self.progress_bars = []
        self.progress_labels = []
        self.progress_pct_labels = []

        # File log state
        self.log_lines = []
        self.file_counter = 0

        # Fake attacker info
        self.attacker_ip = f"{random.randint(45,200)}.{random.randint(10,250)}.{random.randint(1,254)}.{random.randint(1,254)}"
        self.attacker_port = random.choice([4444, 8080, 1337, 31337, 9001, 6667])

        # Build UI
        self._build_ui()

    # --- UI Construction ---------------------------------------------------

    def _build_ui(self):
        """Construct the scary 'hacked' interface — fully responsive."""

        W = self.screen_w
        H = self.screen_h

        # Scale factor based on a 1920x1080 reference
        sx = W / 1920.0   # horizontal scale
        sy = H / 1080.0   # vertical scale
        s = min(sx, sy)   # uniform scale (prevents distortion)

        def sz(base_size):
            """Scale a font size."""
            return max(7, int(base_size * s))

        # Fonts — all scaled
        self.font_hack_title = tkfont.Font(family="Courier", size=sz(36), weight="bold")
        self.font_hack_sub = tkfont.Font(family="Courier", size=sz(16), weight="bold")
        self.font_timer = tkfont.Font(family="Courier", size=sz(52), weight="bold")
        self.font_label = tkfont.Font(family="Courier", size=sz(12))
        self.font_label_bold = tkfont.Font(family="Courier", size=sz(12), weight="bold")
        self.font_small = tkfont.Font(family="Courier", size=sz(10))
        self.font_log = tkfont.Font(family="Courier", size=sz(9))
        self.font_tiny = tkfont.Font(family="Courier", size=sz(8))

        # Main canvas
        self.canvas = tk.Canvas(
            self.root, bg=BG_COLOR, highlightthickness=0,
            width=W, height=H
        )
        self.canvas.pack(fill="both", expand=True)

        # ========== TOP SECTION: HACKED TITLE ==========
        # Flashing red border at top/bottom
        border_h = max(3, int(4 * sy))
        self.top_bar = self.canvas.create_rectangle(
            0, 0, W, border_h, fill=ACCENT_RED, outline=""
        )
        self.bottom_bar = self.canvas.create_rectangle(
            0, H - border_h, W, H, fill=ACCENT_RED, outline=""
        )

        # Skull + HACKED title
        y_cursor = int(50 * sy)
        self.title_text = self.canvas.create_text(
            W // 2, y_cursor,
            text="💀  YOUR SYSTEM HAS BEEN HACKED  💀",
            fill=ACCENT_RED, font=self.font_hack_title, anchor="center"
        )

        y_cursor += int(50 * sy)
        self.canvas.create_text(
            W // 2, y_cursor,
            text="All your personal data is being extracted to a remote server",
            fill=ACCENT_AMBER, font=self.font_hack_sub, anchor="center"
        )

        # Attacker info box
        y_cursor += int(45 * sy)
        info_w = int(600 * sx)
        info_h = int(55 * sy)
        info_x = (W - info_w) // 2
        self.canvas.create_rectangle(
            info_x, y_cursor, info_x + info_w, y_cursor + info_h,
            fill=PANEL_BG, outline=ACCENT_RED, width=1
        )
        self.canvas.create_text(
            W // 2, y_cursor + int(18 * sy),
            text=f"ATTACKER SERVER:  {self.attacker_ip}:{self.attacker_port}",
            fill=ACCENT_RED, font=self.font_label_bold, anchor="center"
        )
        self.conn_status = self.canvas.create_text(
            W // 2, y_cursor + int(38 * sy),
            text="● CONNECTION ACTIVE  —  ENCRYPTED TUNNEL ESTABLISHED",
            fill=ACCENT_GREEN, font=self.font_small, anchor="center"
        )

        # ========== MIDDLE SECTION: DATA EXTRACTION PROGRESS ==========
        y_cursor += info_h + int(25 * sy)
        self.canvas.create_text(
            W // 2, y_cursor,
            text="▼  DATA EXTRACTION IN PROGRESS  ▼",
            fill=ACCENT_RED, font=self.font_label_bold, anchor="center"
        )

        y_cursor += int(30 * sy)
        bar_w = int(550 * sx)
        bar_h = max(14, int(18 * sy))
        bar_x = (W - bar_w) // 2
        label_x = bar_x - int(10 * sx)
        row_spacing = int(48 * sy)

        for i, cat in enumerate(DATA_CATEGORIES):
            row_y = y_cursor + i * row_spacing

            # Category label (left of bar)
            self.canvas.create_text(
                label_x, row_y,
                text=cat["name"], fill=TEXT_PRIMARY,
                font=self.font_label, anchor="e"
            )

            # Size label
            self.canvas.create_text(
                label_x, row_y + int(16 * sy),
                text=cat["size"], fill=TEXT_DIM,
                font=self.font_tiny, anchor="e"
            )

            # Bar background
            self.canvas.create_rectangle(
                bar_x, row_y - int(8 * sy),
                bar_x + bar_w, row_y - int(8 * sy) + bar_h,
                fill=BAR_BG, outline=BORDER_COLOR, width=1
            )

            # Bar fill (starts at 0 width)
            bar_fill = self.canvas.create_rectangle(
                bar_x + 1, row_y - int(8 * sy) + 1,
                bar_x + 1, row_y - int(8 * sy) + bar_h - 1,
                fill=ACCENT_RED, outline=""
            )
            self.progress_bars.append({
                "fill": bar_fill,
                "x": bar_x + 1,
                "y_top": row_y - int(8 * sy) + 1,
                "y_bot": row_y - int(8 * sy) + bar_h - 1,
                "w": bar_w - 2,
            })

            # Percentage label (right of bar)
            pct_label = self.canvas.create_text(
                bar_x + bar_w + int(15 * sx), row_y,
                text="0%", fill=ACCENT_RED,
                font=self.font_label_bold, anchor="w"
            )
            self.progress_pct_labels.append(pct_label)

        # ========== DATA TRANSFER STATS ==========
        y_cursor = y_cursor + len(DATA_CATEGORIES) * row_spacing + int(20 * sy)
        stats_w = int(700 * sx)
        stats_h = int(35 * sy)
        stats_x = (W - stats_w) // 2
        self.canvas.create_rectangle(
            stats_x, y_cursor, stats_x + stats_w, y_cursor + stats_h,
            fill=PANEL_BG, outline=BORDER_COLOR, width=1
        )
        self.stats_text = self.canvas.create_text(
            W // 2, y_cursor + stats_h // 2,
            text="FILES EXTRACTED: 0  |  DATA SENT: 0.0 MB  |  SPEED: 0 KB/s",
            fill=ACCENT_GREEN, font=self.font_small, anchor="center"
        )

        # ========== FILE EXTRACTION LOG ==========
        y_cursor += stats_h + int(15 * sy)
        self.canvas.create_text(
            W // 2, y_cursor,
            text="[  LIVE EXTRACTION LOG  ]",
            fill=TEXT_DIM, font=self.font_label_bold, anchor="center"
        )

        y_cursor += int(22 * sy)
        log_w = int(750 * sx)
        log_line_h = int(14 * sy)
        num_log_lines = max(4, int(7 * sy))  # scale number of visible lines
        log_h = num_log_lines * log_line_h + int(20 * sy)
        log_x = (W - log_w) // 2
        self.canvas.create_rectangle(
            log_x, y_cursor, log_x + log_w, y_cursor + log_h,
            fill="#08080d", outline=BORDER_COLOR, width=1
        )

        # Create log line text items
        self.log_text_items = []
        self._num_log_lines = num_log_lines
        for j in range(num_log_lines):
            txt = self.canvas.create_text(
                log_x + int(10 * sx), y_cursor + int(10 * sy) + j * log_line_h,
                text="", fill=ACCENT_GREEN, font=self.font_log, anchor="nw",
                width=log_w - int(20 * sx)
            )
            self.log_text_items.append(txt)

        # ========== COUNTDOWN TIMER ==========
        y_cursor += log_h + int(20 * sy)
        self.canvas.create_text(
            W // 2, y_cursor,
            text="TRANSFER COMPLETES IN:",
            fill=TEXT_DIM, font=self.font_label, anchor="center"
        )

        y_cursor += int(45 * sy)
        self.timer_text = self.canvas.create_text(
            W // 2, y_cursor,
            text="02:00", fill=ACCENT_RED, font=self.font_timer, anchor="center"
        )

        # ========== BOTTOM WARNING ==========
        self.canvas.create_text(
            W // 2, H - int(55 * sy),
            text="⚠  DO NOT ATTEMPT TO CLOSE THIS WINDOW  ⚠",
            fill=ACCENT_RED, font=self.font_label_bold, anchor="center"
        )
        self.canvas.create_text(
            W // 2, H - int(30 * sy),
            text="Your data will be permanently compromised if transfer is interrupted",
            fill=ACCENT_AMBER, font=self.font_small, anchor="center"
        )

        # Scanlines
        self._draw_scanlines()

    def _draw_scanlines(self):
        """Subtle CRT scanlines."""
        step = max(2, int(3 * self.screen_h / 1080))
        for y in range(0, self.screen_h, step):
            self.canvas.create_line(
                0, y, self.screen_w, y,
                fill="#0a0a10", width=1
            )

    # --- Animation Loop ----------------------------------------------------

    def _generate_log_entry(self):
        """Generate a fake file extraction log line."""
        self.file_counter += 1
        path = random.choice(FAKE_FILES)
        # Replace {} with random numbers to make paths look unique
        path = path.format(random.randint(10000, 99999))
        size = random.choice([
            f"{random.randint(1, 999)} KB",
            f"{random.randint(1, 50)}.{random.randint(0,9)} MB",
        ])
        return f"[{time.strftime('%H:%M:%S')}] EXFIL  {path}  ({size})"

    def _update_timer(self):
        """Main loop — called every second."""
        if not self._running:
            return

        elapsed = DEMO_DURATION_SECONDS - self.remaining
        progress = elapsed / DEMO_DURATION_SECONDS

        # --- Update countdown ---
        mins = self.remaining // 60
        secs = self.remaining % 60
        self.canvas.itemconfigure(
            self.timer_text, text=f"{mins:02d}:{secs:02d}"
        )

        # Flash timer in last 30 seconds
        if self.remaining <= 30:
            color = ACCENT_AMBER if self.remaining % 2 == 0 else ACCENT_RED
            self.canvas.itemconfigure(self.timer_text, fill=color)

        # --- Flash title ---
        if elapsed % 2 == 0:
            self.canvas.itemconfigure(self.title_text, fill=ACCENT_RED)
        else:
            self.canvas.itemconfigure(self.title_text, fill=ACCENT_DARK_RED)

        # --- Flash connection status ---
        if elapsed % 3 == 0:
            self.canvas.itemconfigure(self.conn_status,
                text="● CONNECTION ACTIVE  —  ENCRYPTED TUNNEL ESTABLISHED")
        else:
            self.canvas.itemconfigure(self.conn_status,
                text="● TRANSFERRING DATA  —  DO NOT DISCONNECT")

        # --- Update progress bars ---
        for i, cat in enumerate(DATA_CATEGORIES):
            # Each bar progresses at a different speed with some randomness
            speed = cat["speed"]
            jitter = random.uniform(-0.02, 0.04)
            self.progress_values[i] = min(
                1.0,
                self.progress_values[i] + (speed / DEMO_DURATION_SECONDS) + jitter
            )
            pct = self.progress_values[i]

            # Update bar width
            bar = self.progress_bars[i]
            fill_w = int(bar["w"] * pct)
            self.canvas.coords(
                bar["fill"],
                bar["x"], bar["y_top"],
                bar["x"] + fill_w, bar["y_bot"]
            )

            # Change color when "complete"
            if pct >= 1.0:
                self.canvas.itemconfigure(bar["fill"], fill=ACCENT_GREEN)
                self.canvas.itemconfigure(
                    self.progress_pct_labels[i], text="DONE ✓", fill=ACCENT_GREEN
                )
            else:
                self.canvas.itemconfigure(bar["fill"], fill=ACCENT_RED)
                self.canvas.itemconfigure(
                    self.progress_pct_labels[i],
                    text=f"{int(pct * 100)}%", fill=ACCENT_RED
                )

        # --- Update stats ---
        total_files = int(self.file_counter + elapsed * 3.7)
        data_mb = round(elapsed * 0.42 + random.uniform(0, 2), 1)
        speed_kb = random.randint(340, 890)
        self.canvas.itemconfigure(
            self.stats_text,
            text=f"FILES EXTRACTED: {total_files:,}  |  DATA SENT: {data_mb} MB  |  SPEED: {speed_kb} KB/s"
        )

        # --- Update scrolling file log ---
        # Add 2-3 new entries per second
        for _ in range(random.randint(2, 3)):
            self.log_lines.append(self._generate_log_entry())

        # Show the last N entries (scaled to screen)
        visible = self.log_lines[-self._num_log_lines:]
        for j, txt_item in enumerate(self.log_text_items):
            if j < len(visible):
                self.canvas.itemconfigure(txt_item, text=visible[j])

        # --- Flash top/bottom red bars ---
        if elapsed % 2 == 0:
            self.canvas.itemconfigure(self.top_bar, fill=ACCENT_RED)
            self.canvas.itemconfigure(self.bottom_bar, fill=ACCENT_RED)
        else:
            self.canvas.itemconfigure(self.top_bar, fill=ACCENT_DARK_RED)
            self.canvas.itemconfigure(self.bottom_bar, fill=ACCENT_DARK_RED)

        # --- Volume enforcement ---
        self.vol_enforcer.set_target(100)

        # --- Decrement ---
        self.remaining -= 1
        if self.remaining < 0:
            self._shutdown()
            return

        self.root.after(1000, self._update_timer)

    # --- Focus enforcement -------------------------------------------------

    def _enforce_focus(self):
        """Lock focus to this window — prevents screen switching."""
        if not self._running:
            return
        try:
            self.root.attributes("-topmost", True)
            self.root.attributes("-fullscreen", True)
            self.root.focus_force()
            self.root.lift()
            self.root.grab_set_global()
        except Exception:
            pass
        self.root.after(500, self._enforce_focus)

    # --- Lifecycle ----------------------------------------------------------

    def run(self):
        """Start the simulation."""
        # Generate tone if it doesn't exist
        if not os.path.exists(AUDIO_FILE):
            print("[*] Generating alert tone...")
            from generate_tone import generate_alert_tone
            generate_alert_tone()

        # Start audio
        threading.Thread(target=self.audio.start, daemon=True).start()

        # Start system volume enforcement
        self.vol_enforcer.start()

        # Start focus enforcement
        self.root.after(100, self._enforce_focus)

        # Kick off the timer loop
        self._start_time = time.time()
        self.root.after(1000, self._update_timer)

        # Enter mainloop
        self.root.mainloop()

    def _ignore(self):
        pass

    def _shutdown(self):
        """Gracefully shut down and restore normal state."""
        if not self._running:
            return
        self._running = False
        print("[*] Simulation ended. Returning to normal state.")

        # Stop volume enforcement and restore sane volume
        self.vol_enforcer.stop()

        # Stop audio
        self.audio.stop()

        # Release grab and restore window
        try:
            self.root.grab_release()
            self.root.attributes("-fullscreen", False)
            self.root.attributes("-topmost", False)
            self.root.destroy()
        except Exception:
            pass
        sys.exit(0)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  CYBERSECURITY AWARENESS SIMULATION")
    print("  Duration: 2 minutes | Safe exit: Ctrl+Q")
    print("=" * 60)
    app = SimulationApp()
    app.run()
