// MediaPipe Pose Setup
let pose = null;
let camera = null;
let isRunning = false;

// Fall Detection State
let lastHeadY = null;
let lastTime = Date.now();
let state = "NORMAL"; // NORMAL, POTENTIAL_FALL, FALL_DETECTED
let fallStartTime = 0;
let lyingStartTime = 0;
let landmarkHistory = [];
const SMOOTHING_WINDOW = 5;
const DROP_VELOCITY_THRESHOLD = 0.3;
const FALL_ANGLE_THRESHOLD = 45;
const LYING_DOWN_DURATION = 3000; // ms

// Audio Context
const audioContext = new (window.AudioContext || window.webkitAudioContext)();

// Smooth scroll
function scrollToDemo() {
    document.getElementById('demo').scrollIntoView({ behavior: 'smooth' });
}

// Beep function
function beep(frequency, duration) {
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    oscillator.frequency.value = frequency;
    oscillator.type = 'sine';

    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration / 1000);

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + duration / 1000);
}

// Smooth landmarks
function smoothLandmarks(landmarks) {
    landmarkHistory.push(landmarks);
    if (landmarkHistory.length > SMOOTHING_WINDOW) {
        landmarkHistory.shift();
    }

    if (landmarkHistory.length < 2) return landmarks;

    const smoothed = [];
    for (let i = 0; i < landmarks.length; i++) {
        let avgX = 0, avgY = 0, avgZ = 0;
        for (let frame of landmarkHistory) {
            avgX += frame[i].x;
            avgY += frame[i].y;
            avgZ += frame[i].z;
        }
        smoothed.push({
            x: avgX / landmarkHistory.length,
            y: avgY / landmarkHistory.length,
            z: avgZ / landmarkHistory.length,
            visibility: landmarks[i].visibility
        });
    }
    return smoothed;
}

// Calculate torso angle
function calculateTorsoAngle(landmarks) {
    const lShoulder = landmarks[11];
    const rShoulder = landmarks[12];
    const lHip = landmarks[23];
    const rHip = landmarks[24];

    const midShoulderX = (lShoulder.x + rShoulder.x) / 2;
    const midShoulderY = (lShoulder.y + rShoulder.y) / 2;
    const midHipX = (lHip.x + rHip.x) / 2;
    const midHipY = (lHip.y + rHip.y) / 2;

    const dy = midHipY - midShoulderY;
    const dx = midHipX - midShoulderX;

    const angleRad = Math.atan(Math.abs(dy / (dx || 0.00001)));
    return angleRad * (180 / Math.PI);
}

// Analyze fall
function analyzeFall(landmarks) {
    const smoothed = smoothLandmarks(landmarks);
    const currentTime = Date.now();

    // Key landmarks
    const nose = smoothed[0];
    const lShoulder = smoothed[11];
    const rShoulder = smoothed[12];

    // 1. Velocity check
    let velocity = 0;
    let isFalling = false;

    if (lastHeadY !== null) {
        const deltaY = nose.y - lastHeadY;
        const deltaTime = (currentTime - lastTime) / 1000;
        velocity = deltaY / deltaTime;

        if (velocity > DROP_VELOCITY_THRESHOLD) {
            isFalling = true;
        }
    }

    lastHeadY = nose.y;
    lastTime = currentTime;

    // 2. Torso angle
    const angle = calculateTorsoAngle(smoothed);
    const isHorizontal = angle < FALL_ANGLE_THRESHOLD;

    // 3. Height check
    const yCoords = smoothed.map(lm => lm.y);
    const height = Math.max(...yCoords) - Math.min(...yCoords);

    // 4. State machine
    let status = "NORMAL";

    if (state === "NORMAL") {
        if (isFalling && height > 0.4) {
            state = "POTENTIAL_FALL";
            fallStartTime = currentTime;
        }
    } else if (state === "POTENTIAL_FALL") {
        const timeSinceFall = currentTime - fallStartTime;

        if (isHorizontal) {
            if (lyingStartTime === 0) {
                lyingStartTime = currentTime;
            }

            const timeLying = currentTime - lyingStartTime;
            if (timeLying > LYING_DOWN_DURATION) {
                state = "FALL_DETECTED";
                status = "FALL_DETECTED";
            } else {
                status = "POTENTIAL_FALL";
            }
        } else {
            if (timeSinceFall > 1500) {
                state = "NORMAL";
                lyingStartTime = 0;
            }
        }
    } else if (state === "FALL_DETECTED") {
        status = "FALL_DETECTED";
        if (!isHorizontal && height > 0.5) {
            state = "NORMAL";
            lyingStartTime = 0;
        }
    }

    return { status, velocity, angle };
}

