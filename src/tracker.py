#track head PITCH angle using 3D landmarks (y + z axes)
#ignore forward/backward lean since it uses depth

import math

class FocusTracker:
    def __init__(self):
        self.baseline_pitch = None
        self.distracted_pitch = None
        self.threshold_pitch = None
    
    def reset(self):
        self.baseline_pitch = None
        self.distracted_pitch = None
        self.threshold_pitch = None
    
    def _get_pitch(self, landmarks):
        """
        Calculate head pitch using forehead (10) and chin (152) in 3D.
        Uses Y and Z coordinates to get the actual tilt angle,
        not affected by leaning forward/backward.
        """
        forehead = landmarks[10]
        chin = landmarks[152]
        
        dy = chin.y - forehead.y
        dz = chin.z - forehead.z
        
        # Pitch angle: how much the face is tilted forward/back
        # Positive = looking down, Negative = looking up
        pitch = math.degrees(math.atan2(dz, dy))
        return pitch
    
    def calibrate_baseline(self, landmarks):
        self.baseline_pitch = self._get_pitch(landmarks)
        self._update_threshold()
        print(f"Baseline pitch calibrated: {self.baseline_pitch:.2f}°")
    
    def calibrate_distracted(self, landmarks):
        self.distracted_pitch = self._get_pitch(landmarks)
        self._update_threshold()
        print(f"Distracted pitch calibrated: {self.distracted_pitch:.2f}°")
    
    def _update_threshold(self):
        if self.baseline_pitch is not None and self.distracted_pitch is not None:
            # Set threshold at 40% of the way from baseline to distracted
            # (closer to baseline = more sensitive, closer to distracted = less sensitive)
            diff = self.distracted_pitch - self.baseline_pitch
            self.threshold_pitch = self.baseline_pitch + diff * 0.4
            print(f"Threshold set at: {self.threshold_pitch:.2f}°")

    @property
    def baseline_dist(self):
        return self.baseline_pitch
    
    @property
    def distracted_dist(self):
        return self.distracted_pitch

    def is_distracted(self, landmarks):
        if self.threshold_pitch is None:
            return False
        
        current_pitch = self._get_pitch(landmarks)
        
        # Direction from baseline to distracted
        direction = self.distracted_pitch - self.baseline_pitch
        
        if direction == 0:
            return False
        
        # Check if current pitch has crossed the threshold in the right direction
        if direction > 0:
            return current_pitch > self.threshold_pitch
        else:
            return current_pitch < self.threshold_pitch