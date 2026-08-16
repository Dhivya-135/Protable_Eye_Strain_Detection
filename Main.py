import cv2
import tkinter as tk
from PIL import Image, ImageTk
import time


# =========================================================
# SETTINGS
# =========================================================

WINDOW_WIDTH = 320
WINDOW_HEIGHT = 330

# Distance calibration
# Approximate values for a normal laptop webcam
KNOWN_FACE_WIDTH = 14.0
FOCAL_LENGTH = 650

# Distance limits
TOO_CLOSE_DISTANCE = 40
GOOD_DISTANCE = 50

# Blink limit
LOW_BLINK_RATE = 8


# =========================================================
# VARIABLES
# =========================================================

cap = None
running = False

blink_count = 0
blink_rate = 0

eye_closed_frames = 0
blink_in_progress = False

start_time = 0

face_detected = False
eyes_detected = False

distance_cm = 0


# =========================================================
# LOAD FACE DETECTOR
# =========================================================

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)


# =========================================================
# LOAD EYE DETECTOR
# =========================================================

eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_eye.xml"
)


# =========================================================
# CHECK CASCADE FILES
# =========================================================

if face_cascade.empty():

    print("ERROR: Face detector not loaded")


if eye_cascade.empty():

    print("ERROR: Eye detector not loaded")


# =========================================================
# DISTANCE CALCULATION
# =========================================================

def calculate_distance(face_width_pixels):

    if face_width_pixels <= 0:

        return 0

    distance = (
        KNOWN_FACE_WIDTH * FOCAL_LENGTH
    ) / face_width_pixels

    return distance


# =========================================================
# OPEN CAMERA
# =========================================================

def open_camera():

    global cap
    global running
    global start_time

    print("Starting webcam...")

    # Try camera 0
    cap = cv2.VideoCapture(
        0,
        cv2.CAP_DSHOW
    )

    if not cap.isOpened():

        print("Camera 0 failed")

        cap.release()

        # Try camera 1
        cap = cv2.VideoCapture(
            1,
            cv2.CAP_DSHOW
        )

    if not cap.isOpened():

        print("Camera 1 failed")
        print("ERROR: No camera found")

        status_label.config(
            text="CAMERA NOT FOUND"
        )

        return

    print("Camera successfully opened")

    # Camera resolution
    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        640
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        480
    )

    running = True

    start_time = time.time()

    status_label.config(
        text="● CAMERA ACTIVE"
    )

    update_camera()


# =========================================================
# CAMERA PROCESSING
# =========================================================

