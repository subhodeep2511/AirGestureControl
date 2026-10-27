# AirControl 🖐️

**Control your Windows mouse using hand gestures and your laptop's webcam.**

AirControl is a Python-based project that lets you interact with your computer without physically touching a mouse. It uses a webcam to track hand movements and recognizes gestures to perform actions such as moving the cursor, clicking, dragging files, and scrolling.

The idea behind this project is simple: use computer vision to make everyday desktop interaction more natural and hands-free.

## ✨ Features

- **Cursor Movement** — Move the system cursor using your index finger.
- **Left Click** — Use a thumb-and-index-finger pinch gesture.
- **Right Click** — Trigger a right-click using a closed-fist gesture.
- **Drag and Drop** — Hold a pinch gesture to drag files and other items.
- **Gesture-Based Scrolling** — Use two-finger gestures to scroll through pages.
- **Real-Time Hand Tracking** — Detect hand landmarks through your webcam.
- **Pause and Resume** — Temporarily disable gesture control using a keyboard shortcut.

*Note: Gesture recognition and scrolling reliability are still being improved.*

## 🛠️ Tech Stack

- **Python** — Core application logic
- **OpenCV** — Webcam access and image processing
- **MediaPipe** — Hand landmark detection and tracking
- **PyAutoGUI** — System mouse and keyboard interaction

## ⚙️ How It Works

AirControl processes the webcam feed in real time and uses hand landmarks to determine the user's gestures.

```text
Webcam Feed
     |
     v
OpenCV - Capture and Process Frames
     |
     v
MediaPipe - Detect Hand Landmarks
     |
     v
Gesture Recognition
     |
     v
Mouse Control with PyAutoGUI
     |
     v
Windows Desktop Interaction
```

## 📋 Requirements

- Windows 10 or Windows 11
- Python version compatible with your installed MediaPipe package
- A working webcam
- Adequate lighting for hand tracking

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/AirControl.git
cd AirControl
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

If the project contains a `requirements.txt` file:

```powershell
pip install -r requirements.txt
```

Otherwise, install the required packages:

```powershell
pip install mediapipe opencv-contrib-python pyautogui
```

Use the dependency versions tested with your project, especially for MediaPipe.

### 4. Add the hand-tracking model

The application uses the MediaPipe Hand Landmarker model.

Download the compatible `hand_landmarker.task` model from the official MediaPipe documentation:

https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker

Place the model in the location expected by the Python script. In the current prototype, this is the project directory.

### 5. Run the application

If your script is named `air_mouse.py`, run:

```powershell
python air_mouse.py
```

Allow camera access if Windows requests permission.

## 🖐️ Gesture Controls

The current prototype uses the following gestures:

| Gesture | Action |
|---|---|
| Index finger extended | Move cursor |
| Thumb and index finger pinch | Left click |
| Hold thumb and index finger pinched | Drag and drop |
| Closed fist | Right click |
| Index and middle fingers extended | Swipe-based scrolling |

Gesture assignments and recognition behavior may change as the project develops.

## ⌨️ Keyboard Shortcuts

| Key | Action |
|---|---|
| `P` | Pause or resume gesture control |
| `Q` | Quit the application |

## 🔧 Troubleshooting

**Camera not opening**

- Close other applications that may be using the webcam.
- Check Windows camera permissions.
- If necessary, try another camera index in the script.

**Hand gestures are not detected correctly**

- Improve lighting and keep your hand inside the camera frame.
- Avoid placing your hand too close to the camera.
- Keep your fingers clearly separated when performing gestures.

**Scrolling does not work as expected**

- Check whether the application recognizes the scrolling gesture.
- Try scrolling in a normal, scrollable window.
- Scrolling behavior is still under development.

**MediaPipe import errors**

- Verify that the installed MediaPipe version supports the API used by the script.
- Activate the correct virtual environment before installing dependencies.
- Avoid mixing incompatible Python and package versions.

## 🗺️ Future Improvements

AirControl is an ongoing personal project. Planned improvements include:

- More reliable gesture recognition and conflict resolution
- Smoother cursor movement and more consistent scrolling
- A desktop GUI with enable/disable controls
- Adjustable sensitivity and gesture calibration
- Performance monitoring and error logging
- Automated tests for gesture recognition
- Packaging as a standalone Windows application

## 🔒 Safety and Limitations

AirControl generates real mouse events on your computer. Incorrectly detected gestures can trigger unintended clicks or drag operations.

Use it carefully, save your work before testing, and keep a reliable way to regain normal mouse control. Avoid using it for sensitive actions until its reliability has been thoroughly tested.

The current version is a prototype and is not intended to replace a conventional mouse in every situation.

## 👨‍💻 Author

**Subhodeep Sarkar**

MCA Student | Interested in Python, Computer Vision, AI and Software Development

## 📄 License

This project is currently a personal learning project. A license can be added when the repository is published.

---

If you find the project interesting, feel free to explore the code and follow its development.
