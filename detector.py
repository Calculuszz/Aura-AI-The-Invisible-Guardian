import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import time
import math
import numpy as np
from config import Config

class PoseDetector:
    def __init__(self):
        # Load the task file downloaded
        base_options = python.BaseOptions(model_asset_path='pose_landmarker_lite.task')
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO)
        self.landmarker = vision.PoseLandmarker.create_from_options(options)

    def find_pose(self, frame, timestamp_ms):
        # Convert to MP Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # Detect
        try:
            result = self.landmarker.detect_for_video(mp_image, int(timestamp_ms))
            if result.pose_landmarks:
                # Return the landmarks for the first detected person
                return result.pose_landmarks[0]
        except Exception as e:
            print(f"Error in detection: {e}")
            
        return None

from collections import deque
import copy

class LandmarkSmoother:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.history = deque(maxlen=window_size)

    def smooth(self, landmarks):
        # landmarks: list of NormalizedLandmark
        # We need to average x, y, z for each of the 33 landmarks over the window
        
        # Store current frame
        current_data = [(lm.x, lm.y, lm.z, lm.visibility, lm.presence) for lm in landmarks]
        self.history.append(current_data)
        
        if len(self.history) < 2:
            return landmarks
            
        # Average
        num_frames = len(self.history)
        num_landmarks = len(landmarks)
        smoothed = []
        
        for idx in range(num_landmarks):
            avg_x = sum(frame[idx][0] for frame in self.history) / num_frames
            avg_y = sum(frame[idx][1] for frame in self.history) / num_frames
            avg_z = sum(frame[idx][2] for frame in self.history) / num_frames
            # Keep visibility from latest frame
            vis = self.history[-1][idx][3]
            pres = self.history[-1][idx][4]
            
            # Create a simple object mimicking the landmark
            # MediaPipe landmarks are read-only usually, so using a simple class or named tuple
            smoothed.append(SimpleLandmark(avg_x, avg_y, avg_z, vis, pres))
            
        return smoothed

class SimpleLandmark:
    def __init__(self, x, y, z, visibility, presence):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility
        self.presence = presence

class FallAnalyzer:
    def __init__(self):
        self.last_head_y = None
        self.last_time = time.time()
        
        # State
        self.state = "NORMAL" # NORMAL, POTENTIAL_FALL, FALL_DETECTED
        self.fall_start_time = 0
        self.lying_start_time = 0
        
        self.smoother = LandmarkSmoother(window_size=Config.SMOOTHING_WINDOW_SIZE)
        
    def calculate_angle(self, a, b):
        # Calculate angle with respect to vertical axis
        # a, b are landmarks with x, y
        delta_x = b.x - a.x
        delta_y = b.y - a.y
        # In image coords, y increases downwards.
        # Vertical = (0, 1) vector
        
        radian = math.atan2(delta_y, delta_x)
        degrees = math.degrees(radian)
        # 0 is Horizontal Right. 90 is Vertical Down.
        # We want simple inclination from vertical (0 or 180).
        # Actually, let's just get inclination from Horizontal.
        return abs(degrees)

    def analyze(self, raw_landmarks):
        if not raw_landmarks:
            return "NORMAL"
            
        # 1. Smooth Landmarks
        landmarks = self.smoother.smooth(raw_landmarks)
        
        current_time = time.time()
        
        # Key Landmarks
        nose = landmarks[0]
        l_shoulder = landmarks[11]
        r_shoulder = landmarks[12]
        l_hip = landmarks[23]
        r_hip = landmarks[24]
        l_ankle = landmarks[27]
        r_ankle = landmarks[28]
        
        # --- Metrics ---
        
        # 1. Fall Velocity (Head Drop)
        current_head_y = nose.y
        is_falling = False
        velocity = 0
        
        if self.last_head_y is not None:
             delta_y = current_head_y - self.last_head_y
             delta_time = current_time - self.last_time
             
             if delta_time > 0:
                 velocity = delta_y / delta_time 
                 if velocity > Config.DROP_VELOCITY_THRESHOLD:
                     is_falling = True
        
        self.last_head_y = current_head_y
        self.last_time = current_time

        # 2. Torso Angle (Shoulder Midpoint to Hip Midpoint)
        mid_shoulder_x = (l_shoulder.x + r_shoulder.x) / 2
        mid_shoulder_y = (l_shoulder.y + r_shoulder.y) / 2
        mid_hip_x = (l_hip.x + r_hip.x) / 2
        mid_hip_y = (l_hip.y + r_hip.y) / 2
        
        dy = mid_hip_y - mid_shoulder_y
        dx = mid_hip_x - mid_shoulder_x
        if dx == 0: dx = 0.00001
        
        angle_rad = math.atan(abs(dy / dx))
        angle_deg = math.degrees(angle_rad) # 0 = Horizontal, 90 = Vertical logic above was atan2, here atan
        
        # If dy is large and dx is small -> Vertical (Angle close to 90)
        # If dy is small -> Horizontal (Angle close to 0)
        # Let's stick to: 0 = Horizontal, 90 = Vertical
        
        # 3. Lying Down Check (Angle < Threshold AND Height Compression)
        height = max(lm.y for lm in landmarks) - min(lm.y for lm in landmarks)
        
        is_horizontal = False
        if angle_deg < Config.FALL_ANGLE_THRESHOLD: # e.g. < 45 degrees
            is_horizontal = True

        # --- State Machine ---
        status = "NORMAL"
        
        if self.state == "NORMAL":
            if is_falling:
                # Only potential if they aren't already on the floor
                if height > 0.4: 
                    self.state = "POTENTIAL_FALL"
                    self.fall_start_time = current_time
                    # NOTE: We don't trigger solely on velocity if they are sitting.
                    # But sitting can separate head velocity.
                    # We wait for the "Lying" phase to confirm.
            
        elif self.state == "POTENTIAL_FALL":
            time_since_fall = current_time - self.fall_start_time
            
            # Transition to FALL
            if is_horizontal:
                if self.lying_start_time == 0:
                    self.lying_start_time = current_time
                
                time_lying = current_time - self.lying_start_time
                if time_lying > Config.LYING_DOWN_DURATION:
                    self.state = "FALL_DETECTED"
                    status = "FALL_DETECTED"
            else:
                 # Logic for "Sitting":
                 # If time passes, velocity was high, but angle is still VERTICAL (> 45)
                 # Then it was likely sitting or crouching.
                 if time_since_fall > 1.5:
                     self.state = "NORMAL"
                     self.lying_start_time = 0
        
        elif self.state == "FALL_DETECTED":
            status = "FALL_DETECTED"
            # Auto-reset if they stand up (Vertical + Height)
            if not is_horizontal and height > 0.5:
                 self.state = "NORMAL"
                 self.lying_start_time = 0
                 
        return status, landmarks, angle_deg, velocity
