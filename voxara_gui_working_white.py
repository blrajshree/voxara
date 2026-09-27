import tkinter as tk
from tkinter import ttk
import cv2
import mediapipe as mp
import joblib
import speech_recognition as sr
import time
import threading
import queue
import win32com.client

from PIL import Image, ImageTk
from collections import deque, Counter


# =========================================================
# VOXARA
# TWO-WAY COMMUNICATION SYSTEM
# =========================================================


# =========================================================
# MODEL
# =========================================================

MODEL_PATH = r"E:\voxara\training\voxara_model.pkl"

model = joblib.load(MODEL_PATH)


# =========================================================
# SPEECH OUTPUT - ISL TO SPEECH
# =========================================================

speech_queue = queue.Queue()


def speech_worker():

    speaker = win32com.client.Dispatch("SAPI.SpVoice")

    speaker.Rate = 0
    speaker.Volume = 100

    while True:

        text = speech_queue.get()

        if text is None:
            break

        try:

            print("🔊 Speaking:", text)

            speaker.Speak(text)

            print("✓ Speech completed:", text)

        except Exception as error:

            print("Speech error:", error)

        speech_queue.task_done()


speech_thread = threading.Thread(
    target=speech_worker,
    daemon=True
)

speech_thread.start()


# =========================================================
# MEDIAPIPE
# =========================================================

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)


# =========================================================
# CAMERA VARIABLES
# =========================================================

cap = None

camera_running = False

prediction_history = deque(maxlen=7)

last_confirmed_sign = ""

last_speech_time = 0

speech_cooldown = 1.5

CONFIDENCE_THRESHOLD = 0.60


# =========================================================
# SPEECH TO TEXT VARIABLES
# =========================================================

recognizer = sr.Recognizer()

speech_running = False

speech_thread_stt = None

language_codes = {
    "English": "en-IN",
    "Tamil": "ta-IN",
    "Hindi": "hi-IN",
    "Telugu": "te-IN"
}


# =========================================================
# MAIN WINDOW
# =========================================================

root = tk.Tk()

root.title("Voxara - Two-Way Communication System")

root.geometry("1200x800")

root.minsize(1000, 700)


# =========================================================
# TITLE
# =========================================================

title = tk.Label(
    root,
    text="VOXARA",
    font=("Arial", 30, "bold")
)

title.pack(pady=(15, 2))


subtitle = tk.Label(
    root,
    text="Two-Way Communication System",
    font=("Arial", 14)
)

subtitle.pack(pady=(0, 12))


# =========================================================
# MAIN FRAME
# =========================================================

main_frame = tk.Frame(root)

main_frame.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=5
)


# =========================================================
# LEFT SIDE
# ISL → SPEECH
# =========================================================

left_frame = tk.LabelFrame(
    main_frame,
    text="  ISL → SPEECH  ",
    font=("Arial", 14, "bold")
)

left_frame.pack(
    side="left",
    fill="both",
    expand=True,
    padx=8
)


# =========================================================
# CAMERA DISPLAY
# =========================================================

camera_label = tk.Label(
    left_frame,
    text="📷\n\nCamera Preview\n\nPress START CAMERA",
    font=("Arial", 16),
    width=50,
    height=17
)

camera_label.pack(
    padx=10,
    pady=10
)


# =========================================================
# SIGN RESULT
# =========================================================

sign_label = tk.Label(
    left_frame,
    text="Recognized Sign: ---",
    font=("Arial", 17, "bold")
)

sign_label.pack(pady=5)


confidence_label = tk.Label(
    left_frame,
    text="Confidence: ---",
    font=("Arial", 13)
)

confidence_label.pack(pady=3)


# =========================================================
# CAMERA BUTTONS
# =========================================================

camera_button_frame = tk.Frame(left_frame)

camera_button_frame.pack(pady=10)


start_camera_button = tk.Button(
    camera_button_frame,
    text="START CAMERA",
    font=("Arial", 11, "bold"),
    width=16
)

