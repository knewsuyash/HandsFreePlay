import cv2
import mediapipe as mp
import numpy as np

class GestureEngine:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    def process_frame(self, frame):
        """Standardize frame and detect hands."""
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)
        return result, frame

    def draw_landmarks(self, frame, result):
        """Draw Standard MediaPipe Landmarks."""
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

    def is_hand_closed(self, landmarks):
        """Detect if a hand is closed (fist)."""
        wrist = landmarks[0]
        tip_ids = [4, 8, 12, 16, 20]
        
        # Calculate average distance of tips to wrist
        avg_dist = np.mean([np.linalg.norm(
            np.array([landmarks[i].x, landmarks[i].y]) - np.array([wrist.x, wrist.y])
        ) for i in tip_ids])
        
        return avg_dist < 0.08  # Tune threshold

    def get_hand_tilt_and_height(self, landmarks):
        """Calculate hand tilt (X-axis) and height (Y-axis)."""
        wrist = landmarks[0]
        index_mcp = landmarks[5]
        
        tilt = index_mcp.x - wrist.x
        height = wrist.y
        return tilt, height

    def get_steering_angle(self, hand_landmarks):
        """Calculate precise angle for racing games."""
        wrist = hand_landmarks.landmark[0]
        index = hand_landmarks.landmark[5]
        dx = index.x - wrist.x
        dy = index.y - wrist.y
        return np.degrees(np.arctan2(dy, dx))
