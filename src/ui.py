import cv2
import glob
import numpy as np
import os
import random
import signal
import subprocess

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.aac', '.m4a'}

class ScreenHijack:
    def __init__(self, assets_dir="assets"):
        self.window_name = "OI DO UR WORK"
        self.is_active = False
        self.audio_process = None
        self.assets_dir = assets_dir
        self.last_image = None
        self.last_audio = None

        # Scan assets folder for images and audio
        self.images = []
        self.audios = []

        if os.path.isdir(assets_dir):
            for f in os.listdir(assets_dir):
                ext = os.path.splitext(f)[1].lower()
                path = os.path.join(assets_dir, f)
                if ext in IMAGE_EXTENSIONS:
                    self.images.append(path)
                elif ext in AUDIO_EXTENSIONS:
                    self.audios.append(path)

        print(f"Loaded {len(self.images)} images and {len(self.audios)} audio files from {assets_dir}/")

        if not self.images:
            print("WARNING: No images found in assets folder.")
        if not self.audios:
            print("WARNING: No audio files found in assets folder.")
    
    def trigger_alarm(self):
        if self.is_active:
            return

        # Pick a random image and audio (avoid repeats)
        image = None
        if self.images:
            choices = [i for i in self.images if i != self.last_image] or self.images
            image_path = random.choice(choices)
            self.last_image = image_path
            image = cv2.imread(image_path)

        audio_path = None
        if self.audios:
            choices = [a for a in self.audios if a != self.last_audio] or self.audios
            audio_path = random.choice(choices)
            self.last_audio = audio_path

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_TOPMOST, 1)

        # Get the screen size from the fullscreen window
        screen_w, screen_h = cv2.getWindowImageRect(self.window_name)[2:4]
        if screen_w <= 0 or screen_h <= 0:
            screen_w, screen_h = 1920, 1080

        if image is not None:
            display = cv2.resize(image, (screen_w, screen_h), interpolation=cv2.INTER_CUBIC)
        else:
            display = np.zeros((screen_h, screen_w, 3), dtype=np.uint8)
            display[:] = (0, 0, 255)

        # Add "OI DO UR WORK" overlay at the bottom
        overlay_text = "OI DO UR WORK"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = screen_w / 500
        thickness = max(3, int(screen_w / 300))
        text_size = cv2.getTextSize(overlay_text, font, font_scale, thickness)[0]

        # Semi-transparent black bar
        bar_height = text_size[1] + 60
        overlay = display.copy()
        cv2.rectangle(overlay, (0, screen_h - bar_height), (screen_w, screen_h), (0, 0, 200), -1)
        cv2.addWeighted(overlay, 0.6, display, 0.4, 0, display)

        # Centered text
        text_x = (screen_w - text_size[0]) // 2
        text_y = screen_h - 30
        cv2.putText(display, overlay_text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)
        cv2.imshow(self.window_name, display)
        
        # Play audio in a loop
        if audio_path:
            self.audio_process = subprocess.Popen(
                ["bash", "-c", f'while true; do afplay "{audio_path}"; done'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )

        self.is_active = True

    def dismiss_alarm(self):
        if self.is_active:
            cv2.destroyWindow(self.window_name)
            if self.audio_process:
                os.killpg(os.getpgid(self.audio_process.pid), signal.SIGKILL)
                self.audio_process = None
            self.is_active = False