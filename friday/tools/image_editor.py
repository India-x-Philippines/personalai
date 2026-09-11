"""
Image Editor MCP Tools — Microsoft Photos & Image Processing Integration
Provides non-destructive image manipulation tools (crop, rotate, adjust, text overlay)
and launches results in Microsoft Photos viewer on Windows.
"""

import os
import subprocess
import logging
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
from friday.permissions import permission_manager

logger = logging.getLogger("friday-image-editor")

def _generate_output_path(source_path: str, suffix: str) -> str:
    """Generate a non-destructive output path like filename_cropped.png."""
    dir_name, file_name = os.path.split(source_path)
    base_name, ext = os.path.splitext(file_name)
    output_ext = ext if ext.lower() in ['.jpg', '.jpeg', '.png', '.webp'] else '.png'
    return os.path.join(dir_name, f"{base_name}_{suffix}{output_ext}")

def _open_in_photos(image_path: str) -> bool:
    """Launches the target image inside Microsoft Photos via OS shell launcher."""
    try:
        if os.name == 'nt':
            os.startfile(os.path.abspath(image_path))
            return True
    except Exception as e:
        logger.error(f"Failed to launch Microsoft Photos: {e}")
    return False

def register(mcp):

    @mcp.tool()
    def open_image_in_photos(image_path: str) -> str:
        """
        Opens a specific image file inside the Microsoft Photos viewer.
        Use this when the user asks to view or open an image in Photos.
        """
        perm = permission_manager.check_permission("microsoft_photos", "read_images")
        if perm == "DENY":
            return "Permission denied: Unable to read image files."

        if not os.path.exists(image_path):
            return f"Image file not found at path: {image_path}"

        success = _open_in_photos(image_path)
        if success:
            return f"Opened image in Microsoft Photos: {os.path.basename(image_path)}"
        return f"Unable to launch Microsoft Photos for: {image_path}"

    @mcp.tool()
    def crop_image(image_path: str, aspect_ratio: str = "16:9", output_path: str = None) -> str:
        """
        Crops an image to a specific aspect ratio (e.g. '16:9', '4:3', '1:1', 'square').
        Saves an edited copy and opens it in Microsoft Photos.
        """
        perm = permission_manager.check_permission("microsoft_photos", "edit_images")
        if perm == "DENY":
            return "Permission denied: Unable to edit images."

        if not os.path.exists(image_path):
            return f"Image file not found: {image_path}"

        try:
            with Image.open(image_path) as img:
                w, h = img.size
                
                # Calculate target ratio
                if aspect_ratio == "16:9":
                    target_ratio = 16.0 / 9.0
                elif aspect_ratio == "4:3":
                    target_ratio = 4.0 / 3.0
                elif aspect_ratio in ["1:1", "square"]:
                    target_ratio = 1.0
                else:
                    target_ratio = 16.0 / 9.0

                current_ratio = float(w) / float(h)

                if current_ratio > target_ratio:
                    # Image is too wide
                    new_w = int(h * target_ratio)
                    offset = (w - new_w) // 2
                    box = (offset, 0, offset + new_w, h)
                else:
                    # Image is too tall
                    new_h = int(w / target_ratio)
                    offset = (h - new_h) // 2
                    box = (0, offset, w, offset + new_h)

                cropped = img.crop(box)

                save_path = output_path or _generate_output_path(image_path, "cropped")
                cropped.save(save_path)
                _open_in_photos(save_path)

                return f"Successfully cropped image to {aspect_ratio} ratio and opened in Microsoft Photos."

        except Exception as e:
            return f"Failed to crop image: {str(e)}"

    @mcp.tool()
    def rotate_image(image_path: str, angle: int = 90, output_path: str = None) -> str:
        """
        Rotates an image by a specified angle (e.g., 90, 180, 270 degrees clockwise).
        Saves an edited copy and opens it in Microsoft Photos.
        """
        perm = permission_manager.check_permission("microsoft_photos", "edit_images")
        if perm == "DENY":
            return "Permission denied: Unable to edit images."

        if not os.path.exists(image_path):
            return f"Image file not found: {image_path}"

        try:
            with Image.open(image_path) as img:
                # Rotate clockwise in Pillow (angle is counter-clockwise by default, so pass -angle)
                rotated = img.rotate(-angle, expand=True)

                save_path = output_path or _generate_output_path(image_path, f"rotated{angle}")
                rotated.save(save_path)
                _open_in_photos(save_path)

                return f"Rotated image {angle} degrees clockwise and displayed in Microsoft Photos."

        except Exception as e:
            return f"Failed to rotate image: {str(e)}"

    @mcp.tool()
    def adjust_image(image_path: str, brightness: float = 1.2, contrast: float = 1.1, saturation: float = 1.1, output_path: str = None) -> str:
        """
        Adjusts brightness, contrast, and saturation of an image (values > 1.0 increase intensity).
        Saves an edited copy and opens it in Microsoft Photos.
        """
        perm = permission_manager.check_permission("microsoft_photos", "edit_images")
        if perm == "DENY":
            return "Permission denied: Unable to edit images."

        if not os.path.exists(image_path):
            return f"Image file not found: {image_path}"

        try:
            with Image.open(image_path) as img:
                # Adjust Brightness
                if brightness != 1.0:
                    img = ImageEnhance.Brightness(img).enhance(brightness)
                # Adjust Contrast
                if contrast != 1.0:
                    img = ImageEnhance.Contrast(img).enhance(contrast)
                # Adjust Saturation
                if saturation != 1.0:
                    img = ImageEnhance.Color(img).enhance(saturation)

                save_path = output_path or _generate_output_path(image_path, "adjusted")
                img.save(save_path)
                _open_in_photos(save_path)

                return f"Adjusted brightness/contrast/saturation and displayed in Microsoft Photos."

        except Exception as e:
            return f"Failed to adjust image: {str(e)}"

    @mcp.tool()
    def add_text_to_image(image_path: str, text: str, position: str = "center", color: str = "white", font_size: int = 48, output_path: str = None) -> str:
        """
        Draws a text overlay onto an image at the specified position ('center', 'bottom', 'top').
        Saves an edited copy and opens it in Microsoft Photos.
        """
        perm = permission_manager.check_permission("microsoft_photos", "edit_images")
        if perm == "DENY":
            return "Permission denied: Unable to edit images."

        if not os.path.exists(image_path):
            return f"Image file not found: {image_path}"

        try:
            with Image.open(image_path).convert("RGBA") as img:
                txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(txt_layer)

                # Try loading default font or truetype font
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except Exception:
                    font = ImageFont.load_default()

                w, h = img.size
                bbox = draw.textbbox((0, 0), text, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]

                # Position math
                if position == "bottom":
                    x = (w - text_w) // 2
                    y = h - text_h - 40
                elif position == "top":
                    x = (w - text_w) // 2
                    y = 40
                else: # center
                    x = (w - text_w) // 2
                    y = (h - text_h) // 2

                # Color parsing
                text_color = (255, 255, 255, 255) if color.lower() == "white" else (0, 229, 255, 255)
                shadow_color = (0, 0, 0, 220)

                # Draw drop shadow for crisp visibility
                draw.text((x + 2, y + 2), text, font=font, fill=shadow_color)
                # Draw main text
                draw.text((x, y), text, font=font, fill=text_color)

                combined = Image.alpha_composite(img, txt_layer)
                rgb_result = combined.convert("RGB")

                save_path = output_path or _generate_output_path(image_path, "text")
                rgb_result.save(save_path)
                _open_in_photos(save_path)

                return f"Added text overlay '{text}' to image and opened in Microsoft Photos."

        except Exception as e:
            return f"Failed to add text to image: {str(e)}"

    @mcp.tool()
    def save_image_copy(source_path: str, destination_path: str) -> str:
        """
        Saves a copy of an image file to a new destination path.
        """
        perm = permission_manager.check_permission("microsoft_photos", "create_images")
        if perm == "DENY":
            return "Permission denied: Unable to create new files."

        if not os.path.exists(source_path):
            return f"Source image not found: {source_path}"

        try:
            with Image.open(source_path) as img:
                img.save(destination_path)
                return f"Successfully saved image copy to: {destination_path}"
        except Exception as e:
            return f"Failed to save image copy: {str(e)}"
