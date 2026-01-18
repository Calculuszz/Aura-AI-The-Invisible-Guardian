# Aura - Privacy-First Fall Detection Landing Page

## 🚀 Features

### Live Interactive Demo
- **Real-time Pose Detection**: Uses MediaPipe Pose running entirely in the browser
- **Privacy Mode**: Only skeletal representation is shown, no video recording
- **Fall Detection Logic**: 
  - Velocity-based drop detection
  - Torso angle analysis (prevents false alarms from sitting)
  - 3-second confirmation period
- **Audio Alerts**: Different beep patterns for warnings vs. confirmed falls
- **Visual Feedback**: Color-coded status (Green/Orange/Red)

### Premium Design
- **Glassmorphism UI**: Modern frosted glass aesthetic
- **Dark Mode**: Easy on the eyes with vibrant accent colors
- **Responsive**: Works on desktop and mobile
- **Smooth Animations**: Professional transitions and effects

## 📁 File Structure

```
web/
├── index.html      # Main HTML structure
├── styles.css      # Premium styling with glassmorphism
├── app.js          # MediaPipe integration + fall detection logic
└── README.md       # This file
```

## 🎯 How to Run

### Option 1: Simple HTTP Server (Recommended)
```bash
cd web
python -m http.server 8000
```
Then open: http://localhost:8000

### Option 2: Live Server (VS Code)
1. Install "Live Server" extension
2. Right-click `index.html`
3. Select "Open with Live Server"

### Option 3: Direct File
Simply open `index.html` in a modern browser (Chrome/Edge recommended)

## 🎨 Sections

1. **Hero**: Eye-catching introduction with CTA
2. **Live Demo**: Interactive webcam-based fall detection
3. **Features**: Highlight key capabilities
4. **Privacy Comparison**: Visual explanation of privacy benefits
5. **CTA**: Final conversion section
6. **Footer**: Branding

## 🔧 Customization

### Colors
Edit CSS variables in `styles.css`:
```css
:root {
    --accent-green: #00ff88;
    --accent-cyan: #00ccff;
    --accent-purple: #8b5cf6;
}
```

### Detection Thresholds
Edit constants in `app.js`:
```javascript
const DROP_VELOCITY_THRESHOLD = 0.3;
const FALL_ANGLE_THRESHOLD = 45;
const LYING_DOWN_DURATION = 3000; // ms
```

## 📊 Browser Compatibility

- ✅ Chrome 90+
- ✅ Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+

## 🔒 Privacy

- **Zero Server Uploads**: All processing happens locally
- **No Recording**: Video never leaves the device
- **GDPR Compliant**: No personal data is stored

## 🎤 Audio Permissions

The page uses Web Audio API for beep alerts. No microphone access is required.

## 📷 Camera Permissions

The demo requires webcam access. The browser will prompt for permission when you click "Start Camera".

## 🚨 Known Limitations

- Requires HTTPS or localhost for camera access
- Best performance on desktop/laptop
- Lighting conditions affect detection accuracy

## 💡 Tips for Demo

1. **Stand back** so full body is visible
2. **Good lighting** improves accuracy
3. **Side view** works best for lying down detection
4. **Simulate fall**: Drop quickly and stay horizontal for 3+ seconds

## 📝 License

This is a demo/prototype. Customize freely for your needs.

---

Built with ❤️ using MediaPipe, Vanilla JS, and modern CSS
