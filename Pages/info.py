from html.parser import HTMLParser
from Elements import window_elements
from Utils.logger import log
import pygame
from Input import input_handler
from Utils import config

# States
START = "START"
END = "END"
DATA = "DATA"

# Types
OUTSIDE = "OUTSIDE"
NO_STATE = "aml"
HEAD = "head"
BODY = "body"
TITLE = "title"
HEADING1 = "h1"
PARAGRAPH = "p"
IMAGE = "img"

LEFT = "left"
RIGHT = "right"


def scale(value):
    return int(value * config.scale_factor)


def get_image(url, resize=1):
    try:
        raw = pygame.image.load(url)
    except pygame.error:
        log(url + " does not exist", 0)
        return None
    width = scale(raw.get_rect().size[0] * resize)
    height = scale(raw.get_rect().size[1] * resize)
    scaled_image = pygame.transform.scale(raw, (width, height))
    return scaled_image


class Page(window_elements.Subwindow):
    priority = 127

    margins = scale(30)

    title_size = scale(120)
    title_font = "cambria"
    title_color = (255, 255, 255)

    heading_size = scale(46)
    heading_font = "opensans"

    _font_size = 38
    font_size = scale(_font_size)
    font = "opensans"
    font_color = (51, 51, 51)
    font_spacing = scale(_font_size / 4)
    font_indent = scale(15)

    def __init__(self, master):
        super().__init__(master)
        self.cursor = input_handler.get_cursor()
        master.register(self)
        self.offset = 0
        self.scroll = 0
        self.left_margin = 0
        self.right_margin = 0
        self.next_clear = 0

    def increase_offset(self, increase):
        if self.offset >= self.next_clear:
            self.next_clear += increase
            self.left_margin = 0
            self.right_margin = 0
        self.offset += increase

    def draw(self):
        self.screen.fill((255, 255, 255))
        super().draw()

    def go_next_clear(self):
        self.offset = self.next_clear
        return self.next_clear

    def update(self):
        super().update()

        if self.offset > config.screen_y:  # Only scroll if necessary
            self.cursor = input_handler.get_cursor()
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


class Paragraph(window_elements.Subwindow):
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
        self.master.unregister()

    def update(self):
        super().update()
        self.scroll = self.master.scroll


class GenericAmlElement:
    priority = 32

    def __init__(self, master):
        master.register(self)
        self.screen = master.screen
        self.offset = master.offset
        self.margins = master.margins
        self.left_margin = master.left_margin
        self.right_margin = master.right_margin
        self.scroll = master.scroll
        self.master = master

    def draw(self):
        pass

    def update(self):
        self.scroll = self.master.scroll

    def close(self):
        self.master.unregister()


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
        self.screen.blit(self.img, (0, self.scroll))
        self.screen.blit(self.display_text, (self.margins, self.scroll))


class TextLine(GenericAmlElement):
    def __init__(self, master):
        super().__init__(master)
        self.left_extra = master.font_indent
        self.font = pygame.font.SysFont(master.font, master.font_size)
        self.line_text = None
        self.display_text = None
        dummy_text = self.font.render(' ', True, master.font_color)
        self.extra_space = config.screen_x - self.margins * 2 - self.left_margin + self.right_margin
        master.increase_offset(dummy_text.get_height())
        master.increase_offset(master.font_spacing)

    def draw(self):
        self.screen.blit(self.display_text, (self.margins + self.left_margin + self.left_extra, self.offset + self.scroll))

    def append_text(self, text):
        text = text.strip()  # Remove newlines and extra spacing
        text = text + ' '  # Ensure there is a single space
        if self.line_text:
            text = self.line_text + text

        i = 1
        while self.font.size(text[:i])[0] < config.screen_x - self.margins * 2 - self.left_margin - self.right_margin\
                - self.left_extra and i < len(text):
            i += 1

        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        self.line_text = text[:i]

        extra_text = text[i:]

        self.extra_space = config.screen_x - self.margins * 2 - self.font.size(text[:i])[0]
        self.display_text = self.font.render(self.line_text, True, self.master.font_color)

        return extra_text

    def set_left_margin(self, amount):
        self.left_margin = amount
        self.master.set_left_margin(amount)

    def set_left_margin(self, amount):
        self.right_margin = amount
        self.master.set_right_margin(amount)

    def shift(self, direction, amount):
        if self.extra_space > amount:
            self.set_left_margin(amount)
            return True


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


