#!/usr/bin/env python3
"""
Audio Test Script for Baby Monitor
"""
import sounddevice as sd
import numpy as np
import time
import queue

# Test audio capture
audio_queue = queue.Queue()

def audio_callback(indata, frames, time_info, status):
    if status:
        print(f"Audio status: {status}")
    # Convert to bytes directly
    audio_queue.put(indata.tobytes())
    print(f"Captured {len(indata)} audio samples")

def test_audio():
    print("Testing audio capture...")
    print("Available audio devices:")
    devices = sd.query_devices()
    print(devices)
    
    # Find input devices
    input_devices = []
    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            input_devices.append((i, device['name']))
            print(f"Input device {i}: {device['name']}")
    
    if not input_devices:
        print("No input devices found!")
        return
    
    try:
        # Try to use the first available input device
        device_index = input_devices[0][0]
        
        # Start audio stream
        stream = sd.InputStream(
            device=device_index,
            channels=1,  # Mono audio
            samplerate=44100,  # Standard sample rate
            dtype='int16',  # 16-bit signed integer
            callback=audio_callback,
            blocksize=2048  # Larger block size
        )

        print(f"Starting audio capture for 3 seconds using device {device_index}...")
        stream.start()

        # Capture for 3 seconds
        time.sleep(3)

        stream.stop()
        stream.close()

        print("Audio test completed successfully!")
        print(f"Captured audio data: {audio_queue.qsize()} chunks")

    except Exception as e:
        print(f"Audio test failed: {e}")
        # Try with default device and different settings
        try:
            print("Trying with default device and alternative settings...")
            stream = sd.InputStream(
                channels=1,
                samplerate=22050,
                dtype='float32',
                callback=audio_callback,
                blocksize=1024
            )
            stream.start()
            time.sleep(2)
            stream.stop()
            stream.close()
            print("Alternative settings worked!")
        except Exception as e2:
            print(f"Even alternative settings failed: {e2}")

if __name__ == "__main__":
    test_audio()