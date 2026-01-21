import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import keyboard  # for key press simulation



# Initialize mediapipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

def is_hand_closed(landmarks):
    wrist = landmarks[0]
    tip_ids = [4, 8, 12, 16, 20]
    avg_dist = np.mean([np.linalg.norm(
        np.array([landmarks[i].x, landmarks[i].y]) - np.array([wrist.x, wrist.y])
    ) for i in tip_ids])
    return avg_dist < 0.08  # threshold (tune as needed)

def get_hand_tilt(landmarks):
    wrist = landmarks[0]
    index_mcp = landmarks[5]
    return index_mcp.x - wrist.x

def get_hand_height(landmarks):
    wrist = landmarks[0]
    index_mcp = landmarks[5]
    return wrist.y  # lower value = hand higher (camera coordinates)

cap = cv2.VideoCapture(0)
left_clicking = right_clicking = False
pressing_A = pressing_D = pressing_W = pressing_S = False

neutral_height = None  # baseline for W/S detection

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    left_hand = right_hand = None
    if result.multi_handedness:
        for idx, hand in enumerate(result.multi_handedness):
            label = hand.classification[0].label
            if label == "Left":
                left_hand = result.multi_hand_landmarks[idx]
            else:
                right_hand = result.multi_hand_landmarks[idx]

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # --- Left / Right click logic ---
    if left_hand:
        left_closed = is_hand_closed(left_hand.landmark)
        if left_closed and not left_clicking:
            pyautogui.mouseDown(button='left')
            left_clicking = True
        elif not left_closed and left_clicking:
            pyautogui.mouseUp(button='left')
            left_clicking = False

    if right_hand:
        right_closed = is_hand_closed(right_hand.landmark)
        if right_closed and not right_clicking:
            pyautogui.mouseDown(button='right')
            right_clicking = True
        elif not right_closed and right_clicking:
            pyautogui.mouseUp(button='right')
            right_clicking = False

    # --- Movement logic (W, A, S, D) ---
    if left_hand and right_hand:
        left_tilt = get_hand_tilt(left_hand.landmark)
        right_tilt = get_hand_tilt(right_hand.landmark)
        avg_tilt = (left_tilt + right_tilt) / 2

        left_height = get_hand_height(left_hand.landmark)
        right_height = get_hand_height(right_hand.landmark)
        avg_height = (left_height + right_height) / 2

        if neutral_height is None:
            neutral_height = avg_height  # baseline

        height_diff = avg_height - neutral_height  # positive = down, negative = up

        # --- Left/Right tilt control (A/D) ---
        if avg_tilt < -0.02:
            if not pressing_A:
                keyboard.press('a')
                pressing_A = True
            if pressing_D:
                keyboard.release('d')
                pressing_D = False
            cv2.putText(frame, "MOVE LEFT (A)", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        elif avg_tilt > 0.02:
            if not pressing_D:
                keyboard.press('d')
                pressing_D = True
            if pressing_A:
                keyboard.release('a')
                pressing_A = False
            cv2.putText(frame, "MOVE RIGHT (D)", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        else:
            if pressing_A:
                keyboard.release('a')
                pressing_A = False
            if pressing_D:
                keyboard.release('d')
                pressing_D = False

        # --- Up/Down height control (W/S) ---
        if height_diff < -0.03:  # hands raised
            if not pressing_W:
                keyboard.press('w')
                pressing_W = True
            if pressing_S:
                keyboard.release('s')
                pressing_S = False
            cv2.putText(frame, "MOVE FORWARD (W)", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 2)
        elif height_diff > 0.03:  # hands lowered
            if not pressing_S:
                keyboard.press('s')
                pressing_S = True
            if pressing_W:
                keyboard.release('w')
                pressing_W = False
            cv2.putText(frame, "MOVE BACKWARD (S)", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
        else:
            if pressing_W:
                keyboard.release('w')
                pressing_W = False
            if pressing_S:
                keyboard.release('s')
                pressing_S = False

    cv2.imshow("Hand Gesture Gaming (WASD + Clicks)", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

# Cleanup
for key in ['a', 'd', 'w', 's']:
    keyboard.release(key)
pyautogui.mouseUp(button='left')
pyautogui.mouseUp(button='right')
cap.release()
cv2.destroyAllWindows()
