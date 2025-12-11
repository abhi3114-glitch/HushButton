# HushButton

HushButton is a desktop utility that allows users to toggle their system audio or microphone mute status by flashing a light (such as a smartphone flashlight) at their webcam. It is designed to provide a hands-free, visual way to control audio during calls or streams.

## Features

- **Flash Detection**: Uses computer vision to detect sudden increases in brightness (saturated pixels) from a webcam feed.
- **Pattern Recognition**:
    - **Single Flash**: Mutes the target device. shows a red "MUTED" status.
    - **Double Flash**: Unmutes the target device. shows a green "LIVE" status.
- **Device Selection**: Users can select specific audio input (Microphone) or output (Speakers) devices to control from a dropdown list.
- **Adjustable Sensitivity**: A slider allows users to set the threshold for flash detection, effectively filtering out ambient light.
- **Live Feedback**: Real-time display of the current "Flash Score" (pixel count) helps in calibrating the threshold.
- **Privacy Focused**: No video is recorded or stored. Images are processed in-memory solely for brightness calculation and are discarded immediately.

## Tech Stack

- **Language**: Python 3.11+
- **GUI Framework**: Tkinter
- **Computer Vision**: OpenCV (cv2)
- **Audio Control**: pycaw (Python Core Audio Windows Library)

## Installation

### Prerequisites

- Windows OS (Required for pycaw/Waitable Timer APIs)
- Python 3.11 or higher
- A working Webcam

### Setup

1.  Clone this repository or download the source code.
2.  Open a terminal in the project directory.
3.  Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

    *Note: If you encounter installation errors with numpy or pycaw, ensure you are using a compatible Python version (3.11 recommended).*

## Usage

1.  Run the application:

    ```bash
    python main.py
    ```

    *If using the Python Launcher on Windows:*
    ```bash
    py -3.11 main.py
    ```

2.  **Configuration**:
    - **Target Device**: Use the dropdown menu to select the microphone or speaker you wish to control.
    - **Sensitivity**: Observe the "Current Score" value when the room is lit normally. Move the "Flash Size Threshold" slider so it is slightly higher than this resting score.
    - **Test**: Shine your flashlight at the camera. The blue progress bar should fill up, and the status should change.

3.  **Operation**:
    - **Mute**: Flash the light ONCE.
    - **Unmute**: Flash the light TWICE rapidly.

## Troubleshooting

- **App crashes on start**: Ensure you are using Python 3.11 for compatibility with the audio libraries.
- **Audio not changing**: Verify the correct device is selected in the "Target Device" dropdown. If the specific device driver is not compatible, the app may fall back to "Simulation Mode" (indicated in the console), where it updates the UI but cannot toggle the actual hardware mute.
- **False Positives**: If the app triggers without a flashlight, increase the "Flash Size Threshold". Avoid having moving bright objects or windows directly behind you.
- **Not Detecting Flash**: Decrease the threshold. Ensure the flashlight is pointed directly at the camera lens.

## License

This project is open source.
