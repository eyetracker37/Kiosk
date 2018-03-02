from Utils.logger import log
import pygame
from Input import input_handler
from Utils import config
from Utils.scale import scale, get_image
from Pages import map
from Elements import window_elements

LEFT = "left"
RIGHT = "right"


# Main page controller, currently contains most of the style controls
class Page(window_elements.Subwindow):
    priority = 127

    # Gap between text and side of the screen, also controls some other spacing
    margins = scale(30)

    # Style of the text in the title block
    title_size = scale(160)
    title_font = "cambria"
    title_color = (255, 255, 255)

    # Style of the heading text
    heading_size = scale(46)
    heading_font = "opensans"

    # Style of the regular text
    _font_size = 38
    font_size = scale(_font_size)
    font = "opensans"
    font_color = (51, 51, 51)
    font_spacing = scale(_font_size / 4)  # Spacing between lines
    font_indent = scale(15)  # Additional spacing beyond margin to indent regular text

    def __init__(self, master):
        super().__init__(master)
        self.cursor = input_handler.get_cursor()  # TODO make this controlled by either the master window or subwindow

        master.register(self)

        self.offset = 0  # How far down the text goes
        self.scroll = 0  # How far down the user has scrolled

        # Spacing on the left and right, in addition to standard spacing (e.g an image taking up space)
        self.left_margin = 0
        self.right_margin = 0

        self.next_clear = 0  # How far down does image go, if one is currently being spaced

    # Tell page that vertical space has been used
    def increase_offset(self, increase):
        if self.offset >= self.next_clear:  # If we are now clear of the image being spaced, reset margins
            self.next_clear += increase
            self.left_margin = 0
            self.right_margin = 0
        self.offset += increase

    # Draw white background
    def draw(self):
        self.screen.fill((255, 255, 255))
        super().draw()

    # Use up all space next to space occupied by image
    def go_next_clear(self):
        self.offset = self.next_clear
        return self.next_clear

    def update(self):
        super().update()

        self.cursor = input_handler.get_cursor()

        # Scrolling handler
        if self.offset > config.screen_y:  # Only scroll if page is longer than screen can fit
            if self.cursor.is_valid:
                deadband = 100
                min_speed = 5  # Minimum movement speed if moving
                feathering = 30  # Lower = faster

                # Distance from center
                y_off = self.cursor.y_pos - config.screen_y / 2

                # Check if x and y are outside the deadband (center) range
                if y_off > deadband:
                    speed = min_speed + (y_off - deadband) / feathering
                    self.scroll -= speed
                elif y_off < -deadband:
                    speed = -min_speed + (y_off + deadband) / feathering
                    self.scroll -= speed

                # Make sure map doesn't go off the edge
                if self.scroll < -self.offset + config.screen_y:
                    self.scroll = -self.offset + config.screen_y
                elif self.scroll > 0:
                    self.scroll = 0


class Paragraph(window_elements.Subwindow):  # TODO should this be a subwindow?
    priority = 32

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.register(self)
        self.master_margins = master.margins
        self.margins = self.master_margins
        self.left_margin = master.left_margin
        self.right_margin = master.right_margin
        self.font_size = master.font_size
        self.font = master.font
        self.font_color = master.font_color
        self.font_spacing = master.font_spacing
        self.font_indent = master.font_indent
        self.offset = master.offset
        self.last_offset = self.offset
        self.scroll = master.scroll

    def increase_offset(self, increase):
        self.last_offset = self.offset
        self.offset += increase
        self.master.increase_offset(increase)
        self.left_margin = self.master.left_margin
        self.right_margin = self.master.right_margin

    def set_left_margin(self, amount):
        self.left_margin = amount
        self.master.left_margin = amount

    def set_right_margin(self, amount):
        self.right_margin = amount
        self.master.right_margin = amount

    def set_next_clear(self, next):
        self.master.next_clear = next

    def close(self):
        self.master.unregister(self)

    def update(self):
        super().update()
        self.scroll = self.master.scroll


# Base class for AML elements being drawn on screen
class GenericAmlElement:
    priority = 32

    def __init__(self, master):
        master.register(self)  # TODO handle the fact that this might have children
        self.screen = master.screen
        self.offset = master.offset
        self.margins = master.margins
        self.left_margin = master.left_margin
        self.right_margin = master.right_margin
        self.scroll = master.scroll
        self.master = master

    def draw(self):
        pass

    # Get current amount of scrolling
    def update(self):
        self.scroll = self.master.scroll

    def close(self):
        self.master.unregister(self)


class Title(GenericAmlElement):
    priority = 64

    def __init__(self, master, title, directory):
        super().__init__(master)

        self.font = pygame.font.SysFont(master.title_font, master.title_size)
        self.title_text = title
        self.display_text = self.font.render(self.title_text, True, master.title_color)

        url = directory + "header.bmp"
        self.img = get_image(url, 1.01)

        self.width = self.img.get_rect().size[0]
        self.height = self.img.get_rect().size[1]

    def draw(self):
        self.screen.blit(self.img, (0, self.scroll))  # Draw header image
        self.screen.blit(self.display_text, (self.margins, self.scroll))  # Draw text over top of it


