# 👶 Baby Monitor with Audio & Multi-Camera Support

**Enhanced Fork** - Turn your computer's webcam into a secure baby monitor with **real-time audio streaming** and **automatic multi-camera detection**. This application streams live video AND audio to any device on your local WiFi network (phones, tablets, laptops) without sending data to the cloud.

**🎤 Audio + 📹 Multi-Camera = Complete Baby Monitoring Solution!**

![Baby Monitor Interface](baby_face.ico)

## Features

- **Local & Secure**: Streams video directly over your home WiFi. No internet or cloud servers involved.
- **🎤 Real-Time Audio Streaming**: Captures and streams audio from your microphone using sounddevice - hear your baby clearly!
- **📹 Multi-Camera Detection**: Automatically detects all connected cameras and lets you choose which one to use.
- **🔄 Dynamic Device Selection**: Switch between cameras and audio devices without restarting.
- **📱 Works on Any Device**: Watch the stream in any web browser on iOS, Android, or PC.
- **🚨 Motion Detection**: Visual alerts when movement is detected in the frame.
- **🌙 Dark Mode UI**: Interface designed to be easy on the eyes in dark rooms.
- **📲 Easy Connection**: Scan a QR code to connect your phone instantly.
- **🔐 Private & Secure**: Uses unique session tokens to ensure only you can access the feed.
- **⚡ Graceful Fallbacks**: Works perfectly even if audio or certain cameras aren't available.

## Prerequisites

- Python 3.6 or higher
- A webcam connected to your computer
- **Recommended: A microphone or audio input device** - For complete baby monitoring experience
- A local WiFi network (both computer and viewing device must be on the same network)

**Note**: Audio is now a core feature, but the app works perfectly with video-only if no microphone is available.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/elgodox/baby-monitor-audio.git
    cd baby-monitor-audio
    ```

2.  **Install dependencies**:
    ```bash
    pip install opencv-python flask qrcode pillow sounddevice numpy
    ```

    Or use the requirements file:
    ```bash
    pip install -r requirements.txt
    ```

## 🚀 New Features in This Fork

This fork enhances the original Baby Monitor with the following improvements:

### 🎤 Audio Streaming
- **Real-time audio capture** using `sounddevice` library (modern alternative to PyAudio)
- **Web Audio API integration** for streaming audio to web browsers
- **Optional audio** - works perfectly even without microphone
- **Visual audio status** indicators in the web interface
- **Graceful fallback** when audio is not available

### 📹 Multi-Camera Support
- **Automatic camera detection** - finds all connected cameras
- **Camera selection interface** - choose which camera to use
- **Resolution display** - shows camera capabilities (e.g., "Camera 0 (640x480)")
- **Dynamic camera switching** - change cameras without restarting

### 🔧 Technical Improvements
- **Updated dependencies** with `requirements.txt`
- **Better error handling** for audio/camera issues
- **Cleaner code structure** and documentation
- **Cross-platform compatibility** improvements

### 📱 Enhanced User Experience
- **Modern UI indicators** for audio status
- **Comprehensive device detection**
- **Robust connection handling**
- **Better user feedback** and error messages
      2. Direct `pip install pyaudio`
      3. Download appropriate wheel file from [Unofficial Windows Binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install:
         ```bash
         pip install PyAudio‑0.2.11‑cp311‑cp311‑win_amd64.whl
         ```
         (Replace with your Python version)

    - **macOS**:
      ```bash
      brew install portaudio
      pip install pyaudio
      ```

    - **Linux**:
      ```bash
      sudo apt-get install portaudio19-dev
      pip install pyaudio
      ```

4.  **Verify installation**:
    ```bash
    python check_dependencies.py
    ```
    This will check all dependencies and attempt to install PyAudio if missing.

## Usage

1.  **Check dependencies first**:
    ```bash
    python check_dependencies.py
    ```

2.  **Start the application**:
    Double-click `BabyMonitor.pyw` or run via terminal:
    ```bash
    python BabyMonitor.pyw
    ```

3.  **Select your devices**:
    - Choose which camera to use from the dropdown menu
    - The app will automatically detect available cameras and microphones
    - Audio streaming starts automatically when available

4.  **Start Monitoring**:
    Click the **▶ START** button in the application.

5.  **Monitor the Status**:
    - **🟢 Green indicators** show active video and audio streaming
    - **🔴 Red indicators** show when devices aren't available
    - **📊 Status bar** shows connection and device information

5.  **Connect a Device**:
    - **Option A (Easiest)**: Scan the QR code displayed in the app with your phone's camera.
    - **Option B**: Type the "Network IP" address shown in the app into your phone's browser.
    - **Option C**: Click "Copy Link" and send it to yourself via email or messaging app.

## Usage

1.  **Start the application**:
    Double-click `BabyMonitor.pyw` or run via terminal:
    ```bash
    python BabyMonitor.pyw
    ```

2.  **Start Monitoring**:
    Click the **▶ START** button in the application.

3.  **Connect a Device**:
    - **Option A (Easiest)**: Scan the QR code displayed in the app with your phone's camera.
    - **Option B**: Type the "Network IP" address shown in the app into your phone's browser.
    - **Option C**: Click "Copy Link" and send it to yourself via email or messaging app.

4.  **Stop Monitoring**:
    Click **⏹ STOP** to end the session and turn off the camera.

## Disclaimer

This software is designed as a supplementary monitoring tool and **is not a replacement for direct parental supervision**. Always ensure you can hear or see your child physically. The developer assumes no liability for any reliance on this software.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎓 Acknowledgments

**Forked from [Recentlystarted/baby-monitor](https://github.com/Recentlystarted/baby-monitor)**

This project is a fork of the original Baby Monitor by Recentlystarted, enhanced with audio streaming and multi-camera support.

**Original project dedicated to [CodeWithHarry](https://www.codewithharry.com/)**

The original project was built using concepts and inspiration gained from CodeWithHarry's amazing tutorials. Thank you for making programming accessible to everyone!

**Audio enhancements by elgodox**

Added audio streaming capabilities using sounddevice library and multi-camera detection for enhanced baby monitoring experience. 

## Support

If you find this project useful, you can support its development by starring ⭐ this repository!

**Original project support:**
<a href="https://buymeacoffee.com/3lineofcodd" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

**Fork enhancements:**
This fork adds audio streaming and multi-camera support. Feel free to contribute improvements!
