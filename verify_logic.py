import time
from detector import FallAnalyzer
from types import SimpleNamespace

# Mock Landmark Class
class MockLandmark:
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z

# Mock Landmarks Generator
def create_mock_landmarks(nose_y, shoulder_y, ankle_y, width=0.2, height=0.8):
    landmarks = [MockLandmark(0,0)] * 33 # Initialize
    
    # Set specific landmarks
    landmarks[0] = MockLandmark(0.5, nose_y) # Nose
    
    # Shoulders (11, 12)
    landmarks[11] = MockLandmark(0.5 - width/2, shoulder_y)
    landmarks[12] = MockLandmark(0.5 + width/2, shoulder_y)
    
    # Ankles (27, 28)
    landmarks[27] = MockLandmark(0.5 - width/2, ankle_y)
    landmarks[28] = MockLandmark(0.5 + width/2, ankle_y)
    
    return landmarks

def test_fall_scenario():
    analyzer = FallAnalyzer()
    
    print("--- Starting Simulation ---")
    
    # 1. Standing (Normal)
    # Head at 0.1, Ankles at 0.9. Height = 0.8
    print("Phase 1: Standing")
    for _ in range(5):
        lm = create_mock_landmarks(nose_y=0.1, shoulder_y=0.2, ankle_y=0.9, width=0.2, height=0.8)
        status, _, _, _ = analyzer.analyze(lm)
        print(f"Status: {status}")
        time.sleep(0.1)

    # 2. Free Fall (Rapid Drop)
    # Head drops from 0.1 to 0.8 in 0.2 seconds
    print("\nPhase 2: Falling (Rapid Drop)")
    # Frame 1
    lm = create_mock_landmarks(nose_y=0.3, shoulder_y=0.4, ankle_y=0.9, width=0.2, height=0.6)
    status, _, _, _ = analyzer.analyze(lm)
    print(f"Status: {status} (Head Y: 0.3)")
    time.sleep(0.1)
    
    # Frame 2
    lm = create_mock_landmarks(nose_y=0.6, shoulder_y=0.7, ankle_y=0.9, width=0.2, height=0.3)
    status, _, _, _ = analyzer.analyze(lm)
    print(f"Status: {status} (Head Y: 0.6) -> Should trigger POTENTIAL")
    time.sleep(0.1)
    
    # 3. Lying Down
    # Head at 0.8, Ankles at 0.8. Height ~ 0. Width > Height.
    print("\nPhase 3: Lying Down (Waiting 3.1s)")
    start_lie = time.time()
    while time.time() - start_lie < 3.2:
        # Width 0.8, Height 0.1. Shoulders/Ankles same Y roughly.
        lm = create_mock_landmarks(nose_y=0.85, shoulder_y=0.85, ankle_y=0.85, width=0.8, height=0.1)
        status, _, _, _ = analyzer.analyze(lm)
        if status == "FALL_DETECTED":
            print(f"SUCCESS: Status is {status}!")
            return
        time.sleep(0.1)
        
    print(f"Final Status: {status}")

        if status == "FALL_DETECTED":
            print(f"SUCCESS: Status is {status}!")
            return
        time.sleep(0.1)
        
    print(f"Final Status: {status}")

if __name__ == "__main__":
    test_fall_scenario()