start_camera_button.pack(
    side="left",
    padx=5
)


stop_camera_button = tk.Button(
    camera_button_frame,
    text="STOP CAMERA",
    font=("Arial", 11, "bold"),
    width=16
)

stop_camera_button.pack(
    side="left",
    padx=5
)


# =========================================================
# RIGHT SIDE
# SPEECH → TEXT
# =========================================================

right_frame = tk.LabelFrame(
    main_frame,
    text="  SPEECH → TEXT  ",
    font=("Arial", 14, "bold")
)

right_frame.pack(
    side="right",
    fill="both",
    expand=True,
    padx=8
)


# =========================================================
# MICROPHONE
# =========================================================

microphone_label = tk.Label(
    right_frame,
    text="🎤\n\nMicrophone\n\nSpeech Recognition",
    font=("Arial", 17),
    width=35,
    height=8
)

microphone_label.pack(
    padx=10,
    pady=15
)


# =========================================================
# LANGUAGE SELECTION
# =========================================================

language_label = tk.Label(
    right_frame,
    text="Select Language:",
    font=("Arial", 13)
)

language_label.pack(
    pady=(5, 3)
)


language = ttk.Combobox(
    right_frame,
    values=[
        "English",
        "Tamil",
        "Hindi",
        "Telugu"
    ],
    state="readonly",
    font=("Arial", 12),
    width=18
)

language.current(0)

language.pack(pady=5)


# =========================================================
# SPEECH OUTPUT
# =========================================================

speech_text_label = tk.Label(
    right_frame,
    text="Recognized Speech:",
    font=("Arial", 13, "bold")
)

speech_text_label.pack(
    pady=(15, 5)
)


speech_output = tk.Label(
    right_frame,
    text="---",
    font=("Arial", 16),
    wraplength=400
)

speech_output.pack(
    pady=10
)


# =========================================================
# SPEECH BUTTONS
# =========================================================

speech_button_frame = tk.Frame(right_frame)

speech_button_frame.pack(pady=10)


start_speech_button = tk.Button(
    speech_button_frame,
    text="🎤 START LISTENING",
    font=("Arial", 11, "bold"),
    width=19
)

start_speech_button.pack(
    side="left",
    padx=5
)


stop_speech_button = tk.Button(
    speech_button_frame,
    text="🛑 STOP",
    font=("Arial", 11, "bold"),
    width=10
)

stop_speech_button.pack(
    side="left",
    padx=5
)


# =========================================================
# CONVERSATION HISTORY
# =========================================================

history_label = tk.Label(
    right_frame,
    text="Conversation:",
    font=("Arial", 13, "bold")
)

history_label.pack(
    pady=(10, 3)
)


history_text = tk.Text(
    right_frame,
    height=6,
    width=45,
    font=("Arial", 11),
    wrap="word"
)

history_text.pack(
    padx=10,
    pady=5
)

history_text.config(
    state="disabled"
)


# =========================================================
# BOTTOM STATUS
# =========================================================

bottom_frame = tk.Frame(root)

bottom_frame.pack(
    fill="x",
    padx=25,
    pady=10
)


status_label = tk.Label(
    bottom_frame,
    text="Status: Ready",
    font=("Arial", 12)
)

status_label.pack(
    side="left"
)


# =========================================================
# ADD TO CONVERSATION
# =========================================================

def add_history(sender, message):

    history_text.config(
        state="normal"
    )

    history_text.insert(
        "end",
        sender + ": " + message + "\n"
    )

    history_text.see("end")

    history_text.config(
        state="disabled"
    )


# =========================================================
# START CAMERA
# =========================================================

def start_camera():

    global cap
    global camera_running

    if camera_running:

        return

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        status_label.config(
            text="Status: Camera not available"
        )

        return

    camera_running = True

    status_label.config(
        text="Status: Camera running"
    )

    update_camera()


# =========================================================
# UPDATE CAMERA
# =========================================================

