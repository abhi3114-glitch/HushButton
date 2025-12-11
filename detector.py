import cv2
import numpy as np
import time
from collections import deque

class FlashDetector:
    def __init__(self, threshold=200):
        self.threshold = threshold
        self.history = deque(maxlen=5) # Smooth out readings if needed
        
        # State machine for flash patterns
        self.last_flash_time = 0
        self.flash_count = 0
        self.window_start_time = 0
        self.DETECTION_WINDOW = 1.0 # Seconds to wait for second flash
        
        # Cooldown to prevent detecting the same long flash as multiple
        self.in_flash_state = False
        
    def process_frame(self, frame):
        """
        Process a frame and return the detected event ('MUTE', 'UNMUTE', or None).
        Also returns the brightness score (pixel count > threshold).
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Robust Flash Detection: Count pixels that are very bright (saturated)
        # This filters out general room brightness (unless room is blindingly bright)
        # and small reflections (low pixel count).
        _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        bright_pixel_count = cv2.countNonZero(thresh)
        
        # Score is detection count
        detection_score = bright_pixel_count
        
        detected_event = None
        current_time = time.time()
        
        # Use user-defined threshold against the *count* of bright pixels
        # E.g. slider 0-5000
        is_flash_now = detection_score > self.threshold
        
        # Flash rising edge detection
        if is_flash_now and not self.in_flash_state:
            self.in_flash_state = True
            detected_event = self._on_flash_detected(current_time)
        elif not is_flash_now and self.in_flash_state:
            self.in_flash_state = False
            
        # Check for window timeout to resolve single flash (MUTE)
        if detected_event is None and self.flash_count == 1:
            if current_time - self.window_start_time > self.DETECTION_WINDOW:
                detected_event = self._resolve_pattern()
                
        return detected_event, detection_score

    def _on_flash_detected(self, timestamp):
        event = None
        if self.flash_count == 0:
            self.window_start_time = timestamp
            self.flash_count = 1
        elif self.flash_count == 1:
            # Check if this is within the window
            if timestamp - self.window_start_time <= self.DETECTION_WINDOW:
                self.flash_count = 2
                event = "UNMUTE" # Immediate trigger
                # Reset logic immediately or wait? 
                # Better to reset so we don't carry over state.
                self.flash_count = 0 
            else:
                # Window expired, treat as new first flash
                self.flash_count = 1
                self.window_start_time = timestamp
        return event

    def _resolve_pattern(self):
        event = None
        if self.flash_count == 1:
            event = "MUTE"
        # Count 2 is now handled immediately in _on_flash_detected, so this is mainly for single flash timeout
        
        # Reset
        self.flash_count = 0
        return event

    def set_threshold(self, val):
        self.threshold = val