def update_camera():

    global blink_count
    global blink_rate

    global eye_closed_frames
    global blink_in_progress

    global face_detected
    global eyes_detected

    global distance_cm

    if not running:

        return

    # -----------------------------------------------------
    # READ FRAME
    # -----------------------------------------------------

    ret, frame = cap.read()

    if not ret:

        status_label.config(
            text="CAMERA FRAME ERROR"
        )

        root.after(
            100,
            update_camera
        )

        return

    # Mirror image
    frame = cv2.flip(
        frame,
        1
    )

    # -----------------------------------------------------
    # GRAYSCALE
    # -----------------------------------------------------

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    # -----------------------------------------------------
    # FACE DETECTION
    # -----------------------------------------------------

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(80, 80)
    )

    face_detected = len(faces) > 0

    eyes_detected = False

    # -----------------------------------------------------
    # FACE FOUND
    # -----------------------------------------------------

    if face_detected:

        # Select largest face
        x, y, w, h = max(
            faces,
            key=lambda r: r[2] * r[3]
        )

        # -------------------------------------------------
        # DISTANCE
        # -------------------------------------------------

        distance_cm = calculate_distance(w)

        # Face rectangle
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (255, 0, 0),
            2
        )

        # -------------------------------------------------
        # DISTANCE TEXT
        # -------------------------------------------------

        cv2.putText(
            frame,
            "Distance: {:.0f} cm".format(
                distance_cm
            ),
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 255),
            2
        )

        # -------------------------------------------------
        # DISTANCE WARNING
        # -------------------------------------------------

        if distance_cm < TOO_CLOSE_DISTANCE:

            cv2.putText(
                frame,
                "TOO CLOSE!",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        elif distance_cm < GOOD_DISTANCE:

            cv2.putText(
                frame,
                "MOVE BACK",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 165, 255),
                2
            )

        else:

            cv2.putText(
                frame,
                "GOOD DISTANCE",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 0),
                2
            )

        # -------------------------------------------------
        # EYE REGION
        # -------------------------------------------------

        eye_gray = gray[
            y:y + int(h * 0.65),
            x:x + w
        ]

        eye_color = frame[
            y:y + int(h * 0.65),
            x:x + w
        ]

        # -------------------------------------------------
        # EYE DETECTION
        # -------------------------------------------------

        eyes = eye_cascade.detectMultiScale(
            eye_gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(20, 20)
        )

        # -------------------------------------------------
        # FILTER EYES
        # -------------------------------------------------

        valid_eyes = []

        for ex, ey, ew, eh in eyes:

            if ey < h * 0.55:

                valid_eyes.append(
                    (ex, ey, ew, eh)
                )

        # -------------------------------------------------
        # EYES OPEN
        # -------------------------------------------------

        if len(valid_eyes) >= 2:

            eyes_detected = True

            eye_closed_frames = 0

            blink_in_progress = False

            for ex, ey, ew, eh in valid_eyes[:2]:

                cv2.rectangle(
                    eye_color,
                    (ex, ey),
                    (ex + ew, ey + eh),
                    (0, 255, 0),
                    2
                )

        # -------------------------------------------------
        # POSSIBLE BLINK
        # -------------------------------------------------

        else:

            eye_closed_frames += 1

            if eye_closed_frames >= 3:

                if not blink_in_progress:

                    blink_count += 1

                    blink_in_progress = True

        # -------------------------------------------------
        # BLINK RATE
        # -------------------------------------------------

        elapsed = time.time() - start_time

        if elapsed >= 5:

            blink_rate = int(
                blink_count /
                (elapsed / 60)
            )

    # -----------------------------------------------------
    # NO FACE
    # -----------------------------------------------------

    else:

        distance_cm = 0

        eyes_detected = False

        eye_closed_frames = 0

        blink_in_progress = False

    # =====================================================
    # CAMERA TEXT
    # =====================================================

    cv2.putText(
        frame,
        "Blinks: {}".format(
            blink_count
        ),
        (10, 95),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        "Rate: {}/min".format(
            blink_rate
        ),
        (10, 125),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )

    # =====================================================
    # CONVERT IMAGE
    # =====================================================

    frame_rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    image = Image.fromarray(
        frame_rgb
    )

    # SMALL CAMERA
    image = image.resize(
        (280, 180)
    )

    photo = ImageTk.PhotoImage(
        image=image
    )

    # Display
    camera_label.config(
        image=photo,
        text=""
    )

    camera_label.image = photo

    # =====================================================
    # UPDATE INFORMATION
    # =====================================================

    blink_label.config(
        text="Blinks : {}".format(
            blink_count
        )
    )

    rate_label.config(
        text="Rate : {}/min".format(
            blink_rate
        )
    )

    # -----------------------------------------------------
    # FACE STATUS
    # -----------------------------------------------------

    if face_detected:

        face_label.config(
            text="Face : ✓"
        )

    else:

        face_label.config(
            text="Face : ✗"
        )

    # -----------------------------------------------------
    # EYE STATUS
    # -----------------------------------------------------

    if eyes_detected:

        eye_label.config(
            text="Eyes : OPEN"
        )

    else:

        eye_label.config(
            text="Eyes : CLOSED"
        )

    # -----------------------------------------------------
    # DISTANCE STATUS
    # -----------------------------------------------------

    if distance_cm > 0:

        distance_label.config(
            text="Distance : {:.0f} cm".format(
                distance_cm
            )
        )

        if distance_cm < TOO_CLOSE_DISTANCE:

            distance_status.config(
                text="⚠ TOO CLOSE"
            )

        elif distance_cm < GOOD_DISTANCE:

            distance_status.config(
                text="Move Back"
            )

        else:

            distance_status.config(
                text="✓ Good Distance"
            )

    else:

        distance_label.config(
            text="Distance : --"
        )

        distance_status.config(
            text=""
        )

    # =====================================================
    # EYE STRAIN STATUS
    # =====================================================

    if not face_detected:

        strain_label.config(
            text="Eye Status : Waiting"
        )

    elif distance_cm < TOO_CLOSE_DISTANCE:

        strain_label.config(
            text="Eye Status : TOO CLOSE"
        )

    elif blink_rate > 0 and blink_rate < LOW_BLINK_RATE:

        strain_label.config(
            text="Eye Status : CAUTION"
        )

    else:

        strain_label.config(
            text="Eye Status : NORMAL"
        )

    # =====================================================
    # CONTINUE
    # =====================================================

    root.after(
        30,
        update_camera
    )


