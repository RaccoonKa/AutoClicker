from app import AutoClickerApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap("assets/icon.ico")
    app = AutoClickerApp(root)
    root.mainloop()