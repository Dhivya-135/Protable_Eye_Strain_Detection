👁️** Portable Digital Eye Strain Detector **

📌 ** Overview **

The Portable Digital Eye Strain Detector is a Python-based computer vision application designed to monitor basic indicators related to digital eye strain during computer usage. The system uses a webcam to detect the user's face and eyes, count blinks, calculate blink rate, and estimate the distance between the user and the camera.

The results are displayed through a small Tkinter window positioned at the bottom-right corner of the screen, allowing the user to continue using the computer while monitoring their eye-related behavior.

🎯** Objectives **
Detect the user's face using a webcam.
Detect the user's eyes in real time.
Count eye blinks.
Calculate approximate blink rate per minute.
Estimate the user's distance from the screen.
Warn the user when they are too close to the screen.
Display an overall eye-status message.
Provide a compact and user-friendly monitoring interface.
🛠️ ** Technologies Used **
Python
OpenCV
Tkinter
Pillow (PIL)

The code imports OpenCV, Tkinter, Pillow, and Python's time module.

🔧 ** Hardware Requirements **
Laptop/Desktop
Built-in or external webcam

No Raspberry Pi or additional sensor is required for the current version.

💻 ** Software Requirements **
Windows 10/11
Python 3.10 recommended
Thonny / VS Code / Python IDLE
Webcam access
📦 ** Installation **

Install the required Python libraries:

pip install opencv-python
pip install pillow

Tkinter normally comes with Python on Windows.

📂 ** Project Structure **
Portable-Eye-Strain-Detector/
│
├── eye_strain_detector.py
└── README.md
🔄 ** Working Principle **

The system follows this process:

              START
                ↓
          Start Webcam
                ↓
        Capture Video Frame
                ↓
          Detect Face
                ↓
          Detect Eyes
                ↓
       Count Eye Blinks
                ↓
       Calculate Blink Rate
                ↓
       Estimate Face Distance
                ↓
       Check Eye Condition
                ↓
       Display Result in GUI
                ↓
          Continue Monitoring
👤 Face Detection

The project uses OpenCV's built-in Haar Cascade classifier:

haarcascade_frontalface_default.xml

The detector searches each camera frame for faces. The largest detected face is selected for monitoring.

👁️ Eye Detection

After detecting the face, the program extracts the upper portion of the face region and uses:

haarcascade_eye.xml

to detect the eyes. Two valid detected eyes are treated as an open-eye condition.

😉 Blink Detection

The current code uses consecutive eye-detection failures to identify a possible blink.

The logic is:

Eyes detected
     ↓
Eyes open
     ↓
Eye detection temporarily disappears
     ↓
Count closed frames
     ↓
3 or more frames
     ↓
Count one blink

The code requires at least 3 consecutive frames without valid eye detection before counting a blink. A blink_in_progress flag prevents the same closed-eye period from being counted repeatedly.

Note: This is a simple prototype method. It is not as accurate as EAR-based facial-landmark blink detection, so lighting, glasses, camera angle, and eye visibility can affect the result.

📊 Blink Rate

The program calculates an approximate blink rate using the total blink count and elapsed monitoring time:

blink_rate = int(
    blink_count /
    (elapsed / 60)
)

The calculation begins after at least five seconds of monitoring.

📏 Distance Measurement

The program estimates the user's distance from the camera using the detected face width.

The calculation is:

Distance =
(Known Face Width × Focal Length)
---------------------------------
      Face Width in Pixels

The current code uses:

KNOWN_FACE_WIDTH = 14.0
FOCAL_LENGTH = 650

as approximate calibration values.

The distance should therefore be considered an approximate estimate, not an accurate physical measurement.

⚠️ Distance Warning

The system uses two distance thresholds:

TOO_CLOSE_DISTANCE = 40
GOOD_DISTANCE = 50

The application displays:

Distance	Message
Below 40 cm	⚠️ TOO CLOSE
40–50 cm	Move Back
Above 50 cm	✓ Good Distance

This logic is implemented directly in the camera-processing section.

🚦 Eye Status

The application provides three basic states:

🟢 NORMAL

The user is detected and the estimated distance is acceptable.

🟡 CAUTION

The detected blink rate is below the configured threshold.

LOW_BLINK_RATE = 8

🔴 TOO CLOSE

The estimated distance is below the configured close-distance threshold.

The status logic is implemented in the Tkinter interface.

🖥️ Tkinter Interface

The application uses a compact:

320 × 330 pixels

window. It is automatically positioned near the bottom-right corner of the screen and cannot be resized.

The window is also configured to remain above other applications:

root.attributes("-topmost", True)

Dashboard Displays

** The GUI displays: **

Live camera
Camera status
Blink count
Blink rate
Face detection status
Eye status
Distance
Distance warning
Eye status
Close button

These interface elements are defined in the Tkinter section of the code.

📷 Camera Handling

The program first attempts to open:

camera 0

If camera 0 fails, it attempts:

camera 1

The camera resolution is set to:

640 × 480

▶️ How to Run
Using Thonny
Open Thonny.
Open eye_strain_detector.py.
Make sure your webcam is connected.
Save the file.
Click Run ▶.
The camera starts automatically.
The small monitoring window appears at the bottom-right corner.
Click CLOSE to stop the camera and application.
📌 ** Expected Output **
┌──────────────────────────────┐
│   👁 EYE STRAIN MONITOR      │
│                              │
│      [ LIVE CAMERA ]         │
│                              │
│ ● CAMERA ACTIVE              │
│                              │
│ Blinks : 5   Rate : 10/min  │
│ Face : ✓     Eyes : OPEN     │
│                              │
│ Distance : 55 cm             │
│ ✓ Good Distance              │
│                              │
│ Eye Status : NORMAL          │
│                              │
│          [ CLOSE ]           │
└──────────────────────────────┘
🌟 Advantages
Low-cost solution
Uses an existing webcam
No external hardware required
Simple Python implementation
Real-time monitoring
Small and non-intrusive interface
Easy to modify and extend
⚠️ Limitations
Blink detection depends on Haar Cascade eye detection.
Poor lighting can affect detection.
Glasses may affect eye detection.
Distance measurement is approximate.
Webcam position affects distance estimation.
Blink rate is only a basic indicator and does not medically diagnose eye strain.
The current version does not measure ambient light.
🔮 Future Improvements

The project can be improved by adding:

EAR-based blink detection for better accuracy
Ambient light sensor
Automatic screen brightness adjustment
Break reminders
Eye-strain history
CSV/database logging
Mobile notifications
Posture detection
Machine-learning-based fatigue prediction
Personalized user thresholds
📜 ** Disclaimer **

This project is an educational prototype for digital wellness monitoring. It is not a medical device and should not be used to diagnose or treat eye diseases.

👩‍💻 ** Project Summary **

Portable Digital Eye Strain Detector combines computer vision and a lightweight graphical interface to monitor blink behavior and approximate screen distance using only a webcam. The system provides real-time feedback through a compact Tkinter application and can be further extended with more advanced eye-tracking, lighting, and AI-based features.