# =========================================================
# CLOSE CAMERA
# =========================================================

def close_camera():

    global running
    global cap

    running = False

    print("Closing camera...")

    if cap is not None:

        cap.release()

        cap = None

    root.destroy()


# =========================================================
# TKINTER WINDOW
# =========================================================

root = tk.Tk()

root.title(
    "Eye Monitor"
)


# =========================================================
# SMALL WINDOW SIZE
# =========================================================

WINDOW_WIDTH = 320
WINDOW_HEIGHT = 330


# Get screen size
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()


# Bottom-right position
x_position = (
    screen_width -
    WINDOW_WIDTH -
    15
)

y_position = (
    screen_height -
    WINDOW_HEIGHT -
    60
)


root.geometry(
    "{}x{}+{}+{}".format(
        WINDOW_WIDTH,
        WINDOW_HEIGHT,
        x_position,
        y_position
    )
)


# Don't allow resizing
root.resizable(
    False,
    False
)


# Keep window above other windows
root.attributes(
    "-topmost",
    True
)


# =========================================================
# TITLE
# =========================================================

title = tk.Label(
    root,
    text="👁 EYE STRAIN MONITOR",
    font=("Arial", 12, "bold")
)

title.pack(
    pady=4
)


# =========================================================
# CAMERA DISPLAY
# =========================================================

camera_label = tk.Label(
    root,
    text="Starting Camera...",
    width=280,
    height=180,
    bg="black",
    fg="white"
)

camera_label.pack(
    pady=2
)


# =========================================================
# CAMERA STATUS
# =========================================================

status_label = tk.Label(
    root,
    text="STARTING CAMERA...",
    font=("Arial", 9, "bold")
)

status_label.pack(
    pady=2
)


# =========================================================
# DATA FRAME
# =========================================================

info_frame = tk.Frame(
    root
)

info_frame.pack(
    pady=2
)


# Blink count
blink_label = tk.Label(
    info_frame,
    text="Blinks : 0",
    font=("Arial", 9)
)

blink_label.grid(
    row=0,
    column=0,
    padx=8
)


# Blink rate
rate_label = tk.Label(
    info_frame,
    text="Rate : 0/min",
    font=("Arial", 9)
)

rate_label.grid(
    row=0,
    column=1,
    padx=8
)


# Face
face_label = tk.Label(
    info_frame,
    text="Face : ✗",
    font=("Arial", 9)
)

face_label.grid(
    row=1,
    column=0,
    padx=8,
    pady=2
)


# Eyes
eye_label = tk.Label(
    info_frame,
    text="Eyes : --",
    font=("Arial", 9)
)

eye_label.grid(
    row=1,
    column=1,
    padx=8,
    pady=2
)


# =========================================================
# DISTANCE
# =========================================================

distance_label = tk.Label(
    root,
    text="Distance : --",
    font=("Arial", 9, "bold")
)

distance_label.pack(
    pady=1
)


distance_status = tk.Label(
    root,
    text="",
    font=("Arial", 9, "bold")
)

distance_status.pack(
    pady=1
)


# =========================================================
# EYE STATUS
# =========================================================

strain_label = tk.Label(
    root,
    text="Eye Status : --",
    font=("Arial", 9, "bold")
)

strain_label.pack(
    pady=2
)


# =========================================================
# CLOSE BUTTON
# =========================================================

close_button = tk.Button(
    root,
    text="CLOSE",
    width=8,
    font=("Arial", 8, "bold"),
    command=close_camera
)

close_button.pack(
    pady=3
)


# =========================================================
# WINDOW CLOSE BUTTON
# =========================================================

root.protocol(
    "WM_DELETE_WINDOW",
    close_camera
)


# =========================================================
# START CAMERA
# =========================================================

root.after(
    500,
    open_camera
)


# =========================================================
# START TKINTER
# =========================================================

root.mainloop()
