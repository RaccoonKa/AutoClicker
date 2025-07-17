from tkinter import ttk, messagebox
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
        self.check_interval = 500
        self.monitoring_active = True

        self.clicker = AutoClicker()
        self.setup_ui()
        self.register_hotkeys()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.load_templates()
        self.start_monitoring()

    def load_templates(self):
        self.templates = []
        self.template_sizes = []
        assets_dir = "assets"
        valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp')

        if not os.path.exists(assets_dir):
            messagebox.showerror("Error", f"Folder {assets_dir} not found!")
            return

        for filename in os.listdir(assets_dir):
            if filename.lower().endswith(valid_extensions):
                path = os.path.join(assets_dir, filename)
                try:
                    img = cv2.imread(path, cv2.IMREAD_COLOR)
                    if img is not None:
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        self.templates.append(gray)
                        self.template_sizes.append((img.shape[1], img.shape[0]))
                        print(f"Template is uploaded: {filename}")
                except Exception as e:
                    print(f"Download error {filename}: {str(e)}")

        if not self.templates:
            messagebox.showerror("Error", "Not a single template has been uploaded!")
        else:
            self.template_count_label.config(text=f"Templates: {len(self.templates)}")

    def start_monitoring(self):
        if self.templates:
            self.root.after(self.check_interval, self.check_image)

    def setup_ui(self):
        style = ttk.Style()
        style.configure("TButton", padding=6)

        points_frame = ttk.LabelFrame(self.root, text="Click Positions")
        points_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.points_list = tk.Listbox(points_frame, height=8)
        self.points_list.pack(padx=5, pady=5, fill="both", expand=True)

        control_frame = ttk.Frame(self.root)
        control_frame.pack(padx=10, pady=5, fill="x")

        ttk.Button(control_frame, text="Add current position (1)",
                   command=self.add_current_position).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Delete position",
                   command=self.remove_selected).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Clear all",
                   command=self.clear_points).pack(side="left", padx=5)

        interval_frame = ttk.Frame(self.root)
        interval_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(interval_frame, text="Interval (sec):").pack(side="left")
        self.interval_var = tk.DoubleVar(value=1.0)
        interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=5)
        interval_entry.pack(side="left", padx=5)

        ttk.Label(interval_frame, text="Click delay (sec):").pack(side="left", padx=(10, 0))
        self.point_delay_var = tk.DoubleVar(value=0.0)
        ttk.Entry(interval_frame, textvariable=self.point_delay_var, width=5).pack(side="left", padx=5)

        image_frame = ttk.LabelFrame(self.root, text="Image detection settings")
        image_frame.pack(padx=10, pady=5, fill="x")

        ttk.Label(image_frame, text="Detection threshold:").pack(side="left")
        self.threshold_var = tk.IntVar(value=self.detection_threshold)
        threshold_entry = ttk.Entry(image_frame, textvariable=self.threshold_var, width=5)
        threshold_entry.pack(side="left", padx=5)

        ttk.Button(image_frame, text="Set", command=self.set_threshold).pack(side="left", padx=5)

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

        ttk.Button(second_control_frame, text="Add current position (2)",
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

        action_frame = ttk.Frame(self.root)
        action_frame.pack(padx=10, pady=10, fill="x")

        self.toggle_btn = ttk.Button(action_frame, text="Start (0)", command=self.toggle_clicker)
        self.toggle_btn.pack(side="left", padx=5)

        self.hotkey_var = tk.BooleanVar(value=True)
        hotkey_check = ttk.Checkbutton(action_frame, text="Keyboard shortcuts are active",
                                       variable=self.hotkey_var, command=self.toggle_hotkeys)
        hotkey_check.pack(side="right", padx=5)

        ttk.Label(image_frame, text="Threshold of match:").pack(side="left")
        self.threshold_var = tk.DoubleVar(value=self.match_threshold)
        threshold_entry = ttk.Entry(image_frame, textvariable=self.threshold_var, width=5)
        threshold_entry.pack(side="left", padx=5)

        ttk.Button(image_frame, text="Recognition test",
                   command=self.test_image_recognition).pack(side="left", padx=5)



    def add_current_position(self):
        x, y = pyautogui.position()
        self.clicker.add_point(x, y)
        self.points_list.insert(tk.END, f"X: {x}, Y: {y}")

    def set_threshold(self):
        try:
            self.detection_threshold = int(self.threshold_var.get())
            messagebox.showinfo("Success", f"The threshold is set: {self.detection_threshold}")
        except ValueError:
            messagebox.showerror("Error", "Enter an integer")

    def add_second_point(self):
        x, y = pyautogui.position()
        self.clicker.add_second_point(x, y)
        self.second_points_list.insert(tk.END, f"X: {x}, Y: {y}")

    def remove_second_point(self):
        selection = self.second_points_list.curselection()
        if selection:
            index = selection[0]
            self.second_points_list.delete(index)
            self.clicker.second_points.pop(index)

    def clear_second_points(self):
        self.second_points_list.delete(0, tk.END)
        self.clicker.second_points = []

    def check_image(self):
        if self.monitoring_active:
            try:
                screenshot = pyautogui.screenshot()
                screenshot_np = np.array(screenshot)
                screen_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

                if self.clicker.running and not self.second_algorithm_active and self.templates:
                    found = False
                    for template, size in zip(self.templates, self.template_sizes):
                        if template.shape[0] > screen_gray.shape[0] or template.shape[1] > screen_gray.shape[1]:
                            continue

                        res = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                        if max_val >= self.match_threshold:
                            found = True
                            break

                    if found:
                        self.detection_count += 1
                        self.counter_label.config(text=f"Found: {self.detection_count}")

                        if self.detection_count >= self.detection_threshold:
                            self.detection_count = 0
                            self.counter_label.config(text="Found: 0")
                            self.second_algorithm_active = True
                            self.execute_second_algorithm()
            except Exception as e:
                print(f"Monitoring error: {e}")

            self.root.after(self.check_interval, self.check_image)

    def test_image_recognition(self):
        try:
            screenshot = ImageGrab.grab()
            screenshot_np = np.array(screenshot)
            screen_gray = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2GRAY)

            found = False
            for template, size in zip(self.templates, self.template_sizes):
                if template.shape[0] > screen_gray.shape[0] or template.shape[1] > screen_gray.shape[1]:
                    continue

                result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                if max_val >= self.match_threshold:
                    top_left = max_loc
                    bottom_right = (top_left[0] + size[0], top_left[1] + size[1])
                    cv2.rectangle(screenshot_np, top_left, bottom_right, (0, 255, 0), 2)

                    output_path = "detection_result.jpg"
                    cv2.imwrite(output_path, cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR))

                    messagebox.showinfo("Success",
                                        f"Image found (coincidence: {max_val:.2f})\n"
                                        f"The result is saved in: {output_path}")
                    found = True
                    break

            if not found:
                messagebox.showinfo("Not found",
                                    "No patterns detected\n"
                                    "Try to reduce the match threshold")
        except Exception as e:
            messagebox.showerror("Error", f"Testing error: {str(e)}")

    def execute_second_algorithm(self):
        if self.clicker.second_points:
            was_running = self.clicker.running
            if was_running:
                self.clicker.stop()
                self.toggle_btn.config(text="Start (0)")

            try:
                interval = float(self.second_interval_var.get())
                self.clicker.set_second_interval(interval)
                self.clicker.execute_second_algorithm()
            except ValueError:
                messagebox.showerror("Error", "Incorrect interval")

            self.second_algorithm_active = False
            if was_running:
                self.clicker.start()
                self.toggle_btn.config(text="Stop (0)")
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
                self.clicker.set_interval(interval)
                if self.clicker.start():
                    self.toggle_btn.config(text="Stop (0)")
            except ValueError:
                messagebox.showerror("Error", "Incorrect interval")
        else:
            self.clicker.stop()
            self.toggle_btn.config(text="Start (0)")

    def register_hotkeys(self):
        keyboard.add_hotkey('1', self.add_current_position)
        keyboard.add_hotkey('0', self.toggle_clicker)
        keyboard.add_hotkey('2', self.add_second_point)
        keyboard.add_hotkey('8', self.execute_second_algorithm)

    def toggle_hotkeys(self):
        state = self.hotkey_var.get()
        self.clicker.toggle_hotkey(state)

    def on_close(self):
        self.monitoring_active = False
        self.clicker.stop()
        self.root.destroy()
