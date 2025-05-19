from PIL import Image, ImageDraw
import pytesseract
import sys

def extract_text_from_image(image_path):
    """
    Extract text from the image using Tesseract OCR
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Extracted text from the image
    """
    try:
        # Open the image using PIL
        img = Image.open(image_path)
        
        # Extract text from the image
        text = pytesseract.image_to_string(img)
        
        return text
    except Exception as e:
        return f"Error processing image: {e}"

def create_ROI_for_given_coordinates(coordinates, img, idx):
    """
    Creates a Region of Interest (ROI) from the given coordinates and saves it.
    
    Args:
        coordinates (dict): A dictionary containing start and end coordinates.
                           Format: {start: {x: number, y: number}, end: {x: number, y: number}}
        img (PIL.Image): The source image
    
    Returns:
        PIL.Image: The cropped image (ROI)
    """
    try:
        # Extract coordinates
        start_x = coordinates['start']['x']
        start_y = coordinates['start']['y']
        end_x = coordinates['end']['x']
        end_y = coordinates['end']['y']
        
        # Ensure coordinates are within image bounds
        width, height = img.size
        start_x = max(0, min(start_x, width))
        start_y = max(0, min(start_y, height))
        end_x = max(0, min(end_x, width))
        end_y = max(0, min(end_y, height))
        
        # Create the ROI by cropping the image
        roi = img.crop((start_x, start_y, end_x, end_y))
        
        # Save the ROI to a file
        output_path = "image_snap_saved_{idx}.png"
        roi.save(output_path)
        
        print(f"ROI saved to {output_path}")
        return roi
    
    except Exception as e:
        print(f"Error creating ROI: {e}")
        return None

def draw_red_box(coordinates, img):

    """
    Draws a red box on the image using the given coordinates.
    
    Args:
        coordinates (dict): A dictionary containing start and end coordinates.
                           Format: {start: {x: number, y: number}, end: {x: number, y: number}}
        img (PIL.Image): The source image to draw on
    
    Returns:
        PIL.Image: A copy of the original image with the red box drawn on it
    """
    try:
        # Create a copy of the image to avoid modifying the original
        img_with_box = img.copy()
        
        # Extract coordinates
        start_x = coordinates['start']['x']
        start_y = coordinates['start']['y']
        end_x = coordinates['end']['x']
        end_y = coordinates['end']['y']
        
        # Ensure coordinates are within image bounds
        width, height = img.size
        start_x = max(0, min(start_x, width))
        start_y = max(0, min(start_y, height))
        end_x = max(0, min(end_x, width))
        end_y = max(0, min(end_y, height))
        
        # Create ImageDraw object to draw on the image
        draw = ImageDraw.Draw(img_with_box)
        
        # Draw the red box (outline only)
        # Parameters: [(top-left x, top-left y), (bottom-right x, bottom-right y)], outline color, width
        draw.rectangle([(start_x, start_y), (end_x, end_y)], outline="red", width=3)
        
        # Save the image with the box to a file
        output_path = "image_with_red_box.png"
        img_with_box.save(output_path)
        
        print(f"Image with red box saved to {output_path}")
        return img_with_box
    
    except Exception as e:
        print(f"Error drawing red box: {e}")
        return img  # Return original image if there's an error

def main():
    # Check if image path is provided
    if len(sys.argv) < 2:
        print("Usage: python hello_tesseract.py <image_path>")
        return
    
    image_path = sys.argv[1]
    
    # Extract text from the image
    text = extract_text_from_image(image_path)
    
    # Print the extracted text
    print("\nExtracted Text:")
    print("-" * 50)
    print(text)
    print("-" * 50)
    
    # Get additional information about the image
    try:
        # Get image dimensions
        img = Image.open(image_path)
        width, height = img.size
        
        # Get image format and mode
        image_format = img.format
        image_mode = img.mode
        
        print("\nImage Information:")
        print(f"Dimensions: {width}x{height} pixels")
        print(f"Format: {image_format}")
        print(f"Mode: {image_mode}")
        
        # Get confidence levels for the OCR
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        print("\nWord Confidence Levels:")
        for i, word in enumerate(data['text']):
            if word.strip():
                confidence = data['conf'][i]
                print(f"Word: {word} - Confidence: {confidence}%")
        
        # Define coordinates for boxes
        coordinates = [
            {
                'name': 'mainplayer_cards',
                'coords': {
                    'start': {'x': 620, 'y': 570},
                    'end': {'x': 850, 'y': 700}
                }
            },
            {
                'name': 'table_cards',
                'coords': {
                    'start': {'x': 300, 'y': 310},
                    'end': {'x': 780, 'y': 510}
                }
            }
        ]
        
        # Process each coordinate set
        for idx, coord_set in enumerate(coordinates):
            print(f"\nProcessing {coord_set['name']}...")
            
            # Draw red box
            img_with_box = draw_red_box(coord_set['coords'], img)
            
            # Create ROI
            roi_img = create_ROI_for_given_coordinates(coord_set['coords'], img, idx)
            
            # Save the image with box
            box_output_path = f"image_with_red_box_{idx}.png"
            img_with_box.save(box_output_path)
            print(f"Image with box saved to {box_output_path}")
        
    except Exception as e:
        print(f"Error getting image information: {e}")

if __name__ == "__main__":
    main()