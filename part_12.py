import random
import math
import arcade
import os

from typing import cast

SPRITE_SCALING = 0.2
SPRITE_SCALING_LASER = 1.0

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "The Adventurous Knight"

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 100

MOVEMENT_SPEED = 5
SPRITE_SCALING_CHEST = 0.1
CHEST_COUNT = 10
BULLET_SPEED = 10
TEXTURE_LEFT = 0
TEXTURE_RIGHT = 1
ANGLE_SPEED = 5
DEAD_ZONE = 0.05


class TurningSprite(arcade.Sprite):
    """ Sprite that sets its angle to the direction it is traveling in. """
    def update(self):
        super().update()
        self.angle = math.degrees(math.atan2(self.change_y, self.change_x))


class Player(arcade.Sprite):

    def __init__(self, image, scale):
        super().__init__(image, scale)

        self.speed = 0

    def update(self):
        # Figure out if we should face left or right
        # Convert angle in degrees to radians.
        angle_rad = math.radians(self.angle)

        # Rotate the ship
        self.angle += self.change_angle

        # Use math to find our change based on our speed and angle
        self.center_x += -self.speed * math.sin(angle_rad)
        self.center_y += self.speed * math.cos(angle_rad)


class BulletSprite(TurningSprite):
    """
    Class that represents a bullet.

    Derives from arcade.TurningSprite which is just a Sprite
    that aligns to its direction.
    """

    def update(self):
        super().update()
        if self.center_x < -100 or self.center_x > 1500 or \
                self.center_y > 1100 or self.center_y < -100:
            self.remove_from_sprite_lists()


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height, title):
        """
        Initializer
        """
        super().__init__(width, height, title)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # https://freesound.org/people/TNTdude7/sounds/261462/
        self.chest_sound = arcade.load_sound("chest_slam.wav")

        # Sprite lists
        self.player_list = None
        self.chest_list = None
        self.bullet_list = None

        # Set up the player
        self.player_sprite = None
        self.wall_list = None
        self.physics_engine = None
        self.view_bottom = 0
        self.view_left = 0
        self.score = 0
        joysticks = arcade.get_joysticks()

        if joysticks:
            self.joystick_1 = joysticks[0]
            self.joystick_1.open()
            self.joystick_1.on_joybutton_press = self.on_joybutton_press
            self.joystick_1.on_joybutton_release = self.on_joybutton_release
            self.joystick_1.on_joyhat_motion = self.on_joyhat_motion

        else:
            print("There are no joysticks.")
            self.joystick_1 = None

    # noinspection PyMethodMayBeStatic
    def on_joybutton_press(self, _joystick, button):
        print("Button {} down".format(button))
        # Create a bullet
        if button == 7:
            bullet_sprite = BulletSprite("laserBlue05.png", SPRITE_SCALING_LASER)
            bullet_sprite.guid = "Bullet"

            bullet_sprite.change_y = \
                math.cos(math.radians(self.player_sprite.angle)) * BULLET_SPEED
            bullet_sprite.change_x = \
                -math.sin(math.radians(self.player_sprite.angle)) \
                * BULLET_SPEED

            bullet_sprite.center_x = self.player_sprite.center_x
            bullet_sprite.center_y = self.player_sprite.center_y
            bullet_sprite.update()

            self.bullet_list.append(bullet_sprite)

    # noinspection PyMethodMayBeStatic
    def on_joybutton_release(self, _joystick, button):
        print("Button {} up".format(button))

    # noinspection PyMethodMayBeStatic
    def on_joyhat_motion(self, _joystick, hat_x, hat_y):
        print("Hat ({}, {})".format(hat_x, hat_y))

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_list = arcade.SpriteList()

        # https://opengameart.org/content/animated-top-down-survivor-player
        # Set up the player
        self.player_sprite = Player("survivor-idle_rifle_0.png", 0.5)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = SCREEN_HEIGHT / 2
        self.player_list.append(self.player_sprite)
        self.wall_list = arcade.SpriteList()
        self.chest_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        self.score = 0


        # Set up the player
        # https://opengameart.org/content/animated-top-down-survivor-player



        # -- Set up several columns of walls
        for x in range(-700, 1700, 100):
            # sprite form https://opengameart.org/content/bush-png
            wall = arcade.Sprite("bush_11.png", SPRITE_SCALING)
            wall.center_x = x
            wall.center_y = -300
            self.wall_list.append(wall)
        for x in range(-700, 1700, 100):
            # sprite form https://opengameart.org/content/bush-png
            wall = arcade.Sprite("bush_11.png", SPRITE_SCALING)
            wall.center_x = x
            wall.center_y = 1025
            self.wall_list.append(wall)
        for y in range(-300, 1025, 100):
            # sprite form https://opengameart.org/content/bush-png
            wall = arcade.Sprite("bush_11.png", SPRITE_SCALING)
            wall.center_x = -700
            wall.center_y = y
            self.wall_list.append(wall)
        for y in range(-300, 1025, 100):
            # sprite form https://opengameart.org/content/bush-png
            wall = arcade.Sprite("bush_11.png", SPRITE_SCALING)
            wall.center_x = 1700
            wall.center_y = y
            self.wall_list.append(wall)


