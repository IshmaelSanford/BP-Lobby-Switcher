import pyautogui
import os
import logging
from PIL import Image

# Reference resolution (1440p)
REF_WIDTH = 2560
REF_HEIGHT = 1440

def get_scaling_factor():
    """Calculates the scaling factor based on current screen resolution vs 1440p."""
    screen_width, screen_height = pyautogui.size()
    # Use width for scaling factor, assuming aspect ratio is similar or width is the constraint
    scale_x = screen_width / REF_WIDTH
    scale_y = screen_height / REF_HEIGHT
    # Use the smaller scale to ensure it fits? Or just width?
    # Usually UI scales by width or height. Let's average or pick one.
    # For games, usually resolution scaling affects both dimensions.
    return scale_x

def find_image_on_screen(image_path, confidence=0.8, grayscale=False):
    """
    Locates the center of an image on the screen.
    Scales the reference image if the screen resolution is not 1440p.
    Returns (x, y) coordinates or None if not found.
    """
    if not os.path.exists(image_path):
        logging.error(f"Image file not found: {image_path}")
        return None

    try:
        scale = get_scaling_factor()
        
        # If scale is close to 1.0, use the file directly (faster/cleaner)
        if 0.98 < scale < 1.02:
            location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence, grayscale=grayscale)
            return location
        else:
            # Load and resize image
            img = Image.open(image_path)
            new_width = int(img.width * scale)
            new_height = int(img.height * scale)
            
            # Ensure at least 1x1
            new_width = max(1, new_width)
            new_height = max(1, new_height)
            
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # locateCenterOnScreen can take a PIL image
            location = pyautogui.locateCenterOnScreen(resized_img, confidence=confidence, grayscale=grayscale)
            return location

    except pyautogui.ImageNotFoundException:
        return None
    except Exception as e:
        logging.error(f"Error finding image: {e}")
        return None
