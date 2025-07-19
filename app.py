from tkinter import ttk, messagebox, filedialog
from autoclicker import AutoClicker
import tkinter as tk
import cv2
import numpy as np
from PIL import ImageGrab
import pyautogui
import keyboard
import os


class AutoClickerApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Clicker")
        self.root.geometry("950x950")
        self.root.resizable(False, False)

        self.templates = []
        self.template_sizes = []
        self.detection_count = 0
        self.detection_threshold = 5
        self.second_algorithm_active = False
        self.match_threshold = 0.8
        self.check_interval = 1000
        self.check_interval_sec = tk.DoubleVar(value=1.0)
        self.monitoring_active = False
        self.templates_dir = ""

        self.clicker = AutoClicker()
        self.setup_ui()
        self.register_hotkeys()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_templates()

    def select_templates_directory(self):
        dir_path = filedialog.askdirectory(
            title="Select Folder",
            initialdir=self.templates_dir
        )
        if dir_path:
            self.templates_dir = dir_path
            self.dir_label.config(text=f"Folder: {dir_path}")
            self.load_templates()

    def load_templates(self):
        self.templates = []
        self.template_sizes = []
        assets_dir = self.templates_dir
        if not assets_dir:
            self.template_count_label.config(text="Templates: 0")
            return
        valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp')

        if not os.path.exists(assets_dir):
            messagebox.showerror("Error", f"Folder {assets_dir} not found!")
            return

        for filename in os.listdir(assets_dir):
            if filename.lower().endswith(valid_extensions):
                try:
                    path = os.path.normpath(os.path.join(assets_dir, filename))
                    if not os.access(path, os.R_OK):
                        print(f"File is not readable: {filename}")
                        continue

                    with open(path, 'rb') as f:
                        img_array = np.frombuffer(f.read(), dtype=np.uint8)
                        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

                    if img is None:
                        print(f"Failed to load image (may be corrupted or unsupported format): {filename}")
                        continue

                    self.templates.append(img)
                    self.template_sizes.append((img.shape[1], img.shape[0]))
                    print(f"Template loaded: {filename}")
                except Exception as e:
                    print(f"Error loading {filename}: {str(e)}")
                    messagebox.showerror("Loading Error",
                                         f"Failed to load image: {filename}\nError: {str(e)}")

        if not self.templates:
            messagebox.showerror("Error", "No valid templates loaded!")
        else:
            self.template_count_label.config(text=f"Templates: {len(self.templates)}")

    def start_monitoring(self):
        if self.templates and not self.monitoring_active:
            self.monitoring_active = True
            self.root.after(self.check_interval, self.check_image)

    def stop_monitoring(self):
        self.monitoring_active = False

    def setup_ui(self):

        powered_label = ttk.Label(self.root, text="Powered by Mr_RaccoonKa", font=('Roboto', 8))
        powered_label.pack(side="top", anchor="ne", padx=10, pady=5)

        style = ttk.Style()
        style.configure("TButton", padding=6)

        points_frame = ttk.LabelFrame(self.root, text="Click Positions")
        points_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.points_list = tk.Listbox(points_frame, height=4)
        self.points_list.pack(padx=5, pady=5, fill="both", expand=True)

        control_frame = ttk.Frame(points_frame)
        control_frame.pack(fill="x")

        ttk.Button(control_frame, text="Add current position (F7)",
                   command=self.add_current_position).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Delete position",
                   command=self.remove_selected).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Clear all",
                   command=self.clear_points).pack(side="left", padx=5)

        interval_frame = ttk.Frame(points_frame)
        interval_frame.pack(fill="x")

        ttk.Label(interval_frame, text="Interval (sec):").pack(side="left")
        self.interval_var = tk.DoubleVar(value=1.0)
        ttk.Entry(interval_frame, textvariable=self.interval_var, width=5).pack(side="left", padx=5)

        ttk.Label(interval_frame, text="Click delay (sec):").pack(side="left", padx=(10, 0))
        self.point_delay_var = tk.DoubleVar(value=0.0)
        ttk.Entry(interval_frame, textvariable=self.point_delay_var, width=5).pack(side="left", padx=5)

        image_frame = ttk.LabelFrame(self.root, text="Image detection settings")
        image_frame.pack(padx=10, pady=5, fill="x")

        dir_frame = ttk.Frame(image_frame)
        dir_frame.pack(fill="x", pady=(0, 5))

        ttk.Button(
            dir_frame,
            text="Select Folder",
            command=self.select_templates_directory
        ).pack(side="left", padx=(0, 5))

        self.dir_label = ttk.Label(dir_frame, text=f"Folder: {self.templates_dir}")
        self.dir_label.pack(side="left")

        threshold_frame = ttk.Frame(image_frame)
        threshold_frame.pack(fill="x", pady=5)

        ttk.Label(threshold_frame, text="Detection threshold:").pack(side="left")
        self.threshold_var = tk.IntVar(value=self.detection_threshold)
        threshold_entry = ttk.Entry(threshold_frame, textvariable=self.threshold_var, width=5)
        threshold_entry.pack(side="left", padx=5)
        self.threshold_var.trace("w", self.update_threshold)

        ttk.Label(threshold_frame, text="Check interval (sec):").pack(side="left", padx=(10, 0))
        self.check_interval_sec = tk.DoubleVar(value=1.0)
        interval_entry = ttk.Entry(threshold_frame, textvariable=self.check_interval_sec, width=5)
        interval_entry.pack(side="left", padx=5)
        self.check_interval_sec.trace("w", self.update_check_interval)

        self.counter_label = ttk.Label(image_frame, text="Detected: 0")
        self.counter_label.pack(side="right", padx=5)

        self.template_count_label = ttk.Label(image_frame, text="Templates: 0")
        self.template_count_label.pack(side="left", padx=5)

        second_alg_frame = ttk.LabelFrame(self.root, text="Second click positions")
        second_alg_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.second_points_list = tk.Listbox(second_alg_frame, height=4)
        self.second_points_list.pack(padx=5, pady=5, fill="both", expand=True)

        second_control_frame = ttk.Frame(second_alg_frame)
        second_control_frame.pack(fill="x")

        ttk.Button(second_control_frame, text="Add current position (F8)",
                   command=self.add_second_point).pack(side="left", padx=5)
        ttk.Button(second_control_frame, text="Delete position",
                   command=self.remove_second_point).pack(side="left", padx=5)
        ttk.Button(second_control_frame, text="Clear all",
                   command=self.clear_second_points).pack(side="left", padx=5)

        second_interval_frame = ttk.Frame(second_alg_frame)
        second_interval_frame.pack(fill="x")

        ttk.Label(second_interval_frame, text="Interval (sec):").pack(side="left")
        self.second_interval_var = tk.DoubleVar(value=0.5)
        second_interval_entry = ttk.Entry(second_interval_frame,
                                          textvariable=self.second_interval_var, width=5)
        second_interval_entry.pack(side="left", padx=5)

        ttk.Label(second_interval_frame, text="Click delay (sec):").pack(side="left", padx=(10, 0))
        self.second_point_delay_var = tk.DoubleVar(value=0.0)
        ttk.Entry(second_interval_frame, textvariable=self.second_point_delay_var, width=5).pack(side="left", padx=5)

        ttk.Label(second_interval_frame, text="Repeats:").pack(side="left", padx=(10, 0))
        self.second_repeats_var = tk.IntVar(value=1)
        ttk.Entry(second_interval_frame, textvariable=self.second_repeats_var, width=5).pack(side="left", padx=5)

        action_frame = ttk.Frame(self.root)
        action_frame.pack(padx=10, pady=10, fill="x")

        button_frame = ttk.Frame(action_frame)
        button_frame.pack(side="left", padx=5)

        self.toggle_btn = ttk.Button(action_frame, text="Start (F9)", command=self.toggle_clicker)
        self.toggle_btn.pack(side="left", padx=5)

        exit_btn = ttk.Button(action_frame, text="Exit", command=self.on_close)
        exit_btn.pack(side="left", padx=5)

        self.hotkey_var = tk.BooleanVar(value=True)
        hotkey_check = ttk.Checkbutton(action_frame, text="Keyboard shortcuts are active",
                                       variable=self.hotkey_var, command=self.toggle_hotkeys)
        hotkey_check.pack(side="right", padx=5)

        ttk.Label(image_frame, text="Threshold of match:").pack(side="left")
        self.match_threshold_var = tk.DoubleVar(value=self.match_threshold)
        threshold_entry = ttk.Entry(image_frame, textvariable=self.match_threshold_var, width=5)
        threshold_entry.pack(side="left", padx=5)

        ttk.Button(image_frame, text="Recognition test",
                   command=self.test_image_recognition).pack(side="left", padx=5)

    def add_current_position(self):
        x, y = pyautogui.position()
        self.clicker.add_point(x, y)
        self.points_list.insert(tk.END, f"X: {x}, Y: {y}")

    def set_threshold(self): ...

    def update_threshold(self, *args):
        try:
            self.detection_threshold = int(self.threshold_var.get())
        except ValueError:
            pass

    def update_check_interval(self, *args):
        try:
            interval_sec = float(self.check_interval_sec.get())
            if interval_sec > 0:
                self.check_interval = int(interval_sec * 1000)
        except ValueError:
            pass

    def add_second_point(self):
        x, y = pyautogui.position()
        self.clicker.add_second_point(x, y)
        self.second_points_list.insert(tk.END, f"X: {x}, Y: {y}")
        if self.clicker.running and not self.monitoring_active:
            self.start_monitoring()

    def remove_second_point(self):
        selection = self.second_points_list.curselection()
        if selection:
            index = selection[0]
            self.second_points_list.delete(index)
            self.clicker.second_points.pop(index)
            if not self.clicker.second_points and self.monitoring_active:
                self.stop_monitoring()

    def clear_second_points(self):
        self.second_points_list.delete(0, tk.END)
        self.clicker.second_points = []
        if self.monitoring_active:
            self.stop_monitoring()

    def check_image(self):
        if (self.monitoring_active and self.clicker.running and self.clicker.second_points):
            try:
                screenshot = np.array(ImageGrab.grab())
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

                screen_height, screen_width = screenshot.shape[:2]
                found = False

                for idx, template in enumerate(self.templates):
                    tpl_height, tpl_width = template.shape[:2]

                    if tpl_height > screen_height or tpl_width > screen_width:
                        continue

                    res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                    if max_val >= self.match_threshold:
                        found = True
                        break

                if found:
                    self.detection_count += 1
                    self.counter_label.config(text=f"Detected: {self.detection_count}")

                    if self.detection_count >= self.detection_threshold:
                        self.detection_count = 0
                        self.counter_label.config(text="Detected: 0")
                        self.second_algorithm_active = True
                        self.execute_second_algorithm()
            except Exception as e:
                print(f"Monitoring error: {e}")

            if (self.monitoring_active and self.clicker.running and self.clicker.second_points):
                self.root.after(self.check_interval, self.check_image)
            else:
                self.stop_monitoring()

    def test_image_recognition(self):
        try:
            screenshot = np.array(ImageGrab.grab())
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)

            best_match = {
                "max_val": 0,
                "max_loc": None,
                "size": None,
                "template_idx": None
            }

            screen_height, screen_width = screenshot.shape[:2]

            for idx, template in enumerate(self.templates):
                tpl_height, tpl_width = template.shape[:2]

                if tpl_height > screen_height or tpl_width > screen_width:
                    continue

                res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                if max_val > best_match["max_val"]:
                    best_match = {
                        "max_val": max_val,
                        "max_loc": max_loc,
                        "size": (tpl_width, tpl_height),
                        "template_idx": idx
                    }

            if best_match["max_val"] >= self.match_threshold:
                top_left = best_match["max_loc"]
                bottom_right = (top_left[0] + best_match["size"][0], top_left[1] + best_match["size"][1])
                cv2.rectangle(screenshot, top_left, bottom_right, (0, 255, 0), 2)

                output_path = "detection_result.jpg"
                cv2.imwrite(output_path, screenshot)

                template_name = os.listdir(self.templates_dir)[best_match["template_idx"]]
                messagebox.showinfo(
                    "Success",
                    f"Image found: {template_name}\n"
                    f"Match value: {best_match['max_val']:.2f}\n"
                    f"Result saved to: {output_path}"
                )
            else:
                messagebox.showinfo(
                    "Not found",
                    "No templates detected\n"
                    "Try lowering the match threshold"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Testing error: {str(e)}")

    def execute_second_algorithm(self):
        if self.clicker.second_points:
            was_running = self.clicker.running
            if was_running:
                self.clicker.stop()
                self.toggle_btn.config(text="Start (F9)")

            try:
                interval = float(self.second_interval_var.get())
                repeats = int(self.second_repeats_var.get())
                point_delay = float(self.second_point_delay_var.get())
                self.clicker.set_second_interval(interval)
                self.clicker.set_second_algorithm_repeats(repeats)
                self.clicker.second_point_delay = point_delay
                for _ in range(repeats):
                    if not self.second_algorithm_active:
                        break
                    self.clicker.execute_second_algorithm()
            except ValueError:
                messagebox.showerror("Error", "Incorrect interval or repeats value")

            self.second_algorithm_active = False
            if was_running:
                self.clicker.start()
                self.toggle_btn.config(text="Stop (F9)")
        else:
            messagebox.showwarning("Attention", "The second algorithm is not configured")
            self.second_algorithm_active = False

    def remove_selected(self):
        selection = self.points_list.curselection()
        if selection:
            index = selection[0]
            self.points_list.delete(index)
            self.clicker.points.pop(index)

    def clear_points(self):
        self.points_list.delete(0, tk.END)
        self.clicker.points = []

    def toggle_clicker(self):
        if not self.clicker.running:
            try:
                interval = float(self.interval_var.get())
                point_delay = float(self.point_delay_var.get())
                self.clicker.set_interval(interval)
                self.clicker.point_delay = point_delay
                if self.clicker.start():
                    self.toggle_btn.config(text="Stop (F9)")
                    if self.clicker.second_points:
                        self.start_monitoring()
            except ValueError:
                messagebox.showerror("Error", "Incorrect interval")
        else:
            self.clicker.stop()
            self.toggle_btn.config(text="Start (F9)")
            self.stop_monitoring()

    def register_hotkeys(self):
        keyboard.add_hotkey('f7', self.add_current_position)
        keyboard.add_hotkey('f9', self.toggle_clicker)
        keyboard.add_hotkey('f8', self.add_second_point)
        keyboard.add_hotkey('f10', self.execute_second_algorithm)

    def toggle_hotkeys(self):
        state = self.hotkey_var.get()
        self.clicker.toggle_hotkey(state)

    def on_close(self):
        self.monitoring_active = False
        self.clicker.stop()
        self.root.destroy()
