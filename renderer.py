import cv2
import numpy as np

class PrivacyRenderer:
    def __init__(self):
        # Define connections for a skeleton
        # 11-12: Shoulders
        # 23-24: Hips
        # 11-23, 12-24: Torso
        # Arms: 11-13-15, 12-14-16
        # Legs: 23-25-27, 24-26-28
        self.connections = [
            (11, 12), (23, 24), (11, 23), (12, 24),
            (11, 13), (13, 15), (12, 14), (14, 16),
            (23, 25), (25, 27), (24, 26), (26, 28),
            (0, 1), (1, 4), (4, 5), (0, 5) # Simple head
        ]

    def draw(self, frame_shape, landmarks, status="NORMAL", velocity=0, angle=0):
        # Colors (BGR)
        COLOR_NORMAL = (0, 255, 0) # Green
        COLOR_WARN = (0, 165, 255) # Orange
        COLOR_ALARM = (0, 0, 255)    # Red
        
        if status == "NORMAL":
            main_color = COLOR_NORMAL
        elif status == "POTENTIAL_FALL":
            main_color = COLOR_WARN
        else:
            main_color = COLOR_ALARM

        # Create a black background
        height, width, _ = frame_shape
        privacy_frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Dashboard / UI
        # Top Bar
        cv2.rectangle(privacy_frame, (0, 0), (width, 60), (30, 30, 30), -1)
        cv2.putText(privacy_frame, f"STATUS: {status}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, main_color, 2)
        
        # Stats (Velocity, Angle)
        stats_text = f"Spd: {velocity:.2f} | Ang: {int(angle)} deg"
        cv2.putText(privacy_frame, stats_text, (width - 350, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

        if not landmarks:
            return privacy_frame

        # Draw Connections
        for start_idx, end_idx in self.connections:
            if start_idx < len(landmarks) and end_idx < len(landmarks):
                start = landmarks[start_idx]
                end = landmarks[end_idx]
                
                x1, y1 = int(start.x * width), int(start.y * height)
                x2, y2 = int(end.x * width), int(end.y * height)
                
                # Dynamic Line Thickness
                thickness = 2
                if status == "FALL_DETECTED": 
                    thickness = 4
                
                cv2.line(privacy_frame, (x1, y1), (x2, y2), (255, 255, 255), thickness)

        # Draw Points
        for lm in landmarks:
            x, y = int(lm.x * width), int(lm.y * height)
            cv2.circle(privacy_frame, (x, y), 5, main_color, -1)
            # Glow effect (simple outline)
            cv2.circle(privacy_frame, (x, y), 8, main_color, 1)
        
        # If ALARM, draw border
        if status == "FALL_DETECTED":
            cv2.rectangle(privacy_frame, (0, 0), (width, height), main_color, 10)
        
        return privacy_frame
