import numpy as np
    
class WindowProcessor:
    def __init__(self, sampling_rate: int, window_size: int, overlapping: int):
        self.sampling_rate = sampling_rate # Sampling rate of the signal
        self.window_size = window_size # Size of the window
        self.overlapping = overlapping # Number of overlapping sample points
        self.starting_pointer = 0 # Starting pointer of the window
        self.ending_pointer = 0 # Ending pointer of the window
        self.input_buffer = np.zeros(window_size) # Buffer to store signal
        self.output_buffer = np.zeros(window_size) # Buffer to store signal

        self.on_window_full_cb = None
        self.is_window_full = False

    def get_sample_length(self):
        if (self.ending_pointer >= self.starting_pointer):
            return self.ending_pointer - self.starting_pointer + 1
        else:
            return self.window_size - self.starting_pointer + self.ending_pointer + 1
        
        
    def get_output_buffer(self):
        if (self.ending_pointer >= self.starting_pointer):
            return self.input_buffer[self.starting_pointer:self.ending_pointer + 1]
        else:
            return np.concatenate([self.input_buffer[self.starting_pointer:], self.input_buffer[:self.ending_pointer + 1]], axis = 0)
        
    def set_on_window_full(self, callback):
        self.on_window_full_cb = callback

    def on_window_full(self, data):
        if self.on_window_full_cb != None:
            self.on_window_full_cb(data)
        else:
            return self.is_window_full

    def add_sample(self, sample: float):
        # Add sample to signal
        self.input_buffer[self.ending_pointer] = sample

        if (self.get_sample_length() == self.window_size):
            self.is_window_full = True
            self.output_buffer = self.get_output_buffer()
            self.on_window_full(self.output_buffer)
            self.starting_pointer = (self.ending_pointer + 1 - self.overlapping) % self.window_size
        else:
            self.is_window_full = False

        # Increment ending pointer
        self.ending_pointer = (self.ending_pointer + 1) % self.window_size

        

def test_window_buffer():
    window_processor = WindowProcessor(100, 4, 2)
    for i in range(100):
        window_processor.add_sample(i)

        if (window_processor.is_window_full):
            print(window_processor.output_buffer)
