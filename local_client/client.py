import cv2
import json
import time
import pygetwindow as gw
from gesture_engine import GestureEngine
from input_controller import InputController

class HandsFreeClient:
    def __init__(self):
        self.engine = GestureEngine()
        self.controller = InputController()
        self.cap = cv2.VideoCapture(0)
        self.neutral_height = None
        self.profiles = self._load_profiles()
        self.last_check = 0
        
        print(">> CLIENT INITIALIZED")
        print(">> PRESS 'ESC' TO EXIT")

    def _load_profiles(self):
        try:
            with open('profiles.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading profiles: {e}")
            return {}

    def auto_switch_profile(self):
        """Check active window and switch profile if needed."""
        # Rate limit checks to every 1 second
        if time.time() - self.last_check < 1.0:
            return

        try:
            active_window = gw.getActiveWindow()
            if active_window:
                title = active_window.title
                # Simple substring matching
                found_profile = False
                for game, profile in self.profiles.items():
                    if game.lower() in title.lower():
                        if self.controller.current_profile != profile:
                            self.controller.set_profile(profile)
                            self.controller.reset_inputs()
                            self.neutral_height = None # Reset WASD neutral point
                        found_profile = True
                        break
                
                # If no specific profile found, switch to default if not already
                if not found_profile and self.controller.current_profile != "default":
                     self.controller.set_profile("default")
                     self.controller.reset_inputs()
                
        except Exception as e:
            pass
            
        self.last_check = time.time()

    def run(self):
        while True:
            self.auto_switch_profile()
            
            success, frame = self.cap.read()
            if not success:
                break

            result, frame = self.engine.process_frame(frame)
            self.engine.draw_landmarks(frame, result)

            left_hand = right_hand = None
            if result.multi_handedness:
                for idx, hand_meta in enumerate(result.multi_handedness):
                    label = hand_meta.classification[0].label
                    if label == "Left":
                        left_hand = result.multi_hand_landmarks[idx]
                    else:
                        right_hand = result.multi_hand_landmarks[idx]

            # --- CONTROL LOGIC BASED ON PROFILE ---
            mode = self.controller.current_profile

            if mode == "mouse" or mode == "default":
                # Logic: Left Hand = Left Click, Right Hand = Right Click
                left_closed = self.engine.is_hand_closed(left_hand.landmark) if left_hand else False
                right_closed = self.engine.is_hand_closed(right_hand.landmark) if right_hand else False
                self.controller.handle_mouse_clicks(left_closed, right_closed)
                
                cv2.putText(frame, "MODE: MOUSE (Click Enabled)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            elif mode == "fps":
                # Logic: Both Hands for WASD
                if left_hand and right_hand:
                    l_tilt, l_height = self.engine.get_hand_tilt_and_height(left_hand.landmark)
                    r_tilt, r_height = self.engine.get_hand_tilt_and_height(right_hand.landmark)
                    
                    avg_tilt = (l_tilt + r_tilt) / 2
                    avg_height = (l_height + r_height) / 2

                    if self.neutral_height is None:
                        self.neutral_height = avg_height
                        cv2.putText(frame, "CALIBRATING...", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    else:
                        self.controller.handle_wasd(avg_tilt, avg_height, self.neutral_height)

                cv2.putText(frame, "MODE: FPS (WASD)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            elif mode == "racing":
                # Logic: Single or Double hand steering
                if right_hand or left_hand:
                    hand_to_use = right_hand if right_hand else left_hand
                    angle = self.engine.get_steering_angle(hand_to_use)
                    self.controller.handle_steering(angle)
                
                cv2.putText(frame, "MODE: RACING (Steer)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)

            cv2.imshow("HandsFreePlay Client", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        # Cleanup
        self.controller.reset_inputs()
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    client = HandsFreeClient()
    client.run()