class AMLParser(HTMLParser):
    def __init__(self, master):
        super().__init__()
        self.state = OUTSIDE
        self.page = Page(master)
        self.current_paragraph = None
        self.current_line = None
        self.title = None
        self.directory = None
        self.base_offset = 0

    def load_aml(self, file):
        try:
            self.directory = "Pages/InfoPages/" + file + "/"
            url = self.directory + file + ".aml"
            doc = open(url, 'r')
            log('Loaded "' + url + '"', 2)
        except FileNotFoundError:
            log('Attempted to load nonexistent file "' + file + '"', 0)
            return False
        for line in doc:
            self.feed(line)
        return self.close_state_machine()

    def create_title(self, title):
        self.title = Title(self.page, title, self.directory)
        self.page.increase_offset(self.title.height)

    def create_paragraph(self):
        self.current_paragraph = Paragraph(self.page)
        self.current_line = None

    def feed_text(self, data):
        if self.current_line:
            data = self.current_line.append_text(data)
        while data:
            self.current_line = TextLine(self.current_paragraph)
            data = self.current_line.append_text(data)

    def feed_heading1(self, data):
        Heading(self.page, data)

    def feed_image(self, attrs):
        source = attrs[0][1]
        alignment = attrs[1][1]
        resize = float(attrs[2][1])
        url = self.directory + source
        img = Image(self.current_paragraph, alignment, url, resize)
        if not self.current_line.shift(alignment, img.width + self.page.margins):
            img.shift()

    def state_machine(self, tag_type, tag, attrs):
        if tag_type is END:
            if tag == self.state:
                if self.state is NO_STATE:
                    self.state = OUTSIDE
                elif self.state is BODY or self.state is HEAD:
                    self.state = NO_STATE
                elif self.state is TITLE:
                    self.state = HEAD
                else:
                    self.state = BODY
                return

        if self.state is OUTSIDE:
            if tag_type is START:
                if tag == NO_STATE:
                    self.state = NO_STATE
                    return

        if self.state is NO_STATE:
            if tag_type is START:
                if tag == BODY:
                    self.state = BODY
                    return
                if tag == HEAD:
                    self.state = HEAD
                    return

        if self.state is BODY:
            if tag_type is START:
                if tag == HEADING1:
                    self.state = HEADING1
                    return
                if tag == PARAGRAPH:
                    self.create_paragraph()
                    self.state = PARAGRAPH
                    return

        if self.state is HEAD:
            if tag_type is START:
                if tag == TITLE:
                    self.state = TITLE
                    return

        if tag_type is DATA:
            if self.state is HEADING1:
                self.feed_heading1(tag)
                return
            if self.state is TITLE:
                self.create_title(tag)
                return
            if self.state is PARAGRAPH:
                self.feed_text(tag)
                return

        if self.state is PARAGRAPH:
            if tag_type is START:
                if tag == IMAGE:
                    self.feed_image(attrs)
                    return

        log('Unhandled ' + tag_type + ' "' + tag + '" in state ' + self.state, 1)

    def close_state_machine(self):
        if self.state is OUTSIDE:
            log("Closed AML state machine", 2)
            return True
        else:
            log("Failed to close state machine, stuck in state " + self.state, 0)
            return False

    def handle_starttag(self, tag, attrs):
        self.state_machine(START, tag, attrs)

    def handle_endtag(self, tag):
        self.state_machine(END, tag, None)

    def handle_data(self, data):
        if data != '\n':
            self.state_machine(DATA, data, None)


def run(master, file):

    window = window_elements.Subwindow(master)
    parser = AMLParser(window)

    parser.load_aml(file)

    master.set_window(window)
    window_elements.run_master(master)
