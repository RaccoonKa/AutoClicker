# 🤖 Smart Vision AutoClicker

Smart autoclicker with image recognition based on OpenCV. He doesn't just click on coordinates, but "sees" the screen and is able to perform complex algorithms when he finds the right objects.

## ✨ The main features

* **Computer vision:** Uses `cv2.matchTemplate` to search for images on the screen in real time.
* **Two-level automation:**
    * Basic clicker with interval and delay settings.
    * The second algorithm, which is launched after successful detection of the target image.
* **Flexible settings:** You can change the threshold, the verification intervals, and the number of repetitions for the second algorithm.
* **Convenient operation:** Keyboard shortcuts for quick settings right in the process.

## ⌨️ Keyboard shortcuts

| Key | Action |
| :--- | :--- |
| **F7** | Add the current cursor position to the main list. |
| **F8** | Add the current position to the second algorithm. |
| **F9** | Start/Stop the clicker. |
| **F10** | Manual start of the second algorithm. |

## 🏗 Branch structure

* 🚀 **`release`**: The stable version of the program. Only the verified code that is ready to work gets here.
* 🧪 **`develop`**: A testing ground for experiments. There are new recognition algorithms and features that are still being tested.
