import numpy as np
import math as m

from numpy.fft import fft, ifft, fftfreq
import wave
import struct



class signal:
    """
    Class for storing signal.
    """

    def __init__(self, name, x, fs):
        """
        Initializes the signal with a name, sample data, and sample rate.
        """
        self.name = name
        if x.dtype == np.int16:
            self.x = x.astype(np.float64) / (2**15 - 1)
        else:
            self.x = x.copy().astype(np.float64)

        self.fs = fs

        self.n = np.arange(0, len(x-1))

        self.y = None
        self.f = None

    def freq_response(self,sens=1.12):
        """
        Generates a Frequency Response of the signal and converts it to dB scale.
        """
     
        self.y_fft = fft(self.x)

        self.f = fftfreq(len(self.x), 1 / self.fs)
        
        A = 2*np.abs(self.y_fft) / len(self.x)
        self.y = 20 * np.log10(A + np.finfo(float).eps) 
        
        self.y_mV = np.log10(A * sens + np.finfo(float).eps)
        
        

    def export(self, filename):
        """
        Exports the signal as a WAV file.
        """
        if self.x.dtype != np.int16:
            x = (self.x/np.max(np.abs(self.x)) * (2**15 - 1)).astype(np.int16)
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1) 
            wav_file.setsampwidth(2)  
            wav_file.setframerate(self.fs)

            data = struct.pack('<' + ('h' * len(x)), *x)
            wav_file.writeframes(data)


def signal_filter(name, sig1, sig2):
    """
    Computes a Convolution using the FFT and zero-padding.
    """
    if len(sig1.x) > len(sig2.x):
        sig1_x = np.pad(sig1.x, (0, len(sig2.x)), mode='constant', constant_values=0)
        sig2_x = np.pad(sig2.x, (0, len(sig1.x) - len(sig2.x)+len(sig2.x)), mode='constant', constant_values=0)
    else:
        sig1_x = np.pad(sig1.x, (0, len(sig2.x) - len(sig1.x)+len(sig2.x)), mode='constant', constant_values=0)
        sig2_x = np.pad(sig2.x, (0, len(sig2.x)), mode='constant', constant_values=0)

    y = np.multiply(fft(sig1_x), fft(sig2_x))

    x = ifft(y)

    filtered_signal = signal(name, x, sig1.fs)

    return filtered_signal

def signal_inv_reg_filter(name, sig1, sig2,metric_delay=0,fs=48000,reg_param=0,K=1,sweep_T=0):
    """
    Computes an inverse regularized filter for two signals.
    This routine solves for the impulse response H in the equation Y[k] = X[k]H[k] 
    given a regularization parameter and using zero-padding to properly deal with the signal lengths.

    Parameters:
    
    name: String name for the resulting signal object.
    sig1: The convolved signal; the output from an LTI system, Y.
    sig2: The original signal or non-filtered signal. This is the input to an LTI system.
    metric_delay: A delay metric in seconds. It compensates for delays between the signals.
    fs: The sampling rate of the signal; Default is 48000 Hz.
    reg_param: Regularization parameter. It is to control the impact of the noise, 
       which is improves the inversion stability.
    k: Number of repetitions of the exponential sine sweep ESS signal.
    sweep_T: Period of each repeating sweep - Sweep_T + Decay_T.
    Returns:
    
    filtered signal: Signal object representing the approximated impulse response of the system, \hat{h}.
    """
    
    n0 = int(sweep_T*fs)
    
    if fs == None:
        fs = sig1.fs
        
        if sig1.fs != sig2.f:
            print("Warning: Sample Rate of Signals are not equivalent!")
    elif sig1.fs != fs or sig2.fs != fs:
        print("Warning: One or more Signal is not correct Sample Rate!")

    
    sample_delay = int(metric_delay*fs)

    
    print(f"Status: Compensating for delay of {sample_delay} frames")
    
    if sample_delay > 0:
        sig1_x = sig1.x[abs(sample_delay):] 
        sig2_x = sig2.x
    else:
        sig2_x = sig2.x[abs(sample_delay):] 
        sig1_x = sig1.x
        
        
    print("Status: Padding Signals for Linear Convolution")
    #zero-pad signal:
    pad_length = len(sig1_x) + len(sig2_x) - 1
    #   Assure that only 0s wrap around.
    sig1_x_final = np.pad(sig1_x, (0,pad_length-len(sig1_x)), mode='constant', constant_values=0)
    sig2_x_final = np.pad(sig2_x, (0,pad_length-len(sig2_x)), mode='constant', constant_values=0)
        
    
    print("Status: Computing FFTs - Y and X")

    Y = fft(sig1_x_final)
    X = fft(sig2_x_final)
    print("Status: Computing G from X")
    G = np.conjugate(X)/(np.abs(X)**2+reg_param*pad_length**2)

    print("Status: Computing FFT Products: Y*G")
    H = np.multiply(Y,G)
    print("Status: Computing iFFT of Product")
    h = ifft(H)

    
    if K > 1:
        h = h[:n0*K]
        
        h_shape = h.reshape(K,-1)
        
        h = np.sum(h_shape,axis=0)/K
    
    filtered_signal = signal(name, h, sig1.fs)
    
    return filtered_signal


def ir_tail_cleanup(signal,tol = 1):
    diff_indices = np.where(np.abs(np.diff(signal.x)) > tol)[0]
    
    if len(diff_indices) == 0:
        return signal
    
    trim_index = diff_indices[-1] + 1
    
    signal.x = signal.x[:trim_index]
    signal.n = signal.n[:trim_index]

    return signal
    