# https://www.pinterest.com/pin/258042253625289337

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        # Set the background color
        arcade.set_background_color(arcade.color.BRITISH_RACING_GREEN)

        # Set the viewport boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = 0
        self.view_bottom = 0

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.wall_list.draw()
        self.player_list.draw()
        self.chest_list.draw()
        self.bullet_list.draw()

        output = f"Score: {self.score}"
        arcade.draw_text(output, self.view_left, self.view_bottom, arcade.color.WHITE, 14)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

            # Rotate left/right
        if key == arcade.key.LEFT:
            self.player_sprite.change_angle = ANGLE_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_angle = -ANGLE_SPEED

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.speed = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_angle = 0

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called whenever the mouse moves.
        """
        # Create a bullet
        bullet = arcade.Sprite("laserBlue05.png", SPRITE_SCALING_LASER)

        # Position the bullet at the player's current location
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y

        # Get from the mouse the destination location for the bullet
        # IMPORTANT! If you have a scrolling screen, you will also need
        # to add in self.view_bottom and self.view_left.
        dest_x = x
        dest_y = y

        # Do math to calculate how to get the bullet to the destination.
        # Calculation the angle in radians between the start points
        # and end points. This is the angle the bullet will travel.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # Angle the bullet sprite so it doesn't look like it is flying
        # sideways.
        bullet.angle = math.degrees(angle)
        print(f"Bullet angle: {bullet.angle:.2f}")

        # Taking into account the angle, calculate our change_x
        # and change_y. Velocity is how fast the bullet travels.
        bullet.change_x = math.cos(angle) * BULLET_SPEED
        bullet.change_y = math.sin(angle) * BULLET_SPEED

        # Add the bullet to the appropriate lists
        self.bullet_list.append(bullet)

    def update(self, delta_time):
        """ Movement and game logic """

        if self.joystick_1:
            print(self.joystick_1.x, self.joystick_1.y)
        if abs(self.joystick_1.x) < DEAD_ZONE:
            self.player_sprite.change_x = 0
        else:
            self.player_sprite.change_x = self.joystick_1.x * MOVEMENT_SPEED

        if abs(self.joystick_1.y) < DEAD_ZONE:
            self.player_sprite.change_y = 0
        else:
            self.player_sprite.change_y = -self.joystick_1.y * MOVEMENT_SPEED

        self.player_list.update()

        self.bullet_list.update()

        hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                        self.chest_list
                                                        )

        for chest in hit_list:
            chest.remove_from_sprite_lists()
            self.score += 1

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        self.physics_engine.update()

        # --- Manage Scrolling ---

        # Keep track of if we changed the boundary. We don't want to call the
        # set_viewport command if we didn't change the view port.
        changed = False

        # Scroll left
        left_boundary = self.view_left + VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.view_bottom + VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True

        # Make sure our boundaries are integer values. While the view port does
        # support floating point numbers, for this application we want every pixel
        # in the view port to map directly onto a pixel on the screen. We don't want
        # any rounding errors.
        self.view_left = int(self.view_left)
        self.view_bottom = int(self.view_bottom)

        # If we changed the boundary values, update the view port to match
        if changed:
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left - 1,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom - 1)

        if hit_list:
            arcade.play_sound(self.chest_sound)



def main():
    """ Main method """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()