def update_camera():

    global cap
    global camera_running
    global last_confirmed_sign
    global last_speech_time

    if not camera_running:

        return

    success, frame = cap.read()

    if not success:

        status_label.config(
            text="Status: Camera error"
        )

        root.after(
            100,
            update_camera
        )

        return

    # Mirror camera
    frame = cv2.flip(
        frame,
        1
    )

    # Convert BGR → RGB
    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # MediaPipe
    results = hands.process(
        rgb_frame
    )

    predicted_sign = ""

    confidence = 0.0


    # =====================================================
    # HAND DETECTED
    # =====================================================

    if results.multi_hand_landmarks:

        hand_landmarks = results.multi_hand_landmarks[0]

        # Draw hand landmarks
        mp_drawing.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS
        )

        # Wrist landmark
        wrist = hand_landmarks.landmark[0]

        landmarks = []


        # =================================================
        # NORMALIZE LANDMARKS
        # =================================================

        for landmark in hand_landmarks.landmark:

            x = landmark.x - wrist.x

            y = landmark.y - wrist.y

            z = landmark.z - wrist.z

            landmarks.extend([
                x,
                y,
                z
            ])


        # =================================================
        # RANDOM FOREST PREDICTION
        # =================================================

        probabilities = model.predict_proba(
            [landmarks]
        )[0]

        best_index = probabilities.argmax()

        confidence = probabilities[best_index]

        prediction = str(
            model.classes_[best_index]
        )


        # =================================================
        # CONFIDENCE CHECK
        # =================================================

        if confidence >= CONFIDENCE_THRESHOLD:

            prediction_history.append(
                prediction
            )

            predicted_sign = Counter(
                prediction_history
            ).most_common(1)[0][0]

        else:

            prediction_history.clear()


    else:

        prediction_history.clear()

        predicted_sign = ""


    # =====================================================
    # DISPLAY SIGN
    # =====================================================

    if predicted_sign:

        display_text = predicted_sign.replace(
            "_",
            " "
        )

        sign_label.config(
            text="Recognized Sign: " + display_text
        )

        confidence_label.config(
            text=f"Confidence: {confidence * 100:.1f}%"
        )


        # =================================================
        # SPEAK SIGN
        # =================================================

        current_time = time.time()

        if (
            predicted_sign != last_confirmed_sign
            and
            current_time - last_speech_time
            >= speech_cooldown
        ):

            speech_text = predicted_sign.replace(
                "_",
                " "
            )

            print(
                f"Prediction: {speech_text} | "
                f"Confidence: {confidence * 100:.1f}%"
            )

            speech_queue.put(
                speech_text
            )

            add_history(
                "👋 ISL",
                speech_text
            )

            last_confirmed_sign = predicted_sign

            last_speech_time = current_time


    else:

        sign_label.config(
            text="Recognized Sign: ---"
        )

        confidence_label.config(
            text="Confidence: ---"
        )

        last_confirmed_sign = ""


    # =====================================================
    # DISPLAY CAMERA
    # =====================================================

    frame_rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    image = Image.fromarray(
        frame_rgb
    )

    image = image.resize(
        (500, 350)
    )

    photo = ImageTk.PhotoImage(
        image=image
    )

    camera_label.config(
        image=photo,
        text=""
    )

    camera_label.image = photo


    # Continue camera
    root.after(
        10,
        update_camera
    )


# =========================================================
# STOP CAMERA
# =========================================================

def stop_camera():

    global cap
    global camera_running
    global last_confirmed_sign

    camera_running = False

    prediction_history.clear()

    last_confirmed_sign = ""

    if cap is not None:

        cap.release()

        cap = None

    camera_label.config(
        image="",
        text="📷\n\nCamera Preview\n\nPress START CAMERA"
    )

    camera_label.image = None

    sign_label.config(
        text="Recognized Sign: ---"
    )

    confidence_label.config(
        text="Confidence: ---"
    )

    status_label.config(
        text="Status: Camera stopped"
    )


