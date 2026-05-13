
import time
import pyautogui
import threading
from typing import List, Dict, Any

class ClickEngine:
    def __init__(self, on_active_change=None):
        self.is_running = False
        self.points: List[Dict[str, Any]] = []
        self._thread = None
        self.on_active_change = on_active_change
        
        # PyAutoGUI safety settings
        pyautogui.PAUSE = 0.01
        pyautogui.FAILSAFE = True

    def set_points(self, points: List[Dict[str, Any]]):
        self.points = points

    def start(self):
        if not self.is_running and self.points:
            self.is_running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.is_running = False

    def _run_loop(self):
        while self.is_running:
            for i, point in enumerate(self.points):
                if not self.is_running:
                    break
                
                if self.on_active_change:
                    self.on_active_change(i)
                
                # Wait before action
                time.sleep(point.get('delay_before', 0.1))
                
                x, y = point['x'], point['y']
                action = point.get('action', 'left_click')
                
                try:
                    if action == 'left_click':
                        pyautogui.click(x, y, button='left')
                    elif action == 'right_click':
                        pyautogui.click(x, y, button='right')
                    elif action == 'double_click':
                        pyautogui.doubleClick(x, y)
                    elif action == 'hold_left':
                        duration = point.get('duration', 1.0)
                        pyautogui.mouseDown(x, y, button='left')
                        time.sleep(duration)
                        pyautogui.mouseUp(x, y, button='left')
                    elif action == 'hold_right':
                        duration = point.get('duration', 1.0)
                        pyautogui.mouseDown(x, y, button='right')
                        time.sleep(duration)
                        pyautogui.mouseUp(x, y, button='right')
                    elif action == 'key_press':
                        key = point.get('key', 'a')
                        pyautogui.press(key)
                    elif action == 'hold_key':
                        key = point.get('key', 'a')
                        duration = point.get('duration', 1.0)
                        pyautogui.keyDown(key)
                        time.sleep(duration)
                        pyautogui.keyUp(key)
                    elif action == 'type_text':
                        text = point.get('text', '')
                        press_enter = point.get('press_enter', False)
                        pyautogui.write(text)
                        if press_enter:
                            pyautogui.press('enter')
                    elif action == 'drag':
                        target_x = point.get('target_x', x)
                        target_y = point.get('target_y', y)
                        pyautogui.dragTo(target_x, target_y, duration=0.5)
                except Exception as e:
                    print(f"Error executing action: {e}")
                
                # Wait after action
                time.sleep(point.get('delay_after', 0.1))
            
            # Loop delay to prevent 100% CPU usage if sequence is empty or very fast
            time.sleep(0.01)

engine = ClickEngine()
