import os
import subprocess
import json
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import threading


class VideoOptimizer:

    def __init__(self, root):
        self.root = root
        self.root.title("Facebook Video Optimizer")
        self.root.geometry("600x400")
        self.config = self.load_config()
        self.create_widgets()

    def load_config(self):
        config_dir = os.path.dirname(__file__)
        software_config_path = os.path.join(config_dir, "software-config.json")
        hardware_config_path = os.path.join(config_dir, "hardware-config.json")
        try:
            with open(software_config_path) as software_config_file:
                software_config = json.load(software_config_file)
            with open(hardware_config_path) as hardware_config_file:
                hardware_config = json.load(hardware_config_file)
            return {"software": software_config, "hardware": hardware_config}
        except FileNotFoundError:
            messagebox.showerror("Error", "Config files not found.")
            self.root.destroy()
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid config files.")
            self.root.destroy()

    def create_widgets(self):
        # File selection button
        self.select_button = Button(self.root, text="Select File", command=self.select_files)
        self.select_button.pack(pady=20)

        # Configuration selection
        self.config_var = StringVar()
        self.config_var.set("software")
        self.config_radio_frame = Frame(self.root)
        software_radio = Radiobutton(
            self.config_radio_frame, text="Software Encoding", variable=self.config_var, value="software"
        )
        software_radio.pack(side="left")
        hardware_radio = Radiobutton(
            self.config_radio_frame, text="Hardware Encoding", variable=self.config_var, value="hardware"
        )
        hardware_radio.pack(side="left")
        self.config_radio_frame.pack()

        # Process button
        self.process_button = Button(self.root, text="Process", command=self.process_selected_files)
        self.process_button.pack(pady=10)

        # Console
        self.console = ScrolledText(self.root, width=80, height=20, bg="black", fg="white", font=("Consolas", 10))
        self.console.pack()

    def select_files(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4")])
        if file_path:
            self.process_button.config(state="normal")
            self.print_to_console(f"Selected file: {file_path}")
            self.file_path = file_path

    def process_selected_files(self):
        file_path = self.file_path
        if file_path:
            self.process_button.config(state="disabled")
            self.print_to_console("Starting video optimization...")
            self.print_to_console(f"Input file: {file_path}")
            self.print_to_console("Output file: _optimized.mp4")
            config_type = self.config_var.get()
            encoder_settings = self.config[config_type]
            if "Encoder" not in encoder_settings:
                messagebox.showerror("Error", "Encoder not found in the config file.")
                return
            encoder = encoder_settings["Encoder"]
            common_params = encoder_settings.get("CommonParams", [])
            output_path = os.path.splitext(file_path)[0] + "_optimized.mp4"
            ffmpeg_cmd = [
                "./ffmpeg/ffmpeg",  # Modify this line to include the correct folder path to the FFmpeg executable
                "-i", file_path,
                "-c:v", encoder
            ] + common_params + [output_path]

            self.print_to_console(f"Encoder: {encoder}")
            self.print_to_console("FFmpeg command:")
            self.print_to_console(" ".join(ffmpeg_cmd))
            self.print_to_console("")

            # Run FFmpeg command in a separate thread
            threading.Thread(target=self.run_ffmpeg_command, args=(ffmpeg_cmd,)).start()

    def run_ffmpeg_command(self, cmd):
        try:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True
            )
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.print_to_console(output.strip())
            if process.returncode == 0:
                self.print_to_console("Video optimization completed successfully!")
            else:
                self.print_to_console("Video optimization failed!")
        except FileNotFoundError:
            self.print_to_console("FFmpeg executable not found. Make sure it is installed.")
        self.process_button.config(state="normal")

    def print_to_console(self, message):
        self.console.insert(END, message + "\n")
        self.console.see(END)


if __name__ == "__main__":
    root = Tk()
    app = VideoOptimizer(root)
    root.mainloop()
