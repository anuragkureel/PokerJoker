import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk, ImageDraw
import pytesseract
import sys

class TesseractGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tesseract OCR with ROI Selection")
        
        # Set window size
        self.root.geometry("1000x800")
        
        # Initialize variables
        self.image_path = None
        self.original_image = None
        self.display_image = None
        self.photo = None
        self.start_x = tk.IntVar(value=0)
        self.start_y = tk.IntVar(value=0)
        self.end_x = tk.IntVar(value=100)
        self.end_y = tk.IntVar(value=100)
        
        # Create main frame with padding
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Top frame for buttons
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, pady=5)
        
        # Image selection button
        self.load_button = ttk.Button(
            top_frame, 
            text="Load Image", 
            command=self.load_image,
            width=20
        )
        self.load_button.pack(side=tk.LEFT, padx=5)
        
        # Draw box button
        self.draw_box_button = ttk.Button(
            top_frame, 
            text="Draw Box", 
            command=self.draw_box,
            width=20
        )
        self.draw_box_button.pack(side=tk.LEFT, padx=5)
        
        # Extract ROI button
        self.extract_roi_button = ttk.Button(
            top_frame, 
            text="Extract ROI", 
            command=self.extract_roi,
            width=20
        )
        self.extract_roi_button.pack(side=tk.LEFT, padx=5)
        
        # Image display area
        self.image_label = ttk.Label(self.main_frame)
        self.image_label.pack(pady=10)
        
        # Sliders frame
        sliders_frame = ttk.LabelFrame(self.main_frame, text="Coordinate Selection", padding="10")
        sliders_frame.pack(fill=tk.X, pady=5)
        
        # Coordinate sliders
        self.create_slider(sliders_frame, "Start X:", self.start_x, 0)
        self.create_slider(sliders_frame, "Start Y:", self.start_y, 1)
        self.create_slider(sliders_frame, "End X:", self.end_x, 2)
        self.create_slider(sliders_frame, "End Y:", self.end_y, 3)
        
        # Text display area
        text_frame = ttk.LabelFrame(self.main_frame, text="Extracted Text", padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.text_display = tk.Text(text_frame, height=10, width=50)
        self.text_display.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar to text display
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_display.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_display.configure(yscrollcommand=scrollbar.set)
        
    def create_slider(self, parent, label_text, variable, row):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(frame, text=label_text, width=10).pack(side=tk.LEFT)
        slider = ttk.Scale(
            frame,
            from_=0,
            to=1000,
            variable=variable,
            orient=tk.HORIZONTAL,
            command=self.update_preview
        )
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add value label
        value_label = ttk.Label(frame, text=str(variable.get()))
        value_label.pack(side=tk.LEFT, padx=5)
        
        # Update value label when slider changes
        def update_label(*args):
            value_label.configure(text=str(variable.get()))
        variable.trace_add("write", update_label)
        
    def load_image(self):
        self.image_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if self.image_path:
            self.original_image = Image.open(self.image_path)
            self.display_image = self.original_image.copy()
            
            # Update slider ranges based on image size
            width, height = self.original_image.size
            for child in self.main_frame.winfo_children():
                if isinstance(child, ttk.LabelFrame):
                    for frame in child.winfo_children():
                        if isinstance(frame, ttk.Frame):
                            for widget in frame.winfo_children():
                                if isinstance(widget, ttk.Scale):
                                    widget.configure(to=max(width, height))
            
            self.update_image_display()
            
    def update_image_display(self):
        if self.display_image:
            # Resize image for display while maintaining aspect ratio
            display_size = (800, 600)
            display_image = self.display_image.copy()
            display_image.thumbnail(display_size, Image.LANCZOS)
            
            self.photo = ImageTk.PhotoImage(display_image)
            self.image_label.configure(image=self.photo)
            
    def update_preview(self, _=None):
        if self.original_image:
            self.display_image = self.original_image.copy()
            coordinates = {
                'start': {'x': self.start_x.get(), 'y': self.start_y.get()},
                'end': {'x': self.end_x.get(), 'y': self.end_y.get()}
            }
            self.draw_box(coordinates, preview=True)
            
    def draw_box(self, coordinates=None, preview=False):
        if not coordinates:
            coordinates = {
                'start': {'x': self.start_x.get(), 'y': self.start_y.get()},
                'end': {'x': self.end_x.get(), 'y': self.end_y.get()}
            }
        
        if self.original_image:
            self.display_image = self.original_image.copy()
            draw = ImageDraw.Draw(self.display_image)
            
            # Draw the box
            draw.rectangle(
                [(coordinates['start']['x'], coordinates['start']['y']),
                 (coordinates['end']['x'], coordinates['end']['y'])],
                outline="red",
                width=3
            )
            
            if not preview:
                # Save the image with box
                output_path = "image_with_red_box.png"
                self.display_image.save(output_path)
                self.text_display.insert(tk.END, f"Image with box saved to {output_path}\n")
            
            self.update_image_display()
            
    def extract_roi(self):
        if self.original_image:
            coordinates = {
                'start': {'x': self.start_x.get(), 'y': self.start_y.get()},
                'end': {'x': self.end_x.get(), 'y': self.end_y.get()}
            }
            
            # Create ROI
            roi = self.original_image.crop((
                coordinates['start']['x'],
                coordinates['start']['y'],
                coordinates['end']['x'],
                coordinates['end']['y']
            ))
            
            # Save ROI
            output_path = "image_snap_saved.png"
            roi.save(output_path)
            
            # Extract text from ROI
            text = pytesseract.image_to_string(roi)
            
            # Display results
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(tk.END, f"ROI saved to {output_path}\n\n")
            self.text_display.insert(tk.END, "Extracted Text:\n")
            self.text_display.insert(tk.END, text)

def main():
    root = tk.Tk()
    app = TesseractGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()