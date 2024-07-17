import wave
from scipy.signal import resample, spectrogram
import os
import tempfile
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from config import *


class WaveObject:
    def __init__(self, audio_data, num_frames, num_channels=2, bytes_per_sample=2,
                 sample_rate=44100):
        self.audio_data = audio_data
        self.audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / (2 ** (bytes_per_sample * 8 - 1))
        self.num_channels = num_channels
        self.bytes_per_sample = bytes_per_sample
        self.sample_rate = sample_rate
        self.num_frames = num_frames
        self.duration = num_frames / sample_rate

    @classmethod
    def from_wave_file(cls, wave_file):
        with wave.open(str(wave_file), 'rb') as wave_read:
            num_frames = wave_read.getnframes()
            audio_data = wave_read.readframes(num_frames)
            num_channels = wave_read.getnchannels()
            bytes_per_sample = wave_read.getsampwidth()
            sample_rate = wave_read.getframerate()
            return cls(audio_data, num_frames, num_channels, bytes_per_sample, sample_rate)
    
    
    def resample_o(self, new_sample_rate):
        original_num_samples = int(len(self.audio_data) / self.bytes_per_sample / self.num_channels)
        
        new_num_samples = int(original_num_samples * (new_sample_rate / self.sample_rate))
        
        audio_array_ch = (self.audio_array).reshape(-1, self.num_channels)
        
        resampled_audio_array = resample(audio_array_ch, new_num_samples, axis=0)

        new_audio_data = resampled_audio_array.astype(np.int16).ravel().tobytes()
        
        return WaveObject(new_audio_data, self.num_frames, self.num_channels, self.bytes_per_sample, new_sample_rate)
        
    def save_to_file(self, file_path):
        with wave.open(str(file_path), 'wb') as wave_write:
            wave_write.setnchannels(self.num_channels)
            wave_write.setsampwidth(self.bytes_per_sample)
            wave_write.setframerate(self.sample_rate)
            wave_write.writeframes(self.audio_data)

    def display_waveform(self):
        audio_data_np = self.audio_array
        if self.num_channels == 2:
            audio_data_np = (self.audio_array).reshape(-1, 2).mean(axis=1)
        plt.figure(figsize=(10, 4))
        plt.plot(audio_data_np)
        plt.title('Wave File Plot')
        plt.xlabel('Frame')
        plt.ylabel('Amplitude')
        plt.show()
    

    def display_waveform_from_audiosegment(audio_segment):
        samples = np.array(audio_segment.get_array_of_samples())
        
        num_channels = audio_segment.channels
        if num_channels == 2:
            samples = samples.reshape(-1, 2).mean(axis=1)
        
        plt.figure(figsize=(10, 4))
        plt.plot(samples)
        plt.title('Wave File Plot')
        plt.xlabel('Frame')
        plt.ylabel('Amplitude')
        plt.show()

    def display_spectogram(self):
        audio_data_np = self.audio_array
        if self.num_channels == 2:
            audio_data_np = (self.audio_array).reshape(-1, 2).mean(axis=1)
        f, t, Sxx = spectrogram(audio_data_np, self.sample_rate)
        plt.figure(figsize=(10, 4))
        plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.title('Spectrogram')
        plt.colorbar(label='Intensity [dB]')
        plt.show()


    def display_spectrogram_from_audiosegment(audio_segment):
        samples = np.array(audio_segment.get_array_of_samples())
        
        num_channels = audio_segment.channels
        if num_channels == 2:
            samples = samples.reshape(-1, 2).mean(axis=1)
        
        f, t, Sxx = spectrogram(samples, audio_segment.frame_rate)
        plt.figure(figsize=(10, 4))
        plt.pcolormesh(t, f, 10 * np.log10(Sxx), shading='gouraud')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')
        plt.title('Spectrogram')
        plt.colorbar(label='Intensity [dB]')
        plt.show()
        
    @staticmethod
    def comparability(wf1, wf2):
        if not (wf1.sample_rate == wf2.sample_rate and
                wf1.num_channels == wf2.num_channels and
                wf1.bytes_per_sample == wf2.bytes_per_sample):
            print("Incompatible wave objects. Ensure same sample rate, number of channels, and bytes per sample.")
            return False
        return True

    def ensure_wave_object(wave):
        if not isinstance(wave, WaveObject):
            try:
                wave = WaveObject.from_wave_file(wave)
            except Exception as e:
                print(f"Error processing wave file: {e}")
                return None
        return wave

    @staticmethod
    def concatenate(wave1, wave2):
        wave1 = WaveObject.ensure_wave_object(wave1)
        if wave1 is None:
            return None

        wave2 = WaveObject.ensure_wave_object(wave2)
        if wave2 is None:
            return None

        if not (WaveObject.comparability(wave1, wave2)):
            return None

        audio_array1 = np.frombuffer(wave1.audio_data, dtype=np.int16)
        audio_array2 = np.frombuffer(wave2.audio_data, dtype=np.int16)
        concat_array = np.concatenate((audio_array1, audio_array2), axis=0)
        new_audio_data = concat_array.astype(np.int16).tobytes()

        new_num_frames = wave1.num_frames + wave2.num_frames

        return WaveObject(new_audio_data, new_num_frames, wave1.num_channels, wave1.bytes_per_sample, wave1.sample_rate)

    @staticmethod
    def mix(wave1, wave2, volume1=1, volume2=1):
        wave1 = WaveObject.ensure_wave_object(wave1)
        if wave1 is None:
            return None

        wave2 = WaveObject.ensure_wave_object(wave2)
        if wave2 is None:
            return None
        
        if not (WaveObject.comparability(wave1, wave2)):
            return None

        len1, len2 = len(wave1.audio_array), len(wave2.audio_array)

        if len1 < len2:
            wave1.audio_array = np.pad(wave1.audio_array, (0, len2 - len1), 'constant')
        elif len2 < len1:
            wave2.audio_array = np.pad(wave2.audio_array, (0, len1 - len2), 'constant')

        mixed_array = wave1.audio_array * volume1 + wave2.audio_array * volume2

        if np.max(np.abs(mixed_array)) > 1:
            mixed_array /= np.max(np.abs(mixed_array))

        mixed_array = (mixed_array * 32768).astype(np.int16)
        new_audio_data = mixed_array.tobytes()
        new_num_frames = len(mixed_array)

        return WaveObject(new_audio_data, new_num_frames, wave1.num_channels, wave1.bytes_per_sample, wave1.sample_rate)

    @staticmethod
    def mix_alt(wave1, wave2):
        len1, len2 = len(wave1.audio_array), len(wave2.audio_array)
        if len1 < len2:
            wave1.audio_array = np.pad(wave1.audio_array, (0, len2 - len1), 'constant')
        elif len2 < len1:
            wave2.audio_array = np.pad(wave2.audio_array, (0, len1 - len2), 'constant')

        mixed_array = np.zeros(len(wave1.audio_array))

        for i in range(len(wave1.audio_array)):
            mixed_array[i] = max(abs(wave1.audio_array[i]), abs(wave2.audio_array[i]))

        return mixed_array

    def normalize():
        pass

    def frequency_filtering():
        pass
    
    def frame_segment(self, start_frame, end_frame):
        start_frame = start_frame * self.bytes_per_sample * self.num_channels
        end_frame = end_frame * self.bytes_per_sample * self.num_channels
        new_audio_data = self.audio_data[start_frame: end_frame]
        new_num_frames = end_frame - start_frame

        return WaveObject(new_audio_data, new_num_frames, self.num_channels, self.bytes_per_sample, self.sample_rate)
    
    def time_segment(self, start_time, end_time):
        start_frame = int(start_time * self.sample_rate)
        end_frame = int(end_time * self.sample_rate)
        new_audio_data = self.audio_data[start_frame * self.bytes_per_sample * self.num_channels: end_frame * self.bytes_per_sample * self.num_channels]
        new_num_frames = end_frame - start_frame

        return WaveObject(new_audio_data, new_num_frames, self.num_channels, self.bytes_per_sample, self.sample_rate)

    def play(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
            tmpfile_name = tmpfile.name
        
            with wave.open(tmpfile_name, 'wb') as wavefile:
                wavefile.setnchannels(self.num_channels)
                wavefile.setsampwidth(self.bytes_per_sample)
                wavefile.setframerate(self.sample_rate)
                wavefile.writeframes(self.audio_data)
        try:
            subprocess.run(['afplay', tmpfile_name])
        finally:
            os.remove(tmpfile_name)
    
    @staticmethod
    def play_from_path(wave_path):
        try:
            subprocess.run(['afplay', wave_path])
        except Exception as e:
            print(f"Failed to play audio: {e}")
    
    #to be changed
    def change_volume(self, volume):
        audio_array = np.frombuffer(self.audio_data, dtype=np.int16).astype(np.float32) / 32768
        audio_array *= volume
        if np.max(np.abs(audio_array)) > 1:
            audio_array /= np.max(np.abs(audio_array))

        audio_array = (audio_array * 32768).astype(np.int16)
        new_audio_data = audio_array.tobytes()
        return WaveObject(new_audio_data, self.num_frames, self.num_channels, self.bytes_per_sample, self.sample_rate)


    def __str__(self):
        return f"Wave Object: {self.num_channels} channel, {self.bytes_per_sample * 8} bit, {self.sample_rate} Hz {self.duration} seconds long"
        
    

class FlacObject:
    # similar functions to WaveObject

    def __init__(self, audio_data, num_frames, num_channels=2, bytes_per_sample=2,
                 sample_rate=44100):
        self.audio_data = audio_data
        self.num_channels = num_channels
        self.bytes_per_sample = bytes_per_sample
        self.sample_rate = sample_rate
        self.num_frames = num_frames
        self.duration = num_frames / sample_rate
    
    @classmethod
    def from_flac_file(cls, flac_file):
        pass


