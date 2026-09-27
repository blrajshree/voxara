import cv2
import mediapipe as mp
import joblib
import time
import threading
import queue
import win32com.client
from collections import deque, Counter

MODEL_PATH = r"E:\voxara\training\voxara_model.pkl"

# Load trained model
model = joblib.load(MODEL_PATH)

# ---------------- SPEECH SYSTEM ----------------

speech_queue = queue.Queue()

def speech_worker():
    # Create Windows Speech API voice
    speaker = win32com.client.Dispatch("SAPI.SpVoice")

    # Voice speed
    speaker.Rate = 0

    # Volume
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

# ---------------- MEDIAPIPE ----------------

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ---------------- CAMERA ----------------

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open webcam.")
    exit()

# ---------------- RECOGNITION SETTINGS ----------------

CONFIDENCE_THRESHOLD = 0.60

prediction_history = deque(maxlen=7)

last_confirmed_sign = ""

speech_cooldown = 1.5

last_speech_time = 0


# ---------------- MAIN LOOP ----------------

while True:

    success, frame = cap.read()

    if not success:
        print("Could not read camera frame.")
        break

    # Mirror camera
    frame = cv2.flip(frame, 1)

    # Convert to RGB
    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # Detect hand
    results = hands.process(rgb_frame)

    predicted_sign = ""
    confidence = 0.0

    # ---------------- HAND DETECTED ----------------

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

        # Normalize landmarks relative to wrist
        for landmark in hand_landmarks.landmark:

            x = landmark.x - wrist.x
            y = landmark.y - wrist.y
            z = landmark.z - wrist.z

            landmarks.extend([x, y, z])

        # Prediction probabilities
        probabilities = model.predict_proba(
            [landmarks]
        )[0]

        best_index = probabilities.argmax()

        confidence = probabilities[best_index]

        prediction = str(
            model.classes_[best_index]
        )

        # ---------------- CONFIDENCE CHECK ----------------

        if confidence >= CONFIDENCE_THRESHOLD:

            prediction_history.append(prediction)

            predicted_sign = Counter(
                prediction_history
            ).most_common(1)[0][0]

        else:

            prediction_history.clear()

    else:

        prediction_history.clear()

    # ---------------- DISPLAY + SPEECH ----------------

    if predicted_sign:

        display_text = predicted_sign.replace(
            "_",
            " "
        )

        cv2.putText(
            frame,
            "Sign: " + display_text,
            (30, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.1,
            (0, 255, 0),
            3
        )

        cv2.putText(
            frame,
            f"Confidence: {confidence * 100:.1f}%",
            (30, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        current_time = time.time()

        # Speak only when sign changes
        if (
            predicted_sign != last_confirmed_sign
            and
            current_time - last_speech_time >= speech_cooldown
        ):

            speech_text = predicted_sign.replace(
                "_",
                " "
            )

            print(
                f"Prediction: {speech_text} | "
                f"Confidence: {confidence * 100:.1f}%"
            )

            # Send to speech worker
            speech_queue.put(speech_text)

            last_confirmed_sign = predicted_sign

            last_speech_time = current_time

    else:

        cv2.putText(
            frame,
            "Show a trained sign",
            (30, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            2
        )

        last_confirmed_sign = ""

    # Show camera
    cv2.imshow(
        "Voxara - ISL Recognition",
        frame
    )

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ---------------- CLEANUP ----------------

cap.release()

hands.close()

cv2.destroyAllWindows()

speech_queue.put(None)

print("\nVoxara stopped.")