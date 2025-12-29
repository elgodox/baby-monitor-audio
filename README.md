# 👶 Baby Monitor

Turn your computer's webcam into a secure baby monitor. This application streams live video to any device on your local WiFi network (phones, tablets, laptops) without sending data to the cloud.

![Baby Monitor Interface](baby_face.ico)

## Features

- **Local & Secure**: Streams video directly over your home WiFi. No internet or cloud servers involved.
- **Works on Any Device**: Watch the stream in any web browser on iOS, Android, or PC.
- **Motion Detection**: Visual alerts when movement is detected in the frame.
- **Dark Mode**: Interface designed to be easy on the eyes in dark rooms.
- **Easy Connection**: Scan a QR code to connect your phone instantly.
- **Private**: Uses unique session tokens to ensure only you can access the feed.

## Prerequisites

- Python 3.6 or higher
- A webcam connected to your computer
- A local WiFi network (both computer and viewing device must be on the same network)

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Recentlystarted/baby-monitor.git
    cd baby-monitor
    ```

2.  **Install dependencies**:
    ```bash
    pip install opencv-python flask pillow qrcode
    ```

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

**Dedicated to [CodeWithHarry](https://www.codewithharry.com/)** 

I am a proud student of the CodeWithHarry community. This project was built using concepts and inspiration gained from his amazing tutorials. Thank you, Harry Bhai, for being an incredible mentor and making programming accessible to everyone! 

## Support

If you find this project useful, you can support its development:

<a href="https://buymeacoffee.com/3lineofcodd" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

Or simply star ⭐ this repository to show your support!