class TextLine(GenericAmlElement):
    def __init__(self, master):
        super().__init__(master)

        self.indent = master.font_indent
        self.font = pygame.font.SysFont(master.font, master.font_size)
        self.line_text = None
        self.display_text = None

        # Create dummy text to get vertical spacing without needing content
        dummy_text = self.font.render(' ', True, master.font_color)

        # How much space is left on the line
        self.extra_space = config.screen_x - self.margins * 2 - self.left_margin + self.right_margin

        master.increase_offset(dummy_text.get_height())  # Space taken up by actual content
        master.increase_offset(master.font_spacing)  # Space taken up by font spacing

    def draw(self):
        # Horizontal position defined by normal margin plus indent plus space taken up by image if any
        self.screen.blit(self.display_text, (self.margins + self.left_margin + self.indent, self.offset + self.scroll))

    # Add text to the line
    def append_text(self, text):
        text = text.strip()  # Remove newlines and extra spacing
        text = text + ' '  # Ensure there is a single space
        if self.line_text:
            text = self.line_text + text

        # Add text until it hits the right boundary
        i = 1
        while self.font.size(text[:i])[0] < config.screen_x - self.margins * 2 - self.left_margin - self.right_margin\
                - self.indent and i < len(text):
            i += 1

        # If it didn't all fit, cut it off at the last complete line
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        # Text on the line is everything up to the break
        self.line_text = text[:i]

        # Whatever text got cut off
        extra_text = text[i:]

        # Is any space left over?
        self.extra_space = config.screen_x - self.margins * 2 - self.font.size(text[:i])[0]

        # Text being displayed is what was able to fit
        self.display_text = self.font.render(self.line_text, True, self.master.font_color)

        # Text if any that needs to be put on next line
        return extra_text

    def set_left_margin(self, amount):
        self.left_margin = amount
        self.master.set_left_margin(amount)

    def set_left_margin(self, amount):
        self.right_margin = amount
        self.master.set_right_margin(amount)

    # See if there's room to shift the text over to fit an image on the line
    def shift(self, direction, amount):
        if self.extra_space > amount:
            self.set_left_margin(amount)
            return True
        else:
            return False


class Heading(GenericAmlElement):
    def __init__(self, master, text):
        super().__init__(master)
        master.increase_offset(master.margins)
        self.offset = master.go_next_clear()
        self.font = pygame.font.SysFont(master.heading_font, master.heading_size)
        self.display_text = self.font.render(text, True, (0, 0, 0))
        master.increase_offset(self.display_text.get_height())
        master.increase_offset(scale(15))

    def draw(self):
        self.screen.blit(self.display_text, (self.margins, self.offset + self.master.scroll))


# Footer at the bottom to return to map
class Footer(GenericAmlElement):
    def __init__(self, master):
        super().__init__(master)
        url = "Resources/home.bmp"
        self.img = get_image(url, 0.75)
        self.img_width = self.img.get_rect().size[0]
        self.img_height = self.img.get_rect().size[1]

        # Start the image after any images are done
        master.go_next_clear()
        master.increase_offset(master.margins*3)  # Add some spacing
        self.offset = master.offset

        # Radius of circle around home icon
        self.circle_radius = int(self.master.margins + self.img_width/2)

        # Collider box around home icon to return to map
        self.base_x = int((config.screen_x-self.img_width)/2 - self.master.margins)
        self.base_y = int(self.offset + self.img_height/2 + self.circle_radius)
        self.collider_box = pygame.Rect(self.base_x, self.base_y, self.circle_radius * 2, self.circle_radius * 2)
        self.is_selected = 0

        # Add some spacing below
        master.increase_offset(self.circle_radius * 2)

    def draw(self):
        # Draw icon
        self.screen.blit(self.img, ((config.screen_x-self.img_width)/2, self.scroll + self.offset))

        line_y = int(self.scroll + self.offset + self.img_height/2)

        # Draw lines on left and right of home icon
        pygame.draw.line(self.screen, self.master.font_color, (self.master.margins, line_y),
                         ((config.screen_x-self.img_width)/2 - self.master.margins, line_y), 2)
        pygame.draw.line(self.screen, self.master.font_color, (config.screen_x - self.master.margins, line_y),
                         ((config.screen_x + self.img_width) / 2 + self.master.margins, line_y), 2)

        # Draw circle around home icon proportional to how "selected" it is
        try:
            pygame.draw.circle(self.screen, (55, 55, 55), (int(config.screen_x/2), line_y), int(self.circle_radius / 255 * self.is_selected), 2)
        except ValueError:  # Handle circle having size zero by not drawing it
            pass

    # Basically just checks if home icon is being looked at to "click" on it
    def update(self):
        super().update()
        self.collider_box.y = int(self.scroll + self.offset + self.img_height/2 - self.circle_radius)

        cursor_x = self.master.cursor.x_pos
        cursor_y = self.master.cursor.y_pos

        # If box is selected
        if self.master.cursor.is_valid \
                and self.collider_box.collidepoint(cursor_x, cursor_y):
            # Increase confidence user is actually "clicking" on the box
            self.is_selected += 3
            if self.is_selected > 255:
                log("Button pressed to return home", 2)
                self.is_selected = 0
                self.master.close()
                map.run(self.master.parent.parent)
        else:  # Decrease confidence user is "clicking" on the box
            if self.is_selected > 0:
                self.is_selected -= 10
                if self.is_selected < 0:
                    self.is_selected = 0


class Image(GenericAmlElement):
    def __init__(self, master, alignment, url, resize):
        super().__init__(master)
        self.img = get_image(url, resize)
        self.width = self.img.get_rect().size[0]
        self.height = self.img.get_rect().size[1]
        self.y_off = self.master.last_offset
        if alignment == LEFT:
            master.set_left_margin(self.width)
            self.x_off = self.margins
        elif alignment == RIGHT:
            master.set_right_margin(self.width)
            self.x_off = config.screen_x - self.width - self.margins
        master.set_next_clear(self.y_off + self.height)

    def draw(self):
        self.screen.blit(self.img, (self.x_off, self.y_off + self.scroll))

    def shift(self):
        self.y_off = self.master.offset
        self.master.set_next_clear(self.y_off + self.height)
