from mindrove.board_shim import BoardShim, MindRoveInputParams, BoardIds, LogLevels
from .signal_processor import WindowProcessor
import pyautogui as hid
import numpy as np
from numpy.linalg import norm
import matplotlib.pyplot as plt

# Board Configuration
BoardShim.enable_dev_board_logger()
params = MindRoveInputParams()
board_id = BoardIds.MINDROVE_WIFI_BOARD
board_shim = BoardShim(board_id, params)

# Connect to the board
board_shim.prepare_session()
board_shim.start_stream()

# Get channel indices
emg_channels = BoardShim.get_emg_channels(board_id)
accel_channels = BoardShim.get_accel_channels(board_id)
gyro_channels = BoardShim.get_gyro_channels(board_id)
sampling_rate = BoardShim.get_sampling_rate(board_id)

# Init signal processors
gyro_x_processor = WindowProcessor(sampling_rate, 10, 5)
gyro_y_processor = WindowProcessor(sampling_rate, 10, 5)
emg_ch0_processor = WindowProcessor(sampling_rate, 50, 0)
emg_ch1_processor = WindowProcessor(sampling_rate, 100, 0)
emg_ch2_processor = WindowProcessor(sampling_rate, 100, 0)
emg_ch3_processor = WindowProcessor(sampling_rate, 100, 0)
emg_ch4_processor = WindowProcessor(sampling_rate, 100, 0)
emg_ch5_processor = WindowProcessor(sampling_rate, 100, 0)
emg_ch6_processor = WindowProcessor(sampling_rate, 100, 0)
emg_ch7_processor = WindowProcessor(sampling_rate, 100, 0)

#
norm_processor = WindowProcessor(sampling_rate, 1000, 999)

hid.FAILSAFE = False

def position_filter(sample: float):
    if sample < 2 and sample > -2:
        return 0
    
    return sample / sampling_rate * 1500

fig, ax = plt.subplots()     

# Main loop
while True:
    if board_shim.get_board_data_count() > 0:
        data = board_shim.get_current_board_data(1)

        emg_data = data[emg_channels]
        accel_data = data[accel_channels]
        gyro_data = data[gyro_channels]

        gyro_x_processor.add_sample(gyro_data[2])
        gyro_y_processor.add_sample(gyro_data[1])
        emg_ch0_processor.add_sample(emg_data[0])
        emg_ch1_processor.add_sample(emg_data[1])
        emg_ch2_processor.add_sample(emg_data[2])
        emg_ch3_processor.add_sample(emg_data[3])
        emg_ch4_processor.add_sample(emg_data[4])
        emg_ch5_processor.add_sample(emg_data[5])
        emg_ch6_processor.add_sample(emg_data[6])
        emg_ch7_processor.add_sample(emg_data[7])

        dx, dy = 0, 0

        if gyro_x_processor.is_window_full:
            dx = np.mean(gyro_x_processor.output_buffer)
            dx = position_filter(dx)

        if gyro_y_processor.is_window_full:
            dy = np.mean(gyro_y_processor.output_buffer)
            dy = position_filter(dy)

        # Print mean gyro data
        if emg_ch5_processor.is_window_full:
            emg_ch5_fft = np.fft.rfft(emg_ch0_processor.output_buffer)
            emg_ch5_fft_real = emg_ch5_fft.real[1:]
            emg_ch5_fft_real_norm = norm(emg_ch5_fft_real)

            norm_processor.add_sample(emg_ch5_fft_real_norm)

            # ax.clear()
            # ax.plot(norm_processor.get_output_buffer())
            # ax.set_ylim(-100, 10000)

            # plt.pause(0.01)

            if emg_ch5_fft_real_norm > 1500:
                hid.click()
                print("click")

            hid.move(-dx, -dy)

            