import random
from augm import *
from pathlib import Path
import numpy as np
from uniform import *
import logging

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def random_coefficient():
    return random.random()

def new_volume(sc1, sc2):
    random.choice([sc1, sc2])

def mixture(sc1, sc2, audio_segment1, audio_segment2):
    enh1 = audio_segment1 - calculate_db_loss(sc1)
    enh2 = audio_segment2 - calculate_db_loss(sc2)
    mixed_segment = mix_overlay(enh1, enh2)

    return mixed_segment

def choose_audio(path):
    audio_files = [file for file in path.glob('*.wav') if not file.name.startswith('._')]
    if audio_files:
        return random.choice(audio_files)
    return None

def calculate_db_loss(percent):
    return -10 * np.log10(percent)


def simple_benchmark(num, path, dir1, dir2, p1, p2, progress_bar):
    dir1_norm = get_percentile_dBFS(dir1, 0.95)
    logging.info(f"Dir 2 {p1 * 100} percentile: {dir1_norm} dBFS)")

    dir2_norm = get_percentile_dBFS(dir2, 0.95)
    logging.info(f"Dir 2 {p2 * 100} percentile: {dir2_norm} dBFS)")

    for i in range(num):
        audio_1 = choose_audio(dir1)
        segment_1 = normalize_dBFS(audio_1, dir1_norm)

        if len(segment_1) > 15000:
            segment_1 = random_segment(segment_1, 15000)
        
        while len(segment_1) < 15000:
            extra_audio = choose_audio(dir1)
            extra_segment = normalize_dBFS(extra_audio, dir1_norm)
            segment_1 = concatenate(segment_1, extra_segment, crossfade_duration=300)
        

        audio_2 = choose_audio(dir2)
        segment_2 = normalize_dBFS(audio_2, dir2_norm)

        if len(segment_2) > 10000:
            segment_2 = random_silence_mask(segment_2, total_silence_duration=3000, fade_duration=300)

        k1 = random_coefficient()
        k2 = random_coefficient()

        logging.info(f"Audio 1 coefficient: {k1} Audio 2 coefficient: {k2}")

        mixed_segment = mixture(k1, k2, segment_1, segment_2)
        chosen_volume = random.choice([segment_1.dBFS, segment_2.dBFS])
        mixed_segment = mixed_segment.apply_gain(chosen_volume - mixed_segment.dBFS)
        mixed_segment.export(path / f"audio{i+1}.wav", format='wav')

        progress = ((i + 1) / num) * 100
        progress_bar['value'] = progress 
        root.update_idletasks()
                           

def select_directory(entry):
    directory = filedialog.askdirectory()
    if directory:
        entry.delete(0, tk.END)
        entry.insert(0, directory)

def start_benchmark(num_files_entry, dir1_entry, dir2_entry, dest_entry, progress_bar):
    try:
        num_files = int(num_files_entry.get())
        dir1 = Path(dir1_entry.get())
        dir2 = Path(dir2_entry.get())
        dest = Path(dest_entry.get())

        if not dir1.exists() or not dir2.exists() or not dest.exists() or num_files <= 0:
            messagebox.showerror("Error", "Please ensure all paths exist and the number of files is positive.")
            return

        messagebox.showinfo("Success", "Benchmark started. Check the console for progress.")

        # Reset progress bar
        progress_bar['value'] = 0
        simple_benchmark(num_files, dest, dir1, dir2, progress_bar)
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number of files.")

def validate_percentile(P):
    """Validate the percentile entry to ensure it's between 0.0 and 1.0."""
    try:
        if P == "":
            return True
        val = float(P)
        if 0.0 <= val <= 1.0:
            return True
        else:
            return False
    except ValueError:
        return False

if __name__ == '__main__':
    root = tk.Tk()
    root.title("soundmerge Benchmark")

    vcmd = root.register(validate_percentile)

    tk.Label(root, text="Number of files:").grid(row=0, column=0)
    num_files_entry = tk.Entry(root)
    num_files_entry.grid(row=0, column=1)

    tk.Label(root, text="Directory 1:").grid(row=1, column=0)
    dir1_entry = tk.Entry(root)
    dir1_entry.grid(row=1, column=1)
    tk.Button(root, text="Browse", command=lambda: select_directory(dir1_entry)).grid(row=1, column=2)

    tk.Label(root, text="Directory 2:").grid(row=2, column=0)
    dir2_entry = tk.Entry(root)
    dir2_entry.grid(row=2, column=1)
    tk.Button(root, text="Browse", command=lambda: select_directory(dir2_entry)).grid(row=2, column=2)

    tk.Label(root, text="Destination Directory:").grid(row=3, column=0)
    dest_entry = tk.Entry(root)
    dest_entry.grid(row=3, column=1)

    tk.Label(root, text="Percentile 1 (0.0-1.0):").grid(row=4, column=0)
    percentile1_entry = tk.Entry(root, validate="key", validatecommand=(vcmd, '%P'))
    percentile1_entry.grid(row=4, column=1)

    tk.Label(root, text="Percentile 2 (0.0-1.0):").grid(row=5, column=0)
    percentile2_entry = tk.Entry(root, validate="key", validatecommand=(vcmd, '%P'))
    percentile2_entry.grid(row=5, column=1)

    tk.Button(root, text="Browse", command=lambda: select_directory(dest_entry)).grid(row=3, column=2)

    tk.Button(root, text="Start Benchmark", command=lambda: start_benchmark(num_files_entry, dir1_entry, dir2_entry, dest_entry)).grid(row=6, column=0, columnspan=3)

    progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')
    progress_bar.grid(row=7, column=0, columnspan=3, pady=10)

    root.mainloop()
    