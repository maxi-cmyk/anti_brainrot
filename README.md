# Anti-Brainrot 🧠⚡

A real-time focus monitoring system that uses your webcam and AI-powered face tracking to detect when you're looking down at your phone instead of working. When you get distracted for too long, it hijacks your screen with a fullscreen meme and plays an alarm to snap you back into focus.

## How It Works

1. **Face Mesh AI** — Uses MediaPipe's FaceMesh to track the distance between your nose bridge and nose tip in real-time.
2. **Calibration** — You set a "focused" baseline and a "distracted" state so the system knows the difference for your setup.
3. **Focus Timer** — If you stay distracted for more than 5 seconds, the alarm triggers.
4. **Screen Hijack** — A fullscreen image + audio alarm takes over until you look back at your screen.

## Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/anti_brainrot.git
cd anti_brainrot

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run from the project root
python -m src.main
```

### Controls

| Key       | Action                                                   |
| --------- | -------------------------------------------------------- |
| `b`       | Calibrate **baseline** (look at your monitor naturally)  |
| `d`       | Calibrate **distracted** state (look down at your phone) |
| `r`       | **Reset** calibration                                    |
| `+` / `-` | Adjust distraction timer threshold (1–30s)               |
| `q`       | Quit and show session summary                            |

### Steps

1. **Start the app** — your webcam feed will open with calibration prompts.
2. **Look at your monitor** normally, then press `b` to set the baseline.
3. **Look down at your phone**, then press `d` to set the distracted state.
4. **Get to work!** If you look down for 5+ seconds, the alarm will go off.
5. **Look back at your screen** to dismiss the alarm automatically.
6. **Quit** with `q` to see your session stats (total distractions, duration).

## Project Structure

```
anti_brainrot/
├── assets/
│   ├── brainrot.jpg       # Fullscreen meme image
│   └── meme_song.mp3      # Alarm audio
├── models/
│   └── face_landmarker.task
├── src/
│   ├── main.py            # Entry point and main loop
│   ├── tracker.py         # Head tilt detection via face landmarks
│   ├── timer.py           # Distraction timer logic
│   └── ui.py              # Screen hijack and audio alarm
├── requirements.txt
├── .gitignore
└── README.md
```

## Requirements

- Python 3.10+
- Webcam
- macOS (uses `afplay` for audio — Linux/Windows users will need to modify `ui.py`)
