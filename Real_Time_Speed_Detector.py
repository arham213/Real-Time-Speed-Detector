import math

import cv2
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import time

class CameraApp:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)

        self.video_source = video_source
        self.vid = cv2.VideoCapture(self.video_source)

        self.canvas = tk.Canvas(window, width=self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), height=self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()

        self.label = tk.Label(window, text="Calculating...")
        self.label.pack(padx=10, pady=10)

        self.btn_snapshot = tk.Button(window, text="Snapshot", command=self.snapshot)
        self.btn_snapshot.pack(padx=10, pady=10)

        self.prev_frame = None
        self.prev_time = time.time()  # Initialize the time

        self.update()
        self.window.mainloop()

    def snapshot(self):
        ret, frame = self.vid.read()
        if ret:
            cv2.imwrite("snapshot.png", cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    def update(self):
        ret, frame = self.vid.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if self.prev_frame is not None:
                frame_diff = cv2.absdiff(gray, self.prev_frame)
                _, thresh = cv2.threshold(frame_diff, 130, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                combined_contour = self.combine_contours(contours)

                if combined_contour is not None:
                    x, y, w, h = cv2.boundingRect(combined_contour)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # Calculate the speed of the detected object
                    speed = self.calculate_speed(w, h)
                    self.label.config(text=f"Object Speed: {speed} pixels per second")

            self.photo = self.convert_to_tkinter_image(frame)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

            self.prev_frame = gray.copy()

        self.window.after(10, self.update)

    def calculate_speed(self, width, height):
        # Assuming a distance of 1 meter between the camera and the detected object
        distance_meters = 1.0
        pixels_per_meter = max(width, height) / distance_meters

        # Calculate time elapsed since the previous frame
        current_time = time.time()
        elapsed_time = current_time - self.prev_time

        # Calculate speed in pixels per second
        speed_pixels_per_second = pixels_per_meter / elapsed_time

        # Update the previous time for the next iteration
        self.prev_time = current_time

        return speed_pixels_per_second
    def combine_contours(self, contours):
        if len(contours) == 0:
            return None

        combined_contour = np.concatenate(contours)

        for contour in contours:
            if cv2.contourArea(contour) > 50:  # Adjust the area threshold as needed
                continue

            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            if cv2.isContourConvex(approx):
                combined_contour = np.concatenate((combined_contour, contour))

        return combined_contour

    def convert_to_tkinter_image(self, frame):
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img = ImageTk.PhotoImage(image=img)
        return img

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Set your USB camera source (you may need to change the index)
video_source = 1

root = tk.Tk()
app = CameraApp(root, "Camera App", video_source)
