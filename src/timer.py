#initialise is_distracted = False and start_time
#if time.time() - start_time >= 5:
    #is_distracted = True, alarm triggers

import time 

class FocusTimer:
    def __init__(self, threshold_seconds = 5.0):
        self.threshold = threshold_seconds
        self.is_distracted = False
        self.start_time = 0

    def update(self, currently_distracted):
        if currently_distracted and not self.is_distracted:
            self.is_distracted = True
            self.start_time = time.time()
            return False
        
        #stop being distracted
        elif not currently_distracted and self.is_distracted:
            self.is_distracted = False
            self.start_time = 0.0
            return False
        
        #still distracted
        elif currently_distracted and self.is_distracted:
            elapsed = time.time() - self.start_time
            if elapsed >= self.threshold:
                return True
        
        #not distracted 
        return False
