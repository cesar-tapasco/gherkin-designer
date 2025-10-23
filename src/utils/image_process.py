from PIL import Image
from io import BytesIO
from playwright.sync_api import Locator, Page
import imagehash
import io


def get_hex_colors(screenshot_bytes):
  """
  Extracts a set of unique hex colors from an image.

  Args:
      bytes: Path to the image file.

  Returns:
      A set of unique hex color codes (#RRGGBB format).
  """
  img = Image.open(BytesIO(screenshot_bytes)).convert("RGB")  # Ensure RGB mode
  pixels = img.load()
  colors = set()
  for x in range(img.width):
    for y in range(img.height):
      r, g, b = pixels[x, y]
      hex_color = f"#{r:02x}{g:02x}{b:02x}"  # Format as #RRGGBB
      colors.add(hex_color)
  return colors


def validate_colors(total_colors, target_colors):
  count_found = 0
  for color in total_colors:
    color = str.lower(color)
    for target in target_colors:
      target = str.lower(target)
      if color == target:
        count_found += 1
      if count_found == len(target_colors):
        break
  return count_found == len(target_colors)


def get_bytes_colors_by_locator(locator: Locator, page: Page):
  element_box = locator.bounding_box()
  image_bytes = page.screenshot(
    clip={
      "x": element_box.get("x"),
      "y": element_box.get("y"),
      "width": element_box.get("width"),
      "height": element_box.get("height"),
    }
  )
  return image_bytes


def get_hex_colors_by_locator(locator: Locator, page: Page):
  image_bytes = get_bytes_colors_by_locator(locator, page)
  return get_hex_colors(image_bytes)


def diff_browser_local_image(locator: Locator, page: Page, local_path):
  img_src = Image.open(local_path)
  img_screen_bytes = get_bytes_colors_by_locator(locator, page)
  img_screen = Image.open(io.BytesIO(img_screen_bytes))
  hash1 = imagehash.average_hash(img_src)
  hash2 = imagehash.average_hash(img_screen)
  # Compare hashes
  return hash1 - hash2


def hex_to_rgb(hex_color):
  # Remove the '#' character if it's present
  hex_color = hex_color.lstrip("#")

  # Convert the hex string to integer values
  rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

  # Return the RGB values as a string in the format "rgb(R, G, B)"
  return f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})"
