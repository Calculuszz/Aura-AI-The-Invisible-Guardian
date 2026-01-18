# Aura AI: The Invisible Guardian 🛡️✨
**Privacy-First Fall Detection System using Computer Vision**

Aura AI is a high-performance fall detection system designed for homes and elderly care. Unlike traditional surveillance, Aura uses AI to process only human pose data (skeletons), ensuring that your actual video feed never leaves the device. It's security, without the loss of privacy.

---

## 🌟 Key Highlights
*   **Privacy-Safe Monitoring**: Renders only stick-figure representations. No faces, no recognizable features.
*   **Physics-Based Detection**: Uses a combination of "Head Drop Velocity" and "Torso Angle Analysis" to differentiate between a real fall and just sitting down.
*   **Zero-Cloud Processing**: All Heavy-lifting AI (MediaPipe) runs locally on your machine or browser.
*   **Instant Multi-Channel Alerts**: Notifications via Telegram, Webhooks, and automatic logging to Google Sheets.

---

## 📁 Project Structure
```text
├── web/                  # Premium Interactive Landing Page & Web Demo
│   ├── index.html        # Glassmorphism UI
│   ├── app.js            # Browser-based Pose Detection (MediaPipe JS)
│   └── styles.css        # Modern design system
├── main.py               # Local Desktop Application controller
├── detector.py           # Core Logic: Pose estimation & Fall Analysis
├── renderer.py           # Privacy Engine: Skeleton rendering
├── notifier.py           # Notification routing (Telegram/Sheets)
├── config.py             # Global thresholds & API settings
└── requirements.txt      # Python dependencies
```

---

## 🚀 Getting Started

### 1. Local Desktop App (Python)
Best for 24/7 monitoring in a specific room.
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure your alerts in `config.py` (optional).
3. Run the app:
   ```bash
   python main.py
   ```

### 2. Interactive Web Demo
Best for showing the concept to users or testing via browser.
1. Move to the web folder:
   ```bash
   cd web
   ```
2. Start a simple server:
   ```bash
   python -m http.server 8000
   ```
3. Open `http://localhost:8000` in your browser.

---

## 🧠 The Logic Behind Aura
Aura doesn't just look for "someone on the floor." It analyzes:
1.  **The Drop**: Does the head y-coordinate drop by > 30% in less than 0.5 seconds?
2.  **The Angle**: Is the torso angle (Shoulders to Hips) horizontal (< 45°)?
3.  **The Persistence**: Does the body remain in this horizontal state for > 3 seconds?

Only when all criteria are met is a **FALL_DETECTED** alarm triggered.

---

## 🔒 Privacy Commitment
We believe that privacy is a human right. Aura AI:
*   Processes video frames frame-by-frame and immediately discards them.
*   Only stores "Landmark Data" (coordinates of joints), never images.
*   Sends alerts without attaching raw video logs.

---

## 🎨 Deployment
Aura's landing page is ready for **Netlify**, **Vercel**, or **GitHub Pages**. Simply upload the `web/` folder and ensure your site is served over HTTPS to enable camera access.

---

**Built with ❤️ for a safer, more private world.** 
*Project created for innovative AI safety monitoring.*
