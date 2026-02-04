"""
🍼 Baby Monitor - Complete GUI Application
==========================================
Double-click this file to run!
"""

import cv2
import time
import socket
import secrets
import threading
import webbrowser
from datetime import datetime
from flask import Flask, Response, render_template_string, request
import tkinter as tk
from tkinter import messagebox, ttk
import sys
import os
import sounddevice as sd
import numpy as np
import queue

# QR Code imports
try:
    import qrcode
    from PIL import Image, ImageTk
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

app = Flask(__name__)
SECRET_TOKEN = None
camera = None
server_running = False
first_frame = None
frame_count = 0
SERVER_PORT = 5000

# Audio variables
audio_queue = queue.Queue()
audio_thread = None
audio_stream = None

MOTION_CONFIG = {
    'min_area': 3000,
    'max_area': 100000,
    'blur_size': 25,
    'threshold': 30,
    'dilate_iterations': 3,
    'learning_rate': 0.02,
    'detection_zone': True,
    'zone_margin': 0.15
}

def get_local_ip():
    """Get actual local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def check_auth(token=None):
    """Security check for token"""
    if token is None:
        token = request.args.get('token', '')
    return token == SECRET_TOKEN

def is_in_detection_zone(x, y, w, h, frame_width, frame_height):
    """Check if contour is in the center detection zone"""
    if not MOTION_CONFIG['detection_zone']:
        return True
    
    margin_x = int(frame_width * MOTION_CONFIG['zone_margin'])
    margin_y = int(frame_height * MOTION_CONFIG['zone_margin'])
    cx = x + w // 2
    cy = y + h // 2
    return (margin_x < cx < frame_width - margin_x and 
            margin_y < cy < frame_height - margin_y)

def generate_frames():
    global first_frame, frame_count, camera
    
    while server_running and camera is not None:
        success, frame = camera.read()
        if not success:
            time.sleep(0.1)
            continue
        
        frame_count += 1
        frame_height, frame_width = frame.shape[:2]
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (MOTION_CONFIG['blur_size'], MOTION_CONFIG['blur_size']), 0)

        if first_frame is None:
            first_frame = gray.copy().astype('float')
            continue

        cv2.accumulateWeighted(gray, first_frame, MOTION_CONFIG['learning_rate'])
        background = cv2.convertScaleAbs(first_frame)
        
        delta_frame = cv2.absdiff(background, gray)
        thresh_frame = cv2.threshold(delta_frame, MOTION_CONFIG['threshold'], 255, cv2.THRESH_BINARY)[1]
        thresh_frame = cv2.dilate(thresh_frame, None, iterations=MOTION_CONFIG['dilate_iterations'])
        thresh_frame = cv2.erode(thresh_frame, None, iterations=1)

        contours, _ = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        status_text = "Quiet - No Motion"
        status_color = (0, 200, 100)
        motion_detected = False
        valid_contours = []

        if MOTION_CONFIG['detection_zone']:
            margin_x = int(frame_width * MOTION_CONFIG['zone_margin'])
            margin_y = int(frame_height * MOTION_CONFIG['zone_margin'])
            cv2.rectangle(frame, (margin_x, margin_y), 
                         (frame_width - margin_x, frame_height - margin_y), 
                         (50, 50, 50), 1)

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < MOTION_CONFIG['min_area'] or area > MOTION_CONFIG['max_area']:
                continue
            
            (x, y, w, h) = cv2.boundingRect(contour)
            aspect_ratio = w / float(h) if h > 0 else 0
            if aspect_ratio > 5 or aspect_ratio < 0.2:
                continue
            
            if not is_in_detection_zone(x, y, w, h, frame_width, frame_height):
                continue
            
            valid_contours.append((x, y, w, h, area))

        if len(valid_contours) > 0:
            motion_detected = True
            status_text = "MOVEMENT DETECTED!"
            status_color = (0, 0, 255)
            
            for (x, y, w, h, area) in valid_contours:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        cv2.rectangle(frame, (0, 0), (frame_width, 40), (0, 0, 0), -1)
        cv2.rectangle(frame, (0, frame_height - 35), (frame_width, frame_height), (0, 0, 0), -1)
        
        cv2.putText(frame, status_text, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)

        timestamp = datetime.now().strftime("%I:%M:%S %p")
        cv2.putText(frame, timestamp, (frame_width - 130, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, "Baby Monitor | Secure Stream", (10, frame_height - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Baby Monitor</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>👶</text></svg>">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 18px; 
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }
        .header h1 { font-size: 1.6em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .header p { font-size: 0.85em; opacity: 0.9; margin-top: 5px; }
        .container { max-width: 900px; margin: 0 auto; padding: 20px; }
        .video-wrapper { 
            position: relative;
            background: #000;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 8px 40px rgba(0,0,0,0.5);
        }
        .video-wrapper img { width: 100%; height: auto; display: block; }
        .status-bar { display: flex; justify-content: center; gap: 20px; margin: 20px 0; flex-wrap: wrap; }
        .status-item { 
            background: rgba(255,255,255,0.1);
            padding: 12px 24px;
            border-radius: 30px;
            display: flex;
            align-items: center;
            gap: 10px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .pulse {
            width: 12px; height: 12px;
            background: #4ade80;
            border-radius: 50%;
            animation: pulse 2s infinite;
            box-shadow: 0 0 10px #4ade80;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.9); }
        }
        .secure-badge {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .footer { text-align: center; padding: 20px; color: #666; font-size: 0.85em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>👶 Baby Monitor</h1>
        <p>Secure Live Stream</p>
    </div>
    <div class="container">
        <div class="video-wrapper">
            <img src="/stream/{{ token }}" alt="Live Baby Feed">
        </div>
        <div class="status-bar">
            <div class="status-item"><div class="pulse"></div><span>Live</span></div>
            <div class="status-item" id="audioStatus"><span>🎤</span><span>Audio</span></div>
            <div class="status-item"><span>📡</span><span>Connected</span></div>
            <div class="status-item secure-badge">🔐 Protected</div>
        </div>
        
        <!-- Hidden audio element for streaming -->
        <audio id="audioStream" autoplay style="display: none;"></audio>
        
        <script>
            // Function to start audio streaming
            function startAudioStream() {
                const audioStatus = document.getElementById('audioStatus');
                
                // Create a new AudioContext for Web Audio API
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                
                // Fetch audio stream
                fetch('/audio/{{ token }}')
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Audio stream not available');
                        }
                        return response.body;
                    })
                    .then(stream => {
                        // Create a MediaStream from the response
                        const reader = stream.getReader();
                        
                        function readStream() {
                            reader.read().then(({ done, value }) => {
                                if (done) return;
                                
                                if (value && value.length > 44) { // Ensure we have WAV header + data
                                    try {
                                        // Skip WAV header (44 bytes) and convert the raw audio data
                                        const audioData = new Int16Array(value.buffer.slice(44));
                                        const floatData = new Float32Array(audioData.length);
                                        
                                        for (let i = 0; i < audioData.length; i++) {
                                            floatData[i] = audioData[i] / 32768.0; // Convert to float
                                        }
                                        
                                        // Create audio buffer
                                        const buffer = audioContext.createBuffer(1, floatData.length, 44100);
                                        buffer.copyFromChannel(floatData, 0);
                                        
                                        // Create audio source and play
                                        const source = audioContext.createBufferSource();
                                        source.buffer = buffer;
                                        source.connect(audioContext.destination);
                                        source.start();
                                        
                                        // Update status to show audio is working
                                        audioStatus.innerHTML = '<span>🎤</span><span>Audio Active</span>';
                                        audioStatus.style.background = 'rgba(34, 197, 94, 0.2)';
                                    } catch (e) {
                                        console.log('Error processing audio data:', e);
                                    }
                                }
                                
                                readStream(); // Continue reading
                            }).catch(error => {
                                console.log('Error reading audio stream:', error);
                            });
                        }
                        
                        readStream();
                    })
                    .catch(error => {
                        console.log('Audio streaming not available:', error);
                        // Update status to show audio is not available
                        audioStatus.innerHTML = '<span>🔇</span><span>No Audio</span>';
                        audioStatus.style.background = 'rgba(239, 68, 68, 0.2)';
                    });
            }
            
            // Start audio when page loads
            window.addEventListener('load', startAudioStream);
        </script>
    </div>
    <div class="footer">{{ timestamp }}</div>
</body>
</html>
"""

