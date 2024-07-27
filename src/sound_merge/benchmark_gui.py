"""
This module provides a simple GUI for the soundmerge benchmarking tool.
"""
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

root = tk.Tk()

def select_directory(entry):
    directory = filedialog.askdirectory()
    if directory:
        entry.delete(0, tk.END)
        entry.insert(0, directory)

def validate_percentile(P):
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

def start_benchmark(num_files_entry, dir1_entry, dir2_entry, dest_entry, percetile1_entry, percentile2_entry, benchmark, progress_bar):
    try:
        num_files = int(num_files_entry.get())
        dir1 = Path(dir1_entry.get())
        dir2 = Path(dir2_entry.get())
        dest = Path(dest_entry.get())
        p1 = float(percetile1_entry.get())
        p2 = float(percentile2_entry.get())

        if not dir1.exists() or not dir2.exists() or not dest.exists() or num_files <= 0:
            messagebox.showerror("Error", "Please ensure all paths exist and the number of files is positive.")
            return

        messagebox.showinfo("Success", "Benchmark started. Check the console for progress.")

        progress_bar['value'] = 0
        benchmark(num_files, dest, dir1, dir2, p1, p2, progress_bar)
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number of files.")

def simple_layout(benchmark):
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

    tk.Button(root, text="Start Benchmark", command=lambda: start_benchmark(num_files_entry, dir1_entry, dir2_entry, dest_entry, percentile1_entry, percentile2_entry, benchmark, progress_bar)).grid(row=6, column=0, columnspan=3)

    progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')
    progress_bar.grid(row=7, column=0, columnspan=3, pady=10)

    root.mainloop()

def dynamic_select_layout(benchmark):
    root.title("Dynamic soundmerge Benchmark")
    directories = []

    def add_directory():
        """Add a new directory entry field with a browse button."""
        row = len(directories) + 2
        tk.Label(root, text=f"Source Directory {len(directories)+1}:").grid(row=row, column=0)
        dir_entry = tk.Entry(root)
        dir_entry.grid(row=row, column=1)
        tk.Button(root, text="Browse", command=lambda: select_directory(dir_entry)).grid(row=row, column=2)
        directories.append(dir_entry)

        add_dir_button.grid(row=row+1, column=0, columnspan=5)

    # Initial layout setup
    tk.Label(root, text="Number of files:").grid(row=0, column=0)
    num_files_entry = tk.Entry(root)
    num_files_entry.grid(row=0, column=1)

    tk.Label(root, text="Destination Directory:").grid(row=1, column=0)
    dest_entry = tk.Entry(root)
    dest_entry.grid(row=1, column=1)
    tk.Button(root, text="Browse", command=lambda: select_directory(dest_entry)).grid(row=1, column=2)

    add_dir_button = tk.Button(root, text="Add Directory", command=add_directory)
    add_dir_button.grid(row=2, column=0, columnspan=3)

    def start_dynamic_benchmark():
        try:
            num_files = int(num_files_entry.get())
            dest = Path(dest_entry.get())
            dirs = [Path(entry.get()) for entry in directories]
            messagebox.showinfo("Success", "Benchmark started. Check the console for progress.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of files.")

    tk.Button(root, text="Start Benchmark", command=start_dynamic_benchmark).grid(row=len(directories) + 20, column=0, columnspan=3)

    progress_bar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')
    progress_bar.grid(row=len(directories) + 21, column=0, columnspan=3, pady=10)

    root.mainloop()