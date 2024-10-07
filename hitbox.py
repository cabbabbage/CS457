# hitbox.py

class Hitbox:
    @staticmethod
    def calculate_hitbox(img, x, y, width_adjust=0, height_adjust=0):
        """Calculates and returns a standardized hitbox for an object."""
        center_x, center_y = Hitbox.get_center(img)
        center_x += x
        center_y += y

        # Standardized hitbox size, with optional adjustments per object
        hitbox_top = center_y - (img.get_height() // 2) + height_adjust
        hitbox_bottom = center_y + (img.get_height() // 2) + height_adjust
        hitbox_left = center_x - (img.get_width() // 2) + width_adjust
        hitbox_right = center_x + (img.get_width() // 2) + width_adjust

        return hitbox_top, hitbox_bottom, hitbox_left, hitbox_right

    @staticmethod
    def get_center(img):
        """Calculates the center point of an image."""
        w, h = img.get_width(), img.get_height()
        center_x = w // 2
        center_y = h // 2
        return center_x, center_y