UNAUTHORIZED_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Access Denied</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: white;
            text-align: center;
        }
        .box {
            background: rgba(255,255,255,0.1);
            padding: 50px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        h1 { font-size: 4em; margin: 0; }
        h2 { color: #ff6b6b; margin: 20px 0; }
        p { color: #aaa; }
    </style>
</head>
<body>
    <div class="box">
        <h1>🔒</h1>
        <h2>Access Denied</h2>
        <p>Valid token required.</p>
    </div>
</body>
</html>
"""

@app.route('/')
def index_root():
    if not check_auth():
        return UNAUTHORIZED_HTML, 403
    return render_template_string(PAGE_HTML, token=SECRET_TOKEN,
        timestamp=datetime.now().strftime("%B %d, %Y"))

@app.route('/watch/<token>')
def index(token):
    if not check_auth(token):
        return UNAUTHORIZED_HTML, 403
    return render_template_string(PAGE_HTML, token=token,
        timestamp=datetime.now().strftime("%B %d, %Y"))

@app.route('/video_feed')
def video_feed():
    if not check_auth():
        return "Unauthorized", 403
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stream/<token>')
def video_feed_path(token):
    if not check_auth(token):
        return "Unauthorized", 403
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/audio_feed')
def audio_feed():
    if not check_auth():
        return "Unauthorized", 403
    return Response(generate_audio(), mimetype='audio/wav')

@app.route('/audio/<token>')
def audio_feed_path(token):
    if not check_auth(token):
        return "Unauthorized", 403
    return Response(generate_audio(), mimetype='audio/wav')

def run_flask():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=False, threaded=True, use_reloader=False)

def detect_cameras(max_cameras=10):
    """Detect all available cameras"""
    available_cameras = []
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                # Try to get camera name/description
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                camera_info = f"Camera {i} ({width}x{height})"
                available_cameras.append((i, camera_info))
            cap.release()
        else:
            break
    return available_cameras

def audio_callback(indata, frames, time_info, status):
    """Callback function for audio capture"""
    if status:
        print(f"Audio status: {status}")
    # Convert to bytes directly
    audio_queue.put(indata.tobytes())

def start_audio_capture():
    """Start audio capture thread"""
    global audio_stream, audio_thread
    
    try:
        # Try sounddevice first
        audio_stream = sd.InputStream(
            channels=1,
            samplerate=44100,
            dtype='int16',
            callback=audio_callback,
            blocksize=2048
        )
        audio_stream.start()
        print("Audio capture started with sounddevice")
    except Exception as e:
        print(f"Sounddevice audio capture failed: {e}")
        try:
            # Fallback: try with different settings
            audio_stream = sd.InputStream(
                channels=1,
                samplerate=22050,
                dtype='float32',
                callback=audio_callback,
                blocksize=1024
            )
            audio_stream.start()
            print("Audio capture started with sounddevice (fallback)")
        except Exception as e2:
            print(f"Audio capture not available: {e2}")
            print("Continuing without audio - video only mode")
            audio_stream = None

def stop_audio_capture():
    """Stop audio capture"""
    global audio_stream
    if audio_stream:
        audio_stream.stop()
        audio_stream.close()
        audio_stream = None
        print("Audio capture stopped")

def generate_audio():
    """Generate audio stream for Flask"""
    while server_running:
        try:
            audio_data = audio_queue.get(timeout=1.0)
            # For raw PCM data, we need to add WAV header
            # Simple WAV header for 16-bit mono audio
            if len(audio_data) > 0:
                # Create minimal WAV header
                sample_rate = 44100
                channels = 1
                bits_per_sample = 16
                data_size = len(audio_data)
                
                header = b'RIFF'
                header += (36 + data_size).to_bytes(4, 'little')
                header += b'WAVE'
                header += b'fmt '
                header += (16).to_bytes(4, 'little')  # Subchunk1Size
                header += (1).to_bytes(2, 'little')   # AudioFormat (PCM)
                header += channels.to_bytes(2, 'little')
                header += sample_rate.to_bytes(4, 'little')
                header += (sample_rate * channels * bits_per_sample // 8).to_bytes(4, 'little')  # ByteRate
                header += (channels * bits_per_sample // 8).to_bytes(2, 'little')  # BlockAlign
                header += bits_per_sample.to_bytes(2, 'little')
                header += b'data'
                header += data_size.to_bytes(4, 'little')
                
                yield header + audio_data
        except queue.Empty:
            continue


class BabyMonitorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Baby Monitor")
        
        try:
            if os.path.exists("baby_face.ico"):
                self.root.iconbitmap("baby_face.ico")
        except Exception:
            pass
            
        self.root.geometry("460x850")
        self.root.resizable(False, False)
        self.root.configure(bg='#0d1117')
        
        self.qr_photo = None
        self.qr_pil_image = None
        self.is_running = False
        self.local_ip = get_local_ip()
        self.token = None
        self.full_url = None
        self.selected_camera = 0
        self.available_cameras = detect_cameras()
        
        self.center_window()
        self.create_modern_ui()
        
    def center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 230
        y = (self.root.winfo_screenheight() // 2) - 390
        self.root.geometry(f'460x850+{x}+{y}')
    
    def create_modern_ui(self):
        main = tk.Frame(self.root, bg='#0d1117')
        main.pack(fill='both', expand=True, padx=20, pady=15)
        
        header = tk.Frame(main, bg='#0d1117')
        header.pack(fill='x', pady=(0, 12))
        
        title_row = tk.Frame(header, bg='#0d1117')
        title_row.pack()
        
        tk.Label(title_row, text="👶", font=('Segoe UI Emoji', 26), 
                bg='#0d1117', fg='white').pack(side='left')
        
        tk.Label(title_row, text=" Baby Monitor", font=('Segoe UI', 20, 'bold'),
                bg='#0d1117', fg='#58a6ff').pack(side='left')
        
        status_frame = tk.Frame(main, bg='#161b22', pady=10)
        status_frame.pack(fill='x', pady=(0, 10))
        
        status_inner = tk.Frame(status_frame, bg='#161b22')
        status_inner.pack()
        
        self.status_dot = tk.Canvas(status_inner, width=14, height=14, 
                                    bg='#161b22', highlightthickness=0)
        self.status_dot.pack(side='left', padx=(0, 8))
        self.dot_id = self.status_dot.create_oval(2, 2, 12, 12, fill='#f85149', outline='')
        
        self.status_label = tk.Label(status_inner, text="Server Offline", 
                                     font=('Segoe UI', 12, 'bold'),
                                     fg='#f85149', bg='#161b22')
        self.status_label.pack(side='left')
        
        # Camera selection card
        camera_card = tk.Frame(main, bg='#21262d', pady=12, padx=15)
        camera_card.pack(fill='x', pady=(0, 8))
        
        camera_header = tk.Frame(camera_card, bg='#21262d')
        camera_header.pack(fill='x')
        
        tk.Label(camera_header, text="📹 Camera Selection", font=('Segoe UI', 10, 'bold'),
                fg='#58a6ff', bg='#21262d').pack(side='left')
        
        num_cameras = len(self.available_cameras)
        if num_cameras > 0:
            camera_count_text = f"({num_cameras} detected)"
            camera_count_color = '#3fb950' if num_cameras > 1 else '#8b949e'
        else:
            camera_count_text = "(None found)"
            camera_count_color = '#f85149'
        
        tk.Label(camera_header, text=camera_count_text, 
                font=('Segoe UI', 8), fg=camera_count_color, bg='#21262d').pack(side='left', padx=(6, 0))
        
        if num_cameras > 0:
            tk.Label(camera_card, text="Choose which camera to use", 
                    font=('Segoe UI', 8), fg='#6e7681', bg='#21262d').pack(anchor='w', pady=(4, 8))
            
            camera_options = [info for idx, info in self.available_cameras]
            
            style = ttk.Style()
            style.theme_use('clam')
            style.configure('Camera.TCombobox',
                          fieldbackground='#0d1117',
                          background='#21262d',
                          foreground='#58a6ff',
                          arrowcolor='#58a6ff',
                          borderwidth=0,
                          relief='flat')
            style.map('Camera.TCombobox',
                     fieldbackground=[('readonly', '#0d1117')],
                     selectbackground=[('readonly', '#1f6feb')],
                     selectforeground=[('readonly', 'white')])
            
            self.camera_combo = ttk.Combobox(camera_card, values=camera_options,
                                            state='readonly', font=('Segoe UI', 10),
                                            style='Camera.TCombobox')
            self.camera_combo.set(camera_options[0])
            self.camera_combo.pack(fill='x', ipady=4)
            self.camera_combo.bind('<<ComboboxSelected>>', self.on_camera_select)
        else:
            tk.Label(camera_card, text="⚠️ No cameras detected\nPlease connect a webcam", 
                    font=('Segoe UI', 9), fg='#f85149', bg='#21262d',
                    justify='center').pack(pady=8)
        
        ip_card = tk.Frame(main, bg='#21262d', pady=12, padx=15)
        ip_card.pack(fill='x', pady=(0, 8))
        
        tk.Label(ip_card, text="📡 Network IP", font=('Segoe UI', 9),
                fg='#8b949e', bg='#21262d').pack(anchor='w')
        
        self.ip_label = tk.Label(ip_card, text=self.local_ip, 
                                 font=('Consolas', 18, 'bold'),
                                 fg='#3fb950', bg='#21262d')
        self.ip_label.pack(anchor='w', pady=(4, 0))
        
        url_card = tk.Frame(main, bg='#21262d', pady=12, padx=15)
        url_card.pack(fill='x', pady=(0, 8))
        
        tk.Label(url_card, text="🔗 Secure Connection Link", font=('Segoe UI', 9),
                fg='#8b949e', bg='#21262d').pack(anchor='w')
        
        self.url_var = tk.StringVar(value="Start server to generate...")
        self.url_entry = tk.Entry(url_card, textvariable=self.url_var,
                                  font=('Consolas', 9), 
                                  bg='#0d1117', fg='#58a6ff',
                                  relief='flat', state='readonly',
                                  readonlybackground='#0d1117',
                                  selectbackground='#1f6feb')
        self.url_entry.pack(fill='x', pady=(8, 8), ipady=6)
        
        self.copy_btn = tk.Button(url_card, text="📋  Copy Link",
                                  font=('Segoe UI', 9, 'bold'),
                                  bg='#238636', fg='white',
                                  activebackground='#2ea043', activeforeground='white',
                                  relief='flat', cursor='hand2', pady=6,
                                  command=self.copy_url, state='disabled')
        self.copy_btn.pack(fill='x')
        
        qr_card = tk.Frame(main, bg='#21262d', pady=12, padx=15)
        qr_card.pack(fill='x', pady=(0, 8))
        
        qr_header = tk.Frame(qr_card, bg='#21262d')
        qr_header.pack(fill='x')
        
        tk.Label(qr_header, text="📱 Scan QR Code", font=('Segoe UI', 10, 'bold'),
                fg='#f0883e', bg='#21262d').pack(side='left')
        
        tk.Label(qr_card, text="Scan to View Stream", 
                font=('Segoe UI', 8), fg='#6e7681', bg='#21262d').pack(anchor='w')
        
        qr_container = tk.Frame(qr_card, bg='#30363d', padx=2, pady=2)
        qr_container.pack(pady=(10, 8))
        
        self.qr_label = tk.Label(qr_container, text="QR Code will\nappear here",
                                 font=('Segoe UI', 9), fg='#484f58', bg='#0d1117',
                                 width=16, height=7)
        self.qr_label.pack()
        
        self.save_qr_btn = tk.Button(qr_card, text="💾  Save QR Image",
                                     font=('Segoe UI', 9, 'bold'),
                                     bg='#238636', fg='white',
                                     activebackground='#2ea043', activeforeground='white',
                                     relief='flat', cursor='hand2', pady=6,
                                     command=self.save_qr_code, state='disabled')
        self.save_qr_btn.pack(fill='x', pady=(0, 0))
        
        btn_frame = tk.Frame(main, bg='#0d1117', pady=8)
        btn_frame.pack(fill='x')
        
        self.start_btn = tk.Button(btn_frame, text="▶  START",
                                   font=('Segoe UI', 11, 'bold'),
                                   bg='#238636', fg='white',
                                   activebackground='#2ea043', activeforeground='white',
                                   relief='flat', cursor='hand2', pady=12,
                                   command=self.start_server)
        self.start_btn.pack(side='left', expand=True, fill='x', padx=(0, 4))
        
        self.stop_btn = tk.Button(btn_frame, text="⏹  STOP",
                                  font=('Segoe UI', 11, 'bold'),
                                  bg='#30363d', fg='#8b949e',
                                  activebackground='#484f58', activeforeground='white',
                                  relief='flat', cursor='hand2', pady=12,
                                  command=self.stop_server, state='disabled')
        self.stop_btn.pack(side='left', expand=True, fill='x', padx=(4, 0))
        
        self.browser_btn = tk.Button(main, text="🌐  Preview in Browser",
                                     font=('Segoe UI', 10),
                                     bg='#1f6feb', fg='white',
                                     activebackground='#388bfd', activeforeground='white',
                                     relief='flat', cursor='hand2', pady=8,
                                     command=self.open_browser, state='disabled')
        self.browser_btn.pack(fill='x', pady=(4, 8))
        
        tk.Label(main, text="💡 Ensure both devices are on the same WiFi network",
                font=('Segoe UI', 8), fg='#484f58', bg='#0d1117').pack(pady=(10, 0))
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def generate_qr(self):
        """Generate QR code for the URL"""
        if not QR_AVAILABLE or not self.full_url:
            self.qr_label.config(text="Install:\npip install qrcode pillow")
            return
        
        try:
            qr = qrcode.QRCode(
                version=1, 
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=2
            )
            qr.add_data(self.full_url)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="#000000", back_color="#ffffff")
            qr_img = qr_img.convert('RGB')
            
            self.qr_pil_image = qr_img.copy()
            
            qr_display = qr_img.resize((130, 130), Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)
            
            self.qr_photo = ImageTk.PhotoImage(qr_display)
            
            self.qr_label.config(image=self.qr_photo, text='', width=130, height=130)
            
            self.save_qr_btn.config(state='normal')
            
        except Exception as e:
            self.qr_label.config(text=f"QR Error")
            print(f"QR Error: {e}")
    
    def save_qr_code(self):
        """Save QR code as image"""
        if self.qr_pil_image is None:
            messagebox.showwarning("No QR", "Start server first to generate QR code")
            return
        
        try:
            from PIL import ImageDraw, ImageFont
            
            qr_size = self.qr_pil_image.size[0]
            padding = 30
            text_height = 60
            canvas_width = qr_size + (padding * 2)
            canvas_height = qr_size + (padding * 2) + text_height
            
            canvas = Image.new('RGB', (canvas_width, canvas_height), '#ffffff')
            
            canvas.paste(self.qr_pil_image, (padding, padding))
            
            draw = ImageDraw.Draw(canvas)
            
            try:
                title_font = ImageFont.truetype("arial.ttf", 20)
                url_font = ImageFont.truetype("arial.ttf", 11)
            except:
                title_font = ImageFont.load_default()
                url_font = ImageFont.load_default()
            
            title_y = qr_size + padding + 15
            draw.text((canvas_width // 2, title_y), "Baby Monitor", fill='#000000', font=title_font, anchor='mm')
            
            url_y = title_y + 25
            draw.text((canvas_width // 2, url_y), "Scan with phone camera", fill='#666666', font=url_font, anchor='mm')
            
            script_dir = os.path.dirname(os.path.abspath(__file__))
            filename = "BabyMonitor_QR.png"
            filepath = os.path.join(script_dir, filename)
            
            canvas.save(filepath, 'PNG', quality=95)
            
            if os.path.exists(filepath):
                self.save_qr_btn.config(text="✓ Saved!", bg='#1f6feb')
                self.root.after(2000, lambda: self.save_qr_btn.config(text="💾  Save QR Image", bg='#238636'))
                
                import subprocess
                subprocess.run(['explorer', '/select,', filepath])
                
                messagebox.showinfo("✅ QR Saved!", 
                    f"QR Code saved!\n\n"
                    f"📁 Location:\n{filepath}\n\n"
                    f"The folder is now open.\n"
                    f"Share this image with family members.")
            else:
                messagebox.showerror("Error", f"File was not saved!\nTried: {filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save QR:\n{str(e)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not save QR: {e}")
    
    def start_server(self):
        global SECRET_TOKEN, camera, server_running, first_frame
        
        SECRET_TOKEN = secrets.token_urlsafe(10)
        self.token = SECRET_TOKEN
        self.full_url = f"http://{self.local_ip}:{SERVER_PORT}/watch/{SECRET_TOKEN}"
        
        first_frame = None
        
        camera = cv2.VideoCapture(self.selected_camera)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 15)
        
        if not camera.isOpened():
            messagebox.showerror("Camera Error", 
                f"Cannot access camera {self.selected_camera}!\n\nCheck:\n• Webcam connected\n• Not used by another app\n• Try selecting a different camera")
            return
        
        server_running = True
        threading.Thread(target=run_flask, daemon=True).start()
        
        # Start audio capture
        try:
            start_audio_capture()
        except Exception as e:
            print(f"Warning: Audio capture failed: {e}")
        
        self.is_running = True
        
        self.status_dot.itemconfig(self.dot_id, fill='#3fb950')
        self.status_label.config(text="Server Online", fg='#3fb950')
        
        self.url_var.set(self.full_url)
        
        self.start_btn.config(state='disabled', bg='#30363d', fg='#8b949e')
        self.stop_btn.config(state='normal', bg='#da3633', fg='white')
        self.copy_btn.config(state='normal')
        self.browser_btn.config(state='normal')
        self.save_qr_btn.config(state='normal')
        
        self.generate_qr()
        
        messagebox.showinfo("✅ Started!", 
            f"Baby Monitor is running!\n\n"
            f"📱 EASIEST: Scan QR code with mobile device.\n\n"
            f"Or share link:\n{self.full_url}\n\n"
            f"⚠️ Same WiFi network required!")
    
    def stop_server(self):
        global server_running, camera
        
        server_running = False
        self.is_running = False
        
        if camera is not None:
            camera.release()
            camera = None
        
        # Stop audio capture
        stop_audio_capture()
        
        self.status_dot.itemconfig(self.dot_id, fill='#f85149')
        self.status_label.config(text="Server Offline", fg='#f85149')
        
        self.url_var.set("Start server to generate...")
        
        self.start_btn.config(state='normal', bg='#238636', fg='white')
        self.stop_btn.config(state='disabled', bg='#30363d', fg='#8b949e')
        self.copy_btn.config(state='disabled')
        self.browser_btn.config(state='disabled')
        self.save_qr_btn.config(state='disabled')
        
        self.qr_label.config(image='', text="QR Code will\nappear here", width=16, height=7)
        self.qr_photo = None
        self.qr_pil_image = None
        
        messagebox.showinfo("Stopped", "Baby Monitor stopped.\nCamera released.")
    
    def on_camera_select(self, event=None):
        """Handle camera selection change"""
        selected_idx = self.camera_combo.current()
        self.selected_camera = self.available_cameras[selected_idx][0]
    
    def copy_url(self):
        if self.full_url:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.full_url)
            
            orig_text = self.copy_btn.cget('text')
            self.copy_btn.config(text="✓ Copied!", bg='#1f6feb')
            self.root.after(1500, lambda: self.copy_btn.config(text=orig_text, bg='#238636'))
    
    def open_browser(self):
        if self.full_url:
            webbrowser.open(self.full_url)
    
    def on_close(self):
        global server_running, camera
        
        if self.is_running:
            if messagebox.askokcancel("Exit", "Stop server and exit?"):
                server_running = False
                if camera:
                    camera.release()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        self.root.mainloop()


if __name__ == '__main__':
    app_gui = BabyMonitorApp()
    app_gui.run()
