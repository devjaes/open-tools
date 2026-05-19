import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import threading
import os
import re

class AudioVideoMerger:
    def __init__(self, root):
        self.root = root
        self.root.title("FFmpeg Audio & Video Merger")
        self.root.geometry("550x300")
        self.root.resizable(False, False)
        
        # Style
        self.style = ttk.Style(self.root)
        if 'clam' in self.style.theme_names():
            self.style.theme_use('clam')
        
        # Variables to store paths
        self.video_path = tk.StringVar()
        self.audio_path = tk.StringVar()
        self.output_path = tk.StringVar()
        
        # Progress and status
        self.progress_var = tk.DoubleVar()
        self.total_duration = 0
        
        self.create_widgets()

    def create_widgets(self):
        padding_opts = {'padx': 10, 'pady': 10}
        
        # --- Frame for Inputs ---
        input_frame = ttk.Frame(self.root, padding=10)
        input_frame.pack(fill='x')
        
        # --- Video ---
        ttk.Label(input_frame, text="Video File:").grid(row=0, column=0, sticky="e", **padding_opts)
        ttk.Entry(input_frame, textvariable=self.video_path, width=45, state='readonly').grid(row=0, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=self.select_video).grid(row=0, column=2, padx=5)

        # --- Audio ---
        ttk.Label(input_frame, text="Audio File:").grid(row=1, column=0, sticky="e", **padding_opts)
        ttk.Entry(input_frame, textvariable=self.audio_path, width=45, state='readonly').grid(row=1, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=self.select_audio).grid(row=1, column=2, padx=5)

        # --- Output ---
        ttk.Label(input_frame, text="Save As:").grid(row=2, column=0, sticky="e", **padding_opts)
        ttk.Entry(input_frame, textvariable=self.output_path, width=45, state='readonly').grid(row=2, column=1, padx=5)
        ttk.Button(input_frame, text="Browse", command=self.select_output).grid(row=2, column=2, padx=5)

        # --- Bottom Frame ---
        bottom_frame = ttk.Frame(self.root, padding=10)
        bottom_frame.pack(fill='both', expand=True)

        # --- Merge Button ---
        self.merge_btn = ttk.Button(bottom_frame, text="Merge Files", command=self.start_merge_thread)
        self.merge_btn.pack(pady=5)

        # --- Progress Bar ---
        self.progress_bar = ttk.Progressbar(bottom_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x', pady=5)

        # --- Status ---
        self.status_label = ttk.Label(bottom_frame, text="Ready", foreground="gray")
        self.status_label.pack()

    def select_video(self):
        file = filedialog.askopenfilename(title="Select Video", filetypes=[("Video Files", "*.mp4 *.mkv *.avi *.mov")])
        if file: self.video_path.set(file)

    def select_audio(self):
        file = filedialog.askopenfilename(title="Select Audio", filetypes=[("Audio Files", "*.mp3 *.wav *.aac *.m4a")])
        if file: self.audio_path.set(file)

    def select_output(self):
        file = filedialog.asksaveasfilename(title="Save Output", defaultextension=".mp4", filetypes=[("MP4 File", "*.mp4")])
        if file: self.output_path.set(file)

    def get_duration(self, file_path):
        """Uses ffprobe to get the duration of the video in seconds."""
        command = [
            "ffprobe", "-v", "error", 
            "-show_entries", "format=duration", 
            "-of", "default=noprint_wrappers=1:nokey=1", 
            file_path
        ]
        try:
            # Hide console window on Windows
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=creationflags)
            return float(result.stdout.strip())
        except Exception:
            return 0

    def parse_time_to_seconds(self, time_str):
        """Parses HH:MM:SS.ms string to seconds."""
        parts = time_str.split(':')
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + float(s)
        return 0

    def start_merge_thread(self):
        video = self.video_path.get()
        audio = self.audio_path.get()
        output = self.output_path.get()

        if not video or not audio or not output:
            messagebox.showwarning("Missing Data", "Please select the video, audio, and output path.")
            return

        self.merge_btn.config(state=tk.DISABLED, text="Processing...")
        self.status_label.config(text="Extracting metadata...", foreground="blue")
        self.progress_var.set(0)
        
        threading.Thread(target=self.run_ffmpeg, args=(video, audio, output), daemon=True).start()

    def run_ffmpeg(self, video, audio, output):
        # Get duration for progress calculation
        self.total_duration = self.get_duration(video)
        
        self.root.after(0, lambda: self.status_label.config(text="Running FFmpeg, please wait...", foreground="blue"))

        command = [
            "ffmpeg", "-y",
            "-i", video,
            "-i", audio,
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            output
        ]

        try:
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            # We must use Popen and read stderr continuously to get progress
            # ffmpeg outputs progress to stderr
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True, creationflags=creationflags)

            time_regex = re.compile(r"time=(\d{2}:\d{2}:\d{2}\.\d{2})")

            # Read stderr line by line
            for line in process.stderr:
                match = time_regex.search(line)
                if match and self.total_duration > 0:
                    time_str = match.group(1)
                    current_seconds = self.parse_time_to_seconds(time_str)
                    progress = (current_seconds / self.total_duration) * 100
                    
                    # Update progress bar safely
                    self.root.after(0, self.update_progress, progress)

            process.wait()

            if process.returncode == 0:
                self.root.after(0, self.merge_success)
            else:
                self.root.after(0, self.merge_error, "FFmpeg returned a non-zero exit code. Check if the files are valid.")
        
        except FileNotFoundError:
            self.root.after(0, self.ffmpeg_not_found)
        except Exception as e:
            self.root.after(0, self.merge_error, str(e))

    def update_progress(self, val):
        self.progress_var.set(min(val, 100))

    def merge_success(self):
        self.reset_ui()
        self.progress_var.set(100)
        self.status_label.config(text="Process completed successfully!", foreground="green")
        messagebox.showinfo("Success", "The video and audio have been merged successfully.")

    def merge_error(self, error_msg):
        self.reset_ui()
        self.progress_var.set(0)
        self.status_label.config(text="Error during processing.", foreground="red")
        messagebox.showerror("FFmpeg Error", f"An error occurred while processing the files:\n\n{error_msg}")

    def ffmpeg_not_found(self):
        self.reset_ui()
        self.status_label.config(text="FFmpeg not found.", foreground="red")
        messagebox.showerror("Error", "FFmpeg or FFprobe was not found on the system.\nMake sure they are installed and added to your PATH.")

    def reset_ui(self):
        self.merge_btn.config(state=tk.NORMAL, text="Merge Files")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioVideoMerger(root)
    root.mainloop()
