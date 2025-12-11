import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import threading
import time
from audio_control import AudioController
from detector import FlashDetector

class HushButtonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("HushButton 🤫")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        # Controllers
        self.audio = AudioController()
        self.detector = FlashDetector(threshold=200)
        self.cap = cv2.VideoCapture(0)
        
        # State
        self.is_running = True
        self.show_preview = tk.BooleanVar(value=True)

        # UI Components
        self.setup_ui()
        
        # Start Loop
        self.update_loop()

    def setup_ui(self):
        # Style
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12))
        style.configure("Status.TLabel", font=("Helvetica", 24, "bold"))

        # Header
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="HushButton", font=("Helvetica", 18, "bold")).pack(side=tk.LEFT)
        
        # Main Status Indicator
        self.status_frame = ttk.Frame(self.root, padding=20)
        self.status_frame.pack(expand=True, fill=tk.BOTH)
        
        self.status_label = ttk.Label(self.status_frame, text="INITIALIZING...", style="Status.TLabel", justify=tk.CENTER)
        self.status_label.pack(expand=True)
        
        self.update_status_display(self.audio.is_muted())

        # Controls Frame
        controls_frame = ttk.LabelFrame(self.root, text="Settings", padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Audio Device Selector
        ttk.Label(controls_frame, text="Target Device:").pack(anchor=tk.W)
        self.device_var = tk.StringVar()
        devices = self.audio.get_devices_list()
        if devices:
            self.device_var.set(devices[self.audio.current_device_index])
        
        self.device_selector = ttk.Combobox(controls_frame, textvariable=self.device_var, values=devices, state="readonly")
        self.device_selector.pack(fill=tk.X, pady=5)
        self.device_selector.bind("<<ComboboxSelected>>", self.on_device_change)

        # Sensitivity Slider (Pixel Count Threshold)
        # Range: 0 to 307200 (640x480 resolution)
        self.threshold_var = tk.DoubleVar(value=50000)
        # Label with Value
        self.threshold_label = ttk.Label(controls_frame, text=f"Flash Size Threshold: {int(self.threshold_var.get())}")
        self.threshold_label.pack(anchor=tk.W)
        
        self.slider = ttk.Scale(controls_frame, from_=50, to=307200, orient=tk.HORIZONTAL, variable=self.threshold_var, command=self.on_threshold_change)
        self.detector.set_threshold(50000) # Sync initial
        self.slider.pack(fill=tk.X, pady=5)
        
        # Brightness (Score) Meter - Now detecting pixel count
        self.score_label = ttk.Label(controls_frame, text="Current Score: 0")
        self.score_label.pack(anchor=tk.W)
        
        self.brightness_var = tk.DoubleVar(value=0)
        self.brightness_bar = ttk.Progressbar(controls_frame, maximum=307200, variable=self.brightness_var)
        self.brightness_bar.pack(fill=tk.X, pady=5)

        # Preview Toggle
        ttk.Checkbutton(controls_frame, text="Show Camera Preview", variable=self.show_preview).pack(anchor=tk.W, pady=5)

        # Video Preview Frame
        self.video_frame = ttk.Frame(self.root, height=150)
        self.video_frame.pack(fill=tk.X, padx=10, pady=5)
        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack(expand=True)

    def on_device_change(self, event):
        selection_idx = self.device_selector.current()
        self.audio.set_device(selection_idx)
        # Update status immediately
        self.update_status_display(self.audio.is_muted())

    def on_threshold_change(self, value):
        val = float(value)
        self.detector.set_threshold(val)
        self.threshold_label.config(text=f"Flash Size Threshold: {int(val)}")

    def update_status_display(self, is_muted):
        if is_muted:
            self.status_label.config(text="🔇 MUTED", foreground="red")
        else:
            self.status_label.config(text="🎙️ LIVE", foreground="green")

    def update_loop(self):
        if not self.is_running:
            return

        ret, frame = self.cap.read()
        if ret:
            # Process Frame
            event, score = self.detector.process_frame(frame)
            
            # Update UI Logic
            self.brightness_var.set(score)
            self.score_label.config(text=f"Current Score: {int(score)}")
            
            if event == "MUTE":
                if not self.audio.is_muted():
                    self.audio.mute()
                    self.update_status_display(True)
            elif event == "UNMUTE":
                if self.audio.is_muted():
                    self.audio.unmute()
                    self.update_status_display(False)
            
            current_muted = self.audio.is_muted()
            self.update_status_display(current_muted)

            # Update Video Preview
            if self.show_preview.get():
                # Resize for preview
                small_frame = cv2.resize(frame, (160, 120))
                # Convert to RGB
                cv_image = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(cv_image)
                imgtk = ImageTk.PhotoImage(image=pil_image)
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
            else:
                self.video_label.configure(image="")

        self.root.after(30, self.update_loop)

    def on_close(self):
        self.is_running = False
        if self.cap.isOpened():
            self.cap.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = HushButtonApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
