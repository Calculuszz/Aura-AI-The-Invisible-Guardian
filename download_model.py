import requests

url = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
output = "pose_landmarker_lite.task"

print(f"Downloading {output} from {url}...")
response = requests.get(url)
with open(output, 'wb') as f:
    f.write(response.content)
print("Download complete.")
