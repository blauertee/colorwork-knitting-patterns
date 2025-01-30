import tkinter as tk
from tkinter import filedialog
import numpy as np
from PIL import Image, ImageTk
from sklearn.cluster import KMeans

"""
The Pupose of this app is to create rasterized images for knitting colorwork
you can open an image and tell the program how many colors, and stitches you want
to do. You can enter the properties of you wool and needle size to scale the 
width height ratio of each raster tile.
"""



class PixelateApp(tk.Tk):
    def __init__(self, w=5, h=5, s=1):
        super().__init__()
        self.title("Knitting Colorwork Image rasterizer")

        # Frame
        controls_frame = tk.Frame(self)
        controls_frame.pack()

        self.single_stitch_length_var = tk.IntVar(value=w)
        self.single_row_length_var = tk.IntVar(value=h)
        

        self.scale_var = tk.DoubleVar(value=s)
        self.amount_stitches_var = tk.IntVar(value = 30)
        self.amount_rows_var = tk.IntVar()
        self.amount_colors_var = tk.IntVar(value=2)

        self.ratio_calc_num_stitches_var = tk.IntVar(value=1)
        self.ratio_calc_num_rows_var = tk.IntVar(value=1)
        self.ratio_calc_length_stitches_var = tk.DoubleVar(value=1)
        self.ratio_calc_length_rows_var = tk.DoubleVar(value=1)
        self.ratio_var = tk.DoubleVar(value=1.0)  # For read-only ratio


        # Tile Width
        tk.Label(controls_frame, text="Tile Width (px):").grid(row=0, column=0)
        self.tile_w_entry = tk.Entry(controls_frame, textvariable=self.single_stitch_length_var, state="readonly")
        self.tile_w_entry.grid(row=1, column=0)

        # Tile Height
        tk.Label(controls_frame, text="Tile Height (px):").grid(row=0, column=1)
        self.tile_h_entry = tk.Entry(controls_frame, textvariable=self.single_row_length_var, state="readonly")
        self.tile_h_entry.grid(row=1, column=1)


        # Number of stitches
        tk.Label(controls_frame, text="Number of stitches:").grid(row=0, column=3)
        self.amount_stitches_entry = tk.Entry(controls_frame, textvariable=self.amount_stitches_var)
        self.amount_stitches_entry.grid(row=1, column=3)
        self.amount_stitches_entry.bind("<Return>", lambda e: self.update_preview())

        # Number of rows 
        tk.Label(controls_frame, text="Number of rows:").grid(row=0, column=4)
        self.amount_rows_entry = tk.Entry(controls_frame, textvariable=self.amount_rows_var, state="readonly")
        self.amount_rows_entry.grid(row=1, column=4)

        # Number of colors
        tk.Label(controls_frame, text="Number of colors:").grid(row=0, column=5)
        self.amount_colors_entry = tk.Entry(controls_frame, textvariable=self.amount_colors_var)
        self.amount_colors_entry.grid(row=1, column=5)
        self.amount_colors_entry.bind("<Return>", lambda e: self.update_preview())

        # Ratio calculator
        tk.Label(controls_frame, text="An amount of").grid(row=0, column=6)
        self.ratio_calc_num_stitches_entry = tk.Entry(
            controls_frame, textvariable=self.ratio_calc_num_stitches_var
        )
        self.ratio_calc_num_stitches_entry.grid(row=0, column=7)
        tk.Label(controls_frame, text="stitches has length").grid(row=0, column=8)
        self.ratio_calc_length_stitches_entry = tk.Entry(
            controls_frame, textvariable=self.ratio_calc_length_stitches_var
        )
        self.ratio_calc_length_stitches_entry.grid(row=0, column=9)

        tk.Label(controls_frame, text="An amount of").grid(row=1, column=6)
        self.ratio_calc_num_rows_entry = tk.Entry(
            controls_frame, textvariable=self.ratio_calc_num_rows_var
        )
        self.ratio_calc_num_rows_entry.grid(row=1, column=7)
        tk.Label(controls_frame, text="rows has length").grid(row=1, column=8)
        self.ratio_calc_length_rows_entry = tk.Entry(
            controls_frame, textvariable=self.ratio_calc_length_rows_var
        )
        self.ratio_calc_length_rows_entry.grid(row=1, column=9)

        # Ratio (read-only)
        tk.Label(controls_frame, text="Ratio:").grid(row=2, column=6)
        self.ratio_entry = tk.Entry(
            controls_frame, textvariable=self.ratio_var, state="readonly", width=8
        )
        self.ratio_entry.grid(row=2, column=7)

        # Calculate ratio button
        self.calc_ratio_button = tk.Button(
            controls_frame, text="Calculate Ratio", command=self.update_preview
        )
        self.calc_ratio_button.grid(row=2, column=8, columnspan=2, sticky="ew")

        # Buttons
        self.open_btn = tk.Button(controls_frame, text="Open Image", command=self.open_image)
        self.open_btn.grid(row=2, column=0, columnspan=3, sticky="ew")
        self.save_btn = tk.Button(controls_frame, text="Save Image", command=self.save_image)
        self.save_btn.grid(row=2, column=3, columnspan=3, sticky="ew")

        # Preview label
        self.preview_label = tk.Label(self)
        self.preview_label.bind("<Configure>", lambda e : self.update_preview())
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        # Data
        self.original_array = None
        self.current_image = None
        self.preview_imgtk = None

    def open_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            img = Image.open(file_path).convert("RGB")
            self.original_array = np.array(img)
            self.update_preview()

    def save_image(self):
        if self.current_image is not None:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            if file_path:
                self.current_image.save(file_path)

    def update_preview(self, *args):
        if self.original_array is None:
            return
        
        self.calculate_ratio()
        
        img = Image.fromarray(self.original_array.astype(np.uint8))

        w, h = img.size

        scale = min(self.preview_label.winfo_height() / h, self.preview_label.winfo_width() / w)
        scaled_img = img.resize((int(w*scale), int(h*scale)), Image.NEAREST)

        w, h = scaled_img.size

        pw = w // self.amount_stitches_var.get()
        self.single_stitch_length_var.set(pw)
        ph = round(pw * self.ratio_var.get())
        self.single_row_length_var.set(ph)

        
        scaled_array = np.array(scaled_img)

        pix_array = self.rasterize(scaled_array, pw, ph)
        pix_array = self.reduce_colors_kmeans(pix_array, self.amount_colors_var.get())

        # Draw grid lines and set stitches/rows
        h, w, _ = pix_array.shape
        if min(ph, pw) > 2:
            for y in range(ph, h, ph):
                pix_array[y, :, :] = [0, 0, 0]
            self.amount_rows_var.set(h // ph)
            for x in range(pw, w, pw):
                pix_array[:, x, :] = [0, 0, 0]
        

        pix_img = Image.fromarray(pix_array.astype(np.uint8))
        self.current_image = pix_img
        self.preview_imgtk = ImageTk.PhotoImage(pix_img)
        self.preview_label.config(image=self.preview_imgtk)

    def rasterize(self, img_array, tile_w, tile_h):
        h, w = img_array.shape[:2]
        rasterized = img_array.copy()
        for y in range(0, h, tile_h):
            for x in range(0, w, tile_w):
                block = rasterized[y:y+tile_h, x:x+tile_w]
                avg_color = block.mean(axis=(0, 1))
                block[:] = avg_color
        return rasterized

    def reduce_colors_kmeans(self, img, n_colors):
        pixels = img.reshape(-1, 3)
        kmeans = KMeans(n_clusters=n_colors, n_init="auto")
        kmeans.fit(pixels)
        centers = kmeans.cluster_centers_
        labels = kmeans.labels_
        quantized = centers[labels].reshape(img.shape).astype(np.uint8)
        return quantized


    def calculate_ratio(self):
        try:
            nx = float(self.ratio_calc_num_stitches_var.get())
            ny = float(self.ratio_calc_num_rows_var.get())
            length = float(self.ratio_calc_length_stitches_var.get())
            width = float(self.ratio_calc_length_rows_var.get())

            # ratio = (width / nx) / (length / ny)
            # Simplifies to: ratio of rows to stitches
            ratio = (width * nx) / (length * ny)
            self.ratio_var.set(ratio)

            # Now calculate rows from ratio * (amount of stitches)
            # Note: using current value from the "Number of stitches" field
            st = self.amount_stitches_var.get()
            self.amount_rows_var.set(int(st * ratio))

        except ValueError:
            pass  # Just ignore invalid inputs



if __name__ == "__main__":
    px_app = PixelateApp()
    px_app.attributes('-zoomed', True)
    px_app.mainloop()
