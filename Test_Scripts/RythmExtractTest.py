import wave
import numpy as np
import matplotlib.pyplot as plt

# Without using libraries 
def get_tempo(filename, threshold):

    C = 1 # Sensitivity constant 
    B = np.zeros(44032) # History buffer 
    
    # Read wav file
    wavFile = wave.open(filename, 'r')
    data = wavFile.readframes(-1)
    data = np.frombuffer(data, dtype=np.int32)
    sampling_rate = wavFile.getframerate()
    Te = 1/sampling_rate
    wavFile.close()

    # Detect beats
    beats = []
    prev = 0
    for n in range(len(data)):
        # Compute instant energy
        e = np.sum(data[n:n+1024]**2)/1024
        # Compute average energy 
        E_avg = np.sum(B[:(44032-1024)]**2)/44032
        # Detect beat 
        if e > C*E_avg and (n*Te - prev) > threshold:
            beats.append(n*Te)
            prev = n*Te
            print("Beat detected at time {}".format(n*Te))
        # Shift history buffer 
        B[:(44032-1024)] = B[1024:]
        # Add new samples to history buffer
        if n + 1024 < len(data):
            B[44032-1024:] = data[n:n+1024]
    
    return beats

def plot_beats(filename, peak_times):

    # Read in the WAV file
    wav = wave.open(filename, mode='r')
    # Extract Raw Audio from WAV file
    data = wav.readframes(-1)
    data = np.frombuffer(data, dtype=np.int32)

    # Calculate the time axis
    fs = wav.getframerate()
    Time = np.linspace(0, len(data)/fs, num=len(data))

    # Plot the signal
    plt.plot(Time, data)

    # Plot vertical lines for each peak
    for peak in peak_times:
        plt.axvline(x=peak, color='red')

    plt.show()

# Call the detect_beats function
peak_times = ((get_tempo('Source_Music/Metronome.wav', .2)))

# Plot the beats
plot_beats('Source_Music/Metronome.wav', peak_times)

