import cv2
import os
import time
from src.timer import FocusTimer
from src.tracker import FocusTracker
from src.ui import ScreenHijack

import mediapipe as mp

def main():
    model_path = os.path.join(os.path.dirname(__file__), "..", "models", "face_landmarker.task")

    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.VIDEO,
        num_faces=1,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
    )

    landmarker = FaceLandmarker.create_from_options(options)
    tracker = FocusTracker()
    timer = FocusTimer(threshold_seconds=3.0)
    ui = ScreenHijack(assets_dir="assets")

    cap = cv2.VideoCapture(0)
    frame_timestamp_ms = 0

    # Session stats
    distraction_count = 0
    session_start = time.time()

    print("--- ANTI-BRAINROT SYSTEM BOOTING ---")
    print("1. Look at your monitor naturally and press 'b' to set BASELINE.")
    print("2. Look down at your phone and press 'd' to set DISTRACTED state.")
    print("3. Press 'r' to reset calibration.")
    print("4. Press up arrow / down arrow to adjust distraction timer.")
    print("5. Press 'q' at any time to quit.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            continue

        frame_timestamp_ms += 33  # ~30 fps

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)

        if result.face_landmarks:
            landmarks = result.face_landmarks[0]

            key = cv2.waitKeyEx(1)
            if key == ord('b'):
                tracker.calibrate_baseline(landmarks)
            elif key == ord('d'):
                tracker.calibrate_distracted(landmarks)
            elif key == ord('r'):
                tracker.reset()
                timer.is_distracted = False
                timer.start_time = 0
                ui.dismiss_alarm()
                print("--- CALIBRATION RESET ---")
                print("Press 'b' for baseline, 'd' for distracted.")
            elif key == 63232:  # Up arrow (macOS)
                timer.threshold = min(timer.threshold + 1.0, 30.0)
                print(f"Timer threshold: {timer.threshold:.0f}s")
            elif key == 63233:  # Down arrow (macOS)
                timer.threshold = max(timer.threshold - 1.0, 1.0)
                print(f"Timer threshold: {timer.threshold:.0f}s")
            elif key == ord('q'):
                break

            # Calibration status HUD
            if not tracker.baseline_dist:
                cv2.putText(frame, "Press 'b' to calibrate BASELINE", (30, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
            elif not tracker.distracted_dist:
                cv2.putText(frame, "Press 'd' to calibrate DISTRACTED", (30, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
            else:
                # Live tracking
                currently_distracted = tracker.is_distracted(landmarks)
                trigger_ui = timer.update(currently_distracted)

                if trigger_ui:
                    if not ui.is_active:
                        distraction_count += 1
                    ui.trigger_alarm()
                elif not currently_distracted and ui.is_active:
                    ui.dismiss_alarm()

                # Status HUD
                status_text = "DISTRACTED" if currently_distracted else "FOCUSED"
                color = (0, 0, 255) if currently_distracted else (0, 255, 0)
                cv2.putText(frame, f"State: {status_text}", (30, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)

            # Always show timer threshold and distraction count
            cv2.putText(frame, f"Timer: {timer.threshold:.0f}s | Distractions: {distraction_count}", (30, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 200, 200), 2)
        else:
            key = cv2.waitKeyEx(1)
            if key == ord('q'):
                break
            cv2.putText(frame, "No face detected", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Show the live webcam feed
        cv2.imshow('Anti-Brainrot Camera Feed', frame)

    # Session summary
    session_duration = time.time() - session_start
    minutes = int(session_duration // 60)
    seconds = int(session_duration % 60)
    print("\n--- SESSION SUMMARY ---")
    print(f"Duration: {minutes}m {seconds}s")
    print(f"Total distractions: {distraction_count}")
    if distraction_count > 0:
        print(f"Average: 1 distraction every {session_duration / distraction_count:.0f}s")
    print("--- GOODBYE ---")

    # Clean up
    landmarker.close()
    ui.dismiss_alarm()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
