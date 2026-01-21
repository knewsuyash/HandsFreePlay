import pyautogui
import keyboard

class InputController:
    def __init__(self):
        self.current_profile = "default"
        self.pressing = {'w': False, 'a': False, 's': False, 'd': False}
        self.clicking = {'left': False, 'right': False}
        self.prev_steering_key = None

    def set_profile(self, profile_name):
        self.current_profile = profile_name
        print(f"Switched to profile: {profile_name}")

    def reset_inputs(self):
        """Release all held keys."""
        for key in self.pressing:
            if self.pressing[key]:
                keyboard.release(key)
                self.pressing[key] = False
        if self.prev_steering_key:
            pyautogui.keyUp(self.prev_steering_key)
            self.prev_steering_key = None

    def handle_mouse_clicks(self, left_closed, right_closed):
        if left_closed and not self.clicking['left']:
            pyautogui.mouseDown(button='left')
            self.clicking['left'] = True
        elif not left_closed and self.clicking['left']:
            pyautogui.mouseUp(button='left')
            self.clicking['left'] = False

        if right_closed and not self.clicking['right']:
            pyautogui.mouseDown(button='right')
            self.clicking['right'] = True
        elif not right_closed and self.clicking['right']:
            pyautogui.mouseUp(button='right')
            self.clicking['right'] = False

    def handle_wasd(self, avg_tilt, avg_height, neutral_height):
        if neutral_height is None: 
            return

        height_diff = avg_height - neutral_height

        # A/D - Left/Right
        if avg_tilt < -0.02:
            self._update_key('a', True)
            self._update_key('d', False)
        elif avg_tilt > 0.02:
            self._update_key('d', True)
            self._update_key('a', False)
        else:
            self._update_key('a', False)
            self._update_key('d', False)

        # W/S - Forward/Backward
        if height_diff < -0.03:
            self._update_key('w', True)
            self._update_key('s', False)
        elif height_diff > 0.03:
            self._update_key('s', True)
            self._update_key('w', False)
        else:
            self._update_key('w', False)
            self._update_key('s', False)

    def handle_steering(self, angle):
        """Racing mode steering logic."""
        # Normalize and decide key
        strength = angle / 45.0
        target_key = None
        
        if strength < -0.2: target_key = 'a'
        elif strength > 0.2: target_key = 'd'
        
        if target_key != self.prev_steering_key:
            if self.prev_steering_key:
                pyautogui.keyUp(self.prev_steering_key)
            if target_key:
                pyautogui.keyDown(target_key)
            self.prev_steering_key = target_key

    def _update_key(self, key, press):
        if press and not self.pressing[key]:
            keyboard.press(key)
            self.pressing[key] = True
        elif not press and self.pressing[key]:
            keyboard.release(key)
            self.pressing[key] = False