# =========================================================
# START SPEECH TO TEXT
# =========================================================

def start_speech():

    global speech_running
    global speech_thread_stt

    if speech_running:

        return

    speech_running = True

    status_label.config(
        text="Status: Listening..."
    )

    microphone_label.config(
        text="🎤\n\nListening...\n\nSpeak now"
    )

    speech_thread_stt = threading.Thread(
        target=speech_recognition_worker,
        daemon=True
    )

    speech_thread_stt.start()


# =========================================================
# SPEECH RECOGNITION WORKER
# =========================================================

def speech_recognition_worker():

    global speech_running

    selected_language = language.get()

    language_code = language_codes.get(
        selected_language,
        "en-IN"
    )

    try:

        with sr.Microphone() as source:

            print(
                f"🎤 Listening in {selected_language}..."
            )

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            if not speech_running:

                return

            audio = recognizer.listen(
                source,
                timeout=5,
                phrase_time_limit=8
            )


        if not speech_running:

            return


        print(
            "🔄 Converting speech to text..."
        )


        text = recognizer.recognize_google(
            audio,
            language=language_code
        )


        print(
            "📝 You said:",
            text
        )


        root.after(
            0,
            lambda: show_speech_result(text)
        )


    except sr.WaitTimeoutError:

        root.after(
            0,
            lambda: speech_error(
                "No speech detected."
            )
        )


    except sr.UnknownValueError:

        root.after(
            0,
            lambda: speech_error(
                "Could not understand speech."
            )
        )


    except sr.RequestError:

        root.after(
            0,
            lambda: speech_error(
                "Internet/speech service error."
            )
        )


    except Exception as error:

        print(
            "Speech error:",
            error
        )

        root.after(
            0,
            lambda: speech_error(
                "Microphone error."
            )
        )


    finally:

        speech_running = False

        root.after(
            0,
            speech_stopped
        )


# =========================================================
# SHOW SPEECH RESULT
# =========================================================

def show_speech_result(text):

    speech_output.config(
        text=text
    )

    status_label.config(
        text="Status: Speech converted"
    )

    microphone_label.config(
        text="🎤\n\nMicrophone\n\nSpeech Recognition"
    )

    add_history(
        "🎤 Speech",
        text
    )


# =========================================================
# SPEECH ERROR
# =========================================================

def speech_error(message):

    speech_output.config(
        text=message
    )

    status_label.config(
        text="Status: " + message
    )


# =========================================================
# SPEECH STOPPED
# =========================================================

def speech_stopped():

    microphone_label.config(
        text="🎤\n\nMicrophone\n\nSpeech Recognition"
    )


# =========================================================
# STOP SPEECH
# =========================================================

def stop_speech():

    global speech_running

    speech_running = False

    status_label.config(
        text="Status: Listening stopped"
    )

    microphone_label.config(
        text="🎤\n\nMicrophone\n\nSpeech Recognition"
    )


# =========================================================
# BUTTON CONNECTIONS
# =========================================================

start_camera_button.config(
    command=start_camera
)

stop_camera_button.config(
    command=stop_camera
)

start_speech_button.config(
    command=start_speech
)

stop_speech_button.config(
    command=stop_speech
)


# =========================================================
# EXIT PROGRAM
# =========================================================

def exit_program():

    global camera_running
    global speech_running

    camera_running = False

    speech_running = False

    if cap is not None:

        cap.release()

    hands.close()

    speech_queue.put(None)

    root.destroy()


exit_button = tk.Button(
    bottom_frame,
    text="EXIT",
    font=("Arial", 11, "bold"),
    width=10,
    command=exit_program
)

exit_button.pack(
    side="right"
)


# =========================================================
# WINDOW CLOSE BUTTON
# =========================================================

root.protocol(
    "WM_DELETE_WINDOW",
    exit_program
)


# =========================================================
# START VOXARA
# =========================================================

root.mainloop()