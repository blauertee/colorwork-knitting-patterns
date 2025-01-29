import tkinter as tk
from tkinter import filedialog
import numpy as np
from PIL import Image, ImageTk
from sklearn.cluster import KMeans

"""
TDOD: 
 - amount stitches not readonly
 - ratio readonly
 - calc amount rows from ratio and amount stitches 

"""




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
        self.amount_stitches_var = tk.IntVar()
        self.amount_rows_var = tk.IntVar()
        self.amount_colors_var = tk.IntVar(value = 2)
        self.ratio_calc_num_stitches_var = tk.IntVar(value = 1)
        self.ratio_calc_num_rows_var = tk.IntVar(value = 1)
        self.ratio_calc_length_stitches_var = tk.DoubleVar(value = 1)
        self.ratio_calc_length_rows_var = tk.DoubleVar(value = 1)

        # Tile Width
        tk.Label(controls_frame, text="Tile Width:").grid(row=0, column=0)
        self.stitch_length_entry = tk.Entry(
            controls_frame,
            textvariable=self.tile_w_var, command=self.update_preview
        )
        self.stitch_length_entry.grid(row=1, column=0)

        # Tile Height
        tk.Label(controls_frame, text="Tile Height:").grid(row=0, column=1)
        self.row_length_entry = tk.Entry(
            controls_frame,
            textvariable=self.tile_w_var, command=self.update_preview
        )
        self.row_length_entry.grid(row=1, column=1)

        

        # Scale
        tk.Label(controls_frame, text="Scale:").grid(row=0, column=2)
        self.scale_var_scale = tk.Scale(
            controls_frame, from_=0.2, to=5, resolution=0.1,
            orient=tk.HORIZONTAL, variable=self.scale_var,
            command=self.update_preview
        )
        self.scale_var_scale.grid(row=1, column=2)

        # amount stithes
        tk.Label(controls_frame, text="Number of stitches:").grid(row=0, column=3)
        self.amount_stitches_entry = tk.Entry(controls_frame, textvariable=self.amount_stitches_var, state="readonly")
        self.amount_stitches_entry.grid(row=1, column=3)

        # amount rows
        tk.Label(controls_frame, text="Number of rows:").grid(row=0, column=4)
        self.amount_rows_entry = tk.Entry(controls_frame, textvariable=self.amount_rows_var, state="readonly")
        self.amount_rows_entry.grid(row=1, column=4)

        # amount colors
        tk.Label(controls_frame, text="Number of colors:").grid(row=0, column=5)
        self.amount_colors_entry = tk.Entry(
            controls_frame,
            textvariable=self.amount_colors_var,
            command = self.update_preview)
        self.amount_colors_entry.grid(row=1, column=5)

        # ratio calculator
        tk.Label(controls_frame, text="An amount of").grid(row=0, column=6)
        self.ratio_calc_num_stitches_entry = tk.Entry(controls_frame, textvariable=self.ratio_calc_num_stitches_var,
            command = calculate_ratio)
        self.ratio_calc_num_stitches_entry.grid(row=0, column=7)

        tk.Label(controls_frame, text="stitches has length").grid(row=0, column=8)
        self.ratio_calc_length_stitches_entry = tk.Entry(controls_frame, textvariable=self.ratio_calc_length_stitches_var,
            command = self.calculate_ratio)
        self.ratio_calc_length_stitches_entry.grid(row=0, column=9)

        tk.Label(controls_frame, text="An amount of").grid(row=1, column=6)
        self.ratio_calc_num_stitches_entry = tk.Entry(controls_frame, textvariable=self.ratio_calc_num_rows_var, command = self.calculate_ratio)
        self.ratio_calc_num_stitches_entry.grid(row=1, column=7)

        tk.Label(controls_frame, text="rows has length").grid(row=1, column=8)
        self.ratio_calc_length_rows_entry = tk.Entry(controls_frame, textvariable=self.ratio_calc_length_rows_var, command = self.calculate_ratio)
        self.ratio_calc_length_rows_entry.grid(row=1, column=9)


        # Buttons
        self.open_btn = tk.Button(controls_frame, text="Open Image", command=self.open_image)
        self.open_btn.grid(row=2, column=0, columnspan=3, sticky="ew")

        self.save_btn = tk.Button(controls_frame, text="Save Image", command=self.save_image)
        self.save_btn.grid(row=2, column=2, columnspan=3, sticky="ew")

        # Preview label (not in grid, takes remaining space)
        self.preview_label = tk.Label(self)
        self.preview_label.pack(fill=tk.BOTH, expand=True)

        # data properties
        self.original_array = None
        self.preview_imgtk = None
        self.stitch_row_ratio = 1

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
            
            pix_array = self.rasterize(scaled_array, pw, ph)

            pix_array = self.reduce_colors_kmeans(pix_array, self.amount_colors_var.get())

            # Draw grid lines on the rasterized image (using black lines).
            h, w, _ = pix_array.shape

            if(min(ph,pw) > 2):
                # Horizontal lines
                for y in range(ph, h, ph):
                    pix_array[y, :, :] = [0, 0, 0]
                self.amount_rows_var.set(h // ph)

                # Vertical lines
                for x in range(pw, w, pw):
                    pix_array[:, x, :] = [0, 0, 0]
                self.amount_stitches_var.set(w // pw)

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

    def rasterize(img_array, tile_w, tile_h):
        """
        Return a new numpy array rasterized into tile_w x tile_h blocks.
        Each block is assigned the average color of its pixels.
        """
        h, w = img_array.shape[:2]
        rasterized = img_array.copy()
        
        for y in range(0, h, tile_h):
            for x in range(0, w, tile_w):
                block = rasterized[y:y+tile_h, x:x+tile_w]
                avg_color = block.mean(axis=(0, 1))
                block[:] = avg_color
        
        return rasterized

    # todo: adapt to vars
    def calculate_ratio(self):
        try:
            nx = float(self.ratio_calc_num_stitches_var.get())
            ny = float(self.ratio_calc_num_rows_var.get())
            length = float(self.ratio_calc_length_stitches_var.get())
            width = float(self.ratio_calc_length_rows_var.get())
            ratio = (width / nx) / (length / ny)
            self.ratio = ratio
            self.update_preview()

        except ValueError:
            self.result_label.config(text="Invalid input.")



    
    



if __name__ == "__main__":
    px_app = PixelateApp()
    px_app.attributes('-zoomed', True)
    px_app.mainloop()
