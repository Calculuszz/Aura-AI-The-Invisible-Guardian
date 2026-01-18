import mediapipe as mp
import os
import sys

print(f"MediaPipe Location: {mp.__file__}")
print(f"Dir(mp): {dir(mp)}")

try:
    print(f"Solutions: {mp.solutions}")
except AttributeError:
    print("mp.solutions does not exist")

print(f"CWD: {os.getcwd()}")
print(f"Sys Path: {sys.path}")
