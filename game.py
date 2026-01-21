import cv2
import mediapipe as mp
import numpy as np
import pyautogui

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Initialize MediaPipe Hands
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

def get_hand_tilt(hand_landmarks):
    """Calculate tilt angle of the hand in degrees based on wrist and index finger."""
    wrist = hand_landmarks.landmark[0]
    index = hand_landmarks.landmark[5]  # base of index finger
    dx = index.x - wrist.x
    dy = index.y - wrist.y
    angle = np.degrees(np.arctan2(dy, dx))
    return angle

prev_key = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    h, w, _ = frame.shape
    angles = []

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            angle = get_hand_tilt(hand_landmarks)
            angles.append(angle)

        if len(angles) > 0:
            avg_angle = np.mean(angles)

            # Normalize tilt range roughly between -45° to +45°
            move_strength = np.clip(avg_angle / 45.0, -1, 1)

            if move_strength < -0.2:
                label = f"Move LEFT ({abs(move_strength)*100:.0f}%)"
                color = (0, 0, 255)
                key = 'a'
            elif move_strength > 0.2:
                label = f"Move RIGHT ({abs(move_strength)*100:.0f}%)"
                color = (0, 255, 0)
                key = 'd'
            else:
                label = "CENTER"
                color = (255, 255, 255)
                key = None

            # Key press simulation
            if key != prev_key:
                if prev_key is not None:
                    pyautogui.keyUp(prev_key)
                if key is not None:
                    pyautogui.keyDown(key)
                prev_key = key

            # Draw movement bar
            bar_length = int((move_strength + 1) * w / 2)
            cv2.rectangle(frame, (0, h - 50), (bar_length, h), color, -1)
            cv2.putText(frame, label, (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)
    else:
        if prev_key is not None:
            pyautogui.keyUp(prev_key)
            prev_key = None

    cv2.imshow("Virtual Joystick", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
        break

cap.release()
cv2.destroyAllWindows()