// Update UI
function updateUI(status, velocity, angle) {
    const statusText = document.getElementById('statusText');
    const angleText = document.getElementById('angleText');
    const pillStatus = document.getElementById('pillStatus');

    if (statusText) statusText.textContent = status;
    if (angleText) angleText.textContent = Math.round(angle);

    if (pillStatus) {
        // Reset classes
        pillStatus.style.background = 'rgba(255, 255, 255, 0.05)';
        pillStatus.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        pillStatus.style.color = '#a1a1aa';

        if (status === "POTENTIAL_FALL") {
            pillStatus.style.background = 'rgba(245, 158, 11, 0.1)';
            pillStatus.style.borderColor = '#f59e0b';
            pillStatus.style.color = '#f59e0b';
            beep(1000, 200);
        } else if (status === "FALL_DETECTED") {
            pillStatus.style.background = 'rgba(239, 68, 68, 0.1)';
            pillStatus.style.borderColor = '#ef4444';
            pillStatus.style.color = '#ef4444';
            beep(2500, 400);
        } else if (status === "NORMAL" || status === "READY") {
            pillStatus.style.background = 'rgba(168, 85, 247, 0.1)';
            pillStatus.style.borderColor = '#a855f7';
            pillStatus.style.color = '#a855f7';
        }
    }
}

// Draw skeleton
function drawSkeleton(canvasCtx, landmarks, width, height, status) {
    canvasCtx.clearRect(0, 0, width, height);

    // Background
    canvasCtx.fillStyle = '#000000';
    canvasCtx.fillRect(0, 0, width, height);

    if (!landmarks) return;

    // Color based on status
    let color = '#a855f7';
    if (status === "POTENTIAL_FALL") color = '#f59e0b';
    if (status === "FALL_DETECTED") color = '#ef4444';

    // Connections
    const connections = [
        [11, 12], [23, 24], [11, 23], [12, 24],
        [11, 13], [13, 15], [12, 14], [14, 16],
        [23, 25], [25, 27], [24, 26], [26, 28],
        [0, 1], [1, 4], [4, 5], [0, 5]
    ];

    canvasCtx.strokeStyle = '#ffffff';
    canvasCtx.lineWidth = status === "FALL_DETECTED" ? 4 : 2;

    connections.forEach(([start, end]) => {
        if (start < landmarks.length && end < landmarks.length) {
            const startLm = landmarks[start];
            const endLm = landmarks[end];

            canvasCtx.beginPath();
            canvasCtx.moveTo(startLm.x * width, startLm.y * height);
            canvasCtx.lineTo(endLm.x * width, endLm.y * height);
            canvasCtx.stroke();
        }
    });

    // Points
    canvasCtx.fillStyle = color;
    landmarks.forEach(lm => {
        const x = lm.x * width;
        const y = lm.y * height;

        canvasCtx.beginPath();
        canvasCtx.arc(x, y, 5, 0, 2 * Math.PI);
        canvasCtx.fill();

        // Glow
        canvasCtx.strokeStyle = color;
        canvasCtx.lineWidth = 1;
        canvasCtx.beginPath();
        canvasCtx.arc(x, y, 8, 0, 2 * Math.PI);
        canvasCtx.stroke();
    });

    // Border if FALL_DETECTED
    if (status === "FALL_DETECTED") {
        canvasCtx.strokeStyle = color;
        canvasCtx.lineWidth = 10;
        canvasCtx.strokeRect(0, 0, width, height);
    }
}

// On results callback
function onResults(results) {
    const canvas = document.getElementById('output');
    const canvasCtx = canvas.getContext('2d');

    if (results.poseLandmarks) {
        const { status, velocity, angle } = analyzeFall(results.poseLandmarks);
        updateUI(status, velocity, angle);
        drawSkeleton(canvasCtx, results.poseLandmarks, canvas.width, canvas.height, status);
    } else {
        canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
        canvasCtx.fillStyle = '#000000';
        canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
    }
}

// Start demo
async function startDemo() {
    const videoElement = document.getElementById('webcam');
    const canvas = document.getElementById('output');

    // Setup canvas
    canvas.width = 640;
    canvas.height = 480;

    // Initialize Pose
    pose = new Pose({
        locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
        }
    });

    pose.setOptions({
        modelComplexity: 1,
        smoothLandmarks: true,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
    });

    pose.onResults(onResults);

    // Start camera
    camera = new Camera(videoElement, {
        onFrame: async () => {
            await pose.send({ image: videoElement });
        },
        width: 640,
        height: 480
    });

    await camera.start();
    isRunning = true;

    document.getElementById('startBtn').style.display = 'none';
    document.getElementById('stopBtn').style.display = 'flex';
}

// Stop demo
function stopDemo() {
    if (camera) {
        camera.stop();
    }
    isRunning = false;

    const canvas = document.getElementById('output');
    const canvasCtx = canvas.getContext('2d');
    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

    document.getElementById('startBtn').style.display = 'flex';
    document.getElementById('stopBtn').style.display = 'none';

    // Reset state
    state = "NORMAL";
    lastHeadY = null;
    landmarkHistory = [];

    updateUI("READY", 0, 0);
}

// Draw skeleton preview on load
window.addEventListener('load', () => {
    const previewCanvas = document.getElementById('skeletonPreview');
    if (previewCanvas) {
        const ctx = previewCanvas.getContext('2d');
        previewCanvas.width = 400;
        previewCanvas.height = 300;

        // Draw a sample skeleton
        const sampleLandmarks = [];
        for (let i = 0; i < 33; i++) {
            sampleLandmarks.push({
                x: 0.5 + Math.random() * 0.1 - 0.05,
                y: 0.2 + (i / 33) * 0.6,
                z: 0
            });
        }

        drawSkeleton(ctx, sampleLandmarks, 400, 300, "NORMAL");
    }
});
