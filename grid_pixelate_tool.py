import tkinter as tk
from tkinter import filedialog
import numpy as np
from PIL import Image, ImageTk
from sklearn.cluster import KMeans


def pixelate(img_array, tile_w, tile_h):
    """
    Return a new numpy array pixelated into tile_w x tile_h blocks.
    Each block is assigned the average color of its pixels.
    """
    h, w = img_array.shape[:2]
    pixelated = img_array.copy()
    
    for y in range(0, h, tile_h):
        for x in range(0, w, tile_w):
            block = pixelated[y:y+tile_h, x:x+tile_w]
            avg_color = block.mean(axis=(0, 1))
            block[:] = avg_color
    
    return pixelated

class PixelateApp(tk.Tk):
    def __init__(self, w = 5, h = 5, s = 1):
        super().__init__()
        self.title("Numpy Rectangular Pixelation (no imageio)")

        # Control frame for grid layout
        controls_frame = tk.Frame(self)
        controls_frame.pack()

        self.tile_w_var = tk.IntVar(value=w)
        self.tile_h_var = tk.IntVar(value=h)
        self.scale_var = tk.DoubleVar(value=s)
        self.anz_maschen_var = tk.IntVar()
        self.anz_reihen_var = tk.IntVar()
        self.anz_farben_var = tk.IntVar(value = 2)

        # Tile Width
        tk.Label(controls_frame, text="Tile Width:").grid(row=0, column=0)
        self.tile_w_scale = tk.Scale(
            controls_frame, from_=1, to=100, orient=tk.HORIZONTAL,
            variable=self.tile_w_var, command=self.update_preview
        )
        self.tile_w_scale.grid(row=1, column=0)

        # Tile Height
        tk.Label(controls_frame, text="Tile Height:").grid(row=0, column=1)
        self.tile_h_scale = tk.Scale(
            controls_frame, from_=1, to=100, orient=tk.HORIZONTAL,
            variable=self.tile_h_var, command=self.update_preview
        )
        self.tile_h_scale.grid(row=1, column=1)

        

        # Scale
        tk.Label(controls_frame, text="Scale:").grid(row=0, column=2)
        self.scale_var_scale = tk.Scale(
            controls_frame, from_=0.2, to=5, resolution=0.1,
            orient=tk.HORIZONTAL, variable=self.scale_var,
            command=self.update_preview
        )
        self.scale_var_scale.grid(row=1, column=2)

        # Anz. Maschen
        tk.Label(controls_frame, text="Anz. Maschen").grid(row=0, column=3)
        self.anz_maschen_entry = tk.Entry(controls_frame, textvariable=self.anz_maschen_var, state="readonly")
        self.anz_maschen_entry.grid(row=1, column=3)

        # Anz. Reihen
        tk.Label(controls_frame, text="Anz. Reihen").grid(row=0, column=4)
        self.anz_reihen_entry = tk.Entry(controls_frame, textvariable=self.anz_reihen_var, state="readonly")
        self.anz_reihen_entry.grid(row=1, column=4)

        # Anz. Farben
        tk.Label(controls_frame, text="Anz. Farben").grid(row=0, column=5)
        self.anz_farben_entry = tk.Entry(controls_frame, textvariable=self.anz_farben_var)
        self.anz_farben_entry.grid(row=1, column=5)

        # Buttons
        self.open_btn = tk.Button(controls_frame, text="Open Image", command=self.open_image)
        self.open_btn.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.save_btn = tk.Button(controls_frame, text="Save Image", command=self.save_image)
        self.save_btn.grid(row=2, column=2, columnspan=3, sticky="ew")

        # Preview label (not in grid, takes remaining space)
        self.preview_label = tk.Label(self)
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        # data properties
        self.original_array = None
        self.preview_imgtk = None

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            img = Image.open(file_path).convert("RGB")  # Ensure 3-channel
            self.original_array = np.array(img)
            self.update_preview()
            
    def save_image(self):
        if hasattr(self, 'current_image') and self.current_image is not None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            if file_path:
                self.current_image.save(file_path)

    def update_preview(self, *args):
        if self.original_array is not None:
            pw = self.tile_w_var.get()
            ph = self.tile_h_var.get()


            # scale image within grid
            img = Image.fromarray(self.original_array.astype(np.uint8))
            w, h = img.size
            scale = self.scale_var.get()
            scaled_img = img.resize((int(w*scale), int(h*scale)), Image.NEAREST)
            scaled_array = np.array(scaled_img)
            
            pix_array = pixelate(scaled_array, pw, ph)

            pix_array = self.reduce_colors_kmeans(pix_array, self.anz_farben_var.get())

            # Draw grid lines on the pixelated image (using black lines).
            h, w, _ = pix_array.shape

            if(min(ph,pw) > 2):
                # Horizontal lines
                for y in range(ph, h, ph):
                    pix_array[y, :, :] = [0, 0, 0]
                self.anz_reihen_var.set(h // ph)

                # Vertical lines
                for x in range(pw, w, pw):
                    pix_array[:, x, :] = [0, 0, 0]
                self.anz_maschen_var.set(w // pw)

            # Convert numpy array back to PIL Image for display
            pix_img = Image.fromarray(pix_array.astype(np.uint8))
            self.current_image = pix_img
            self.preview_imgtk = ImageTk.PhotoImage(pix_img)
            self.preview_label.config(image=self.preview_imgtk)

    def reduce_colors_kmeans(self, img: np.array, n_colors: int) -> np.array:
        # Cluster using KMeans
        pixels = img.reshape(-1, 3)
        kmeans = KMeans(n_clusters=n_colors, n_init='auto')
        kmeans.fit(pixels)
        centers = kmeans.cluster_centers_
        labels = kmeans.labels_

        # Replace each pixel with its cluster's average color
        quantized = centers[labels].reshape(img.shape).astype(np.uint8)

        return quantized


class RectangleRatioCalculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rectangle Ratio Calculator")

        tk.Label(self, text="Anzahl Maschen:").grid(row=0, column=0)
        self.entry_x = tk.Entry(self)
        self.entry_x.grid(row=0, column=1)

        tk.Label(self, text="Anzahl Reihen:").grid(row=1, column=0)
        self.entry_y = tk.Entry(self)
        self.entry_y.grid(row=1, column=1)

        tk.Label(self, text="Länge Reihen").grid(row=2, column=0)
        self.entry_length = tk.Entry(self)
        self.entry_length.grid(row=2, column=1)

        tk.Label(self, text="Länge Maschen").grid(row=3, column=0)
        self.entry_width = tk.Entry(self)
        self.entry_width.grid(row=3, column=1)

        tk.Button(self, text="Weiter", command=self.calculate_ratio).grid(row=4, column=0, columnspan=2)
        self.result_label = tk.Label(self, text="")
        self.result_label.grid(row=5, column=0, columnspan=2)

        self.ration = None

    def calculate_ratio(self):
        try:
            nx = float(self.entry_x.get())
            ny = float(self.entry_y.get())
            length = float(self.entry_length.get())
            width = float(self.entry_width.get())
            ratio = (width / nx) / (length / ny)
            self.result_label.config(text=f"Rectangle Ratio: {ratio:.2f}")
            self.ratio = ratio
            self.destroy()
        except ValueError:
            self.result_label.config(text="Invalid input.")
    



if __name__ == "__main__":
    calc_app = RectangleRatioCalculator()
    calc_app.mainloop()
    if(calc_app.ration != None):
        ratio = calc_app.ratio
        height = 10
        width = round(height * ratio)
        px_app = PixelateApp(width, height, 2)
    else:
        px_app = PixelateApp()
    px_app.attributes('-zoomed', True)
    px_app.mainloop()
