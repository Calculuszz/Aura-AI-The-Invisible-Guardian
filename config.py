import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Camera Settings
    CAMERA_INDEX = 0  # Default webcam
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    FPS = 30

    # Fall Detection Thresholds
    FALL_TIME_WINDOW = 0.5  # Seconds to detect the drop
    LYING_DOWN_DURATION = 3.0  # Seconds to confirm they are on the floor
    
    # We define "Fall" as head moving down this ratio of total height per second (speed)
    # or simple vertical displacement check.
    # For a simple heuristic: if nose y changes by > 0.3 (normalized) in < 0.5s
    DROP_VELOCITY_THRESHOLD = 0.3 # Normalized coordinate change per FALL_TIME_WINDOW

    # V2: Advanced Physics
    SMOOTHING_WINDOW_SIZE = 5 # Frames to average
    FALL_ANGLE_THRESHOLD = 45 # Degrees. < 45 means closer to horizontal.
    
    # Directories
    ALERTS_DIR = "captures"

    # "Lying down" heuristic: Width > Height of bounding box, or specific keypoint arrangement
    # For now, we'll check if y-coordinates of head are close to ankles/hips (vertical compression)
    # or simply if the aspect ratio calculation indicates horizontal.

    # APIs
    GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "service_account.json")
    GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "Fall_Detection_Logs")
    
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

    # Display
    PRIVACY_MODE = True  # Default to Stick Figure only
    WINDOW_NAME = "Privacy-First Fall Detector"