def signal_ess(T, fs, f0, f1, t0=None,fade_type="hann",K=1,spacing=0):
    """
    Generates an Exponential Sine Sweep (ESS) of specified time-length T.
    
    Parameters:
    - T: Sweep time in seconds.
    - fs: Sample rate in Hz.
    - f0: Start frequency of the sweep in Hz.
    - f1: End frequency of the sweep in Hz.
    - t0: Time for fade-in and fade-out in seconds (default is T/2).
    - fade_type: Type of fade to apply ('hann' or 'tri', default is 'hann').
    - K: Number of repetitions for the sweep (default is 1).
    - spacing: Spacing between repetitions in seconds (default is 0).
    
    Returns:
    - signal: Signal object containing the generated ESS.
    """
    if t0 == None:
        t0 = T/2
    elif t0 > T/2:
        print("Error: t0 cannot be over T/2!")
        return None

    t = np.linspace(0, T, m.ceil(fs * T))
    L = T / np.log(f1 / f0)
    x = np.sin(2 * np.pi * f0 * L * (np.exp(t / L) - 1))
    
    
    if fade_type == "hann":
        fade = hann_fade(T,t0,fs)
        x=fade*x
    elif fade_type == "tri":
        fade = linear_fade(T,t0,fs)
        x=fade*x
    
    x = np.pad(x, (0, spacing*fs), mode='constant', constant_values=0)
    
    if K>1:
          x = np.tile(x, (K, 1)).flatten()

    return signal(f"ESS Signal - T = {T} sec, f = [{f0} Hz , {f1} Hz]", x, fs)




def signal_import(filename):
    """
    Imports a signal from a WAV file.
    
    Parameters:
    - filename: The name of the WAV file to import.
    
    Returns:
    - signal: Signal object containing the imported audio data.
    """
    with wave.open(filename, 'rb') as wav_file:
        nchannels = wav_file.getnchannels()
        sampwidth = wav_file.getsampwidth()
        fs = wav_file.getframerate()

        if sampwidth != 2:
            raise ValueError(
                "Unsupported WAV format. Must be 16-bit signed integer!")

        if nchannels > 1:
            print("Warning: non-mono WAV file detected. Converting to mono.")
            frames = wav_file.readframes(wav_file.getnframes())
            data = struct.unpack(
                '<' + str(len(frames) // sampwidth) + 'h', frames)
            left_channel = np.array(data[::2], dtype=np.float32)
            right_channel = np.array(data[1::2], dtype=np.float32)
            mono = (left_channel + right_channel) / 2.0
            mono = mono.astype(np.int16)
        else:
            frames = wav_file.readframes(wav_file.getnframes())
            data = struct.unpack(
                '<' + str(len(frames) // sampwidth) + 'h', frames)
            mono = np.array(data, dtype=np.int16)

    return signal(f"{filename}", mono, fs)


def linear_fade(T,t0,fs):
    samples = np.linspace(0, T, m.ceil(fs*T))
    fade = np.ones(m.ceil(fs*T))
    
    for idx,t in enumerate(samples):
        if 0 <= t < t0:
            fade[idx] = t/t0
        elif T-t0< t <= T:
            fade[idx] = -t/t0+T/t0
            
    return fade


def hann_fade(T,t0,fs):
    samples = np.linspace(0, T, m.ceil(fs*T))
    fade = np.ones(m.ceil(fs*T))
    
    for idx,t in enumerate(samples):
        if 0 <= t < t0:
            fade[idx] = (np.sin( np.pi*t/(2*t0)))**2
        elif T-t0< t <= T:
            fade[idx] = (np.sin( np.pi*(t-(T-t0)+t0)/(2*t0)))**2
            
    return fade

def compute_nrmse(ref, signal):
    """
    Computes the normalized root mean square error (NRMSE) between a reference signal and signal.
    
    Parameters:
    - ref: The reference signal object.
    - signal: The signal object to compare against the reference.
    
    Returns:
    - nrmse: The normalized root mean square error value.
    - error: A 2D array with freq and squared errors for plotting/analysis.
    """
    length = max(len(ref.x), len(signal.x))
    ref.x = np.pad(ref.x, (0, length - len(ref.x)), mode='constant')
    signal.x = np.pad(signal.x, (0, length - len(signal.x)), mode='constant')

    ref_X = fft(ref.x)[:len(ref.x)//2]
    signal_X = fft(signal.x)[:len(ref.x)//2]
    
    se = (np.abs(ref_X - signal_X)) ** 2

    mse = np.mean(se)
    rmse = np.sqrt(mse)
    
    norm = np.sum(np.abs(ref_X) ** 2)
    nrmse = rmse / norm
    
    
    freqs = fftfreq(len(ref.x), 1 / ref.fs)[:len(ref.x) // 2]
    error = np.vstack((freqs, se))

    return nrmse, error

def compute_rt(signal,noisefloor=-20):
    """
    Computes the reverberation time (RT60) and early decay time (EDT) of a signal.

    Parameters:
    - signal: The signal object for which the reverberation time is measured.
    - noise floor: The noise floor level in dB. The default is -20.
    
    Returns:
    - rt60: The reverberation time in seconds.
    - edt: The Early Decay Time, in seconds.
    """

    
    squared_ir = signal.x ** 2

    energy_decay = np.cumsum(squared_ir[::-1])[::-1]
    
    max_energy = np.max(energy_decay)
    decay_db = 10 * np.log10(energy_decay / max_energy)

    start_db = -5
    end_db = noisefloor+5
    
    if start_db-end_db <= 3:
        return np.nan, np.nan

    idx = np.where((decay_db <= start_db) & (decay_db >= end_db))[0]

    x = idx / signal.fs
    y = decay_db[idx]

    a, b = np.polyfit(x, y, 1)

    edt = np.where(decay_db <= -10)[0][0]/signal.fs
    rt60 = -60 / a

    return rt60, edt