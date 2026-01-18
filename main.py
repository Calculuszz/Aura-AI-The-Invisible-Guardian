import cv2
import time
import winsound
import os
import datetime
from config import Config
from detector import PoseDetector, FallAnalyzer
from renderer import PrivacyRenderer
from notifier import Notifier

def main():
    # Initialize Modules
    detector = PoseDetector()
    analyzer = FallAnalyzer()
    renderer = PrivacyRenderer()
    notifier = Notifier()
    
    # Snapshot Dir
    if not os.path.exists(Config.ALERTS_DIR):
        os.makedirs(Config.ALERTS_DIR)

    # Open Camera
    cap = cv2.VideoCapture(Config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, Config.FPS)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    print(f"Starting {Config.WINDOW_NAME}...")
    print("Press 'q' to quit.")

    last_beep_time = 0
    
    while True:
        success, frame = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        # 1. Detection
        timestamp_ms = int(time.time() * 1000)
        landmarks = detector.find_pose(frame, timestamp_ms)
        
        # 2. Analysis
        status = "NORMAL"
        velocity = 0
        angle = 0
        
        if landmarks:
            status, landmarks, angle, velocity = analyzer.analyze(landmarks)
            
        # 3. Actions & Feedback
        current_time = time.time()
        
        if status == "POTENTIAL_FALL":
            # Soft warning beep per second
            if current_time - last_beep_time > 1.0:
                 winsound.Beep(1000, 200) # 1kHz, 200ms
                 last_beep_time = current_time
                 
        elif status == "FALL_DETECTED":
             # Alarm!
             if current_time - last_beep_time > 0.5:
                 winsound.Beep(2500, 400) # 2.5kHz, 400ms
                 last_beep_time = current_time
             
             # Capture Snapshot (Once per event ideally, but here simple)
             # Notifier handles "alert cooldown" so let's do similar or just save.
             # We only save if we send an alert logic?
             # Let's save every time the notifier alerts (controlled by notifier internally).
             # But notifier runs async. Let's do a simple check here.
             pass

        # Notification Trigger
        if status == "FALL_DETECTED":
            notifier.alert("FALL_DETECTED", location="Living Room (Camera 1)")
            
            # Save Snapshot if just triggered (Logic inside Notifier is cooling down, 
            # here we might save redundant images if we don't check cooldown, but it's okay for now
            # or we check if notifier.last_alert_time just updated.
            # Simplified: Save if status is FALL_DETECTED. 
            # To avoid spam, we rely on the fact user will stand up or we accept multiple images.
            timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(Config.ALERTS_DIR, f"fall_{timestamp_str}.png")
            if not os.path.exists(filename): # 1 sec granularity check
                 # We want to save the PRIVACY frame, not the raw frame!
                 # So we render first.
                 pass

        # 4. Rendering (Privacy Mode)
        # Always render to get the privacy frame
        privacy_frame = renderer.draw(frame.shape, landmarks, status, velocity, angle)
        
        # Save snapshot logic (continued)
        if status == "FALL_DETECTED" and Config.PRIVACY_MODE:
             timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
             filename = os.path.join(Config.ALERTS_DIR, f"fall_{timestamp_str}.png")
             if not os.path.exists(filename):
                  cv2.imwrite(filename, privacy_frame)

        if Config.PRIVACY_MODE:
            output_image = privacy_frame
        else:
            output_image = frame
            # If not privacy mode, we might want overlay.
            pass

        # Show Result
        cv2.imshow(Config.WINDOW_NAME, output_image)

        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
