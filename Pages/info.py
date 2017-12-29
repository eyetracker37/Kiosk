from html.parser import HTMLParser
from Elements import window_elements
from Utils.logger import log
import pygame
from Utils import config

# States
START = "START"
END = "END"
DATA = "DATA"

# Types
OUTSIDE = "OUTSIDE"
NO_STATE = "aml"
BODY = "body"
HEADING1 = "h1"
PARAGRAPH = "p"
IMAGE = "img"


class Page(window_elements.Subwindow):
    priority = 127
    margins = 10
    font_size = 24
    heading_size = 30

    def __init__(self, master):
        super().__init__(master)
        master.register(self)
        self.offset = 0
        self.scroll = 0

    def increase_offset(self, increase):
        self.offset += increase

    def draw(self):
        self.screen.fill((255, 255, 255))
        super().draw()


class Paragraph(window_elements.Subwindow):
    priority = 127

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.register(self)
        self.master_margins = master.margins
        self.margins = self.master_margins
        self.font_size = master.font_size
        self.offset = master.offset
        self.scroll = master.scroll

    def increase_offset(self, increase):
        self.offset += increase
        self.master.increase_offset(increase)


class GenericText:
    priority = 127

    def __init__(self, master, text, font, size):
        master.register(self)
        self.screen = master.screen
        self.margins = master.margins
        self.font = pygame.font.SysFont(font, size)
        self.offset = master.offset
        self.scroll = master.scroll
        i = 1

        while self.font.size(text[:i])[0] < config.screen_x and i < len(text):
            i += 1

        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        display_text = text[:i]

        self.extra_text = text[i:]

        self.text = self.font.render(display_text, True, (0, 0, 0))
        master.increase_offset(self.text.get_height())

    def draw(self):
        self.screen.blit(self.text, (self.margins, self.offset + self.scroll))


class TextLine(GenericText):
    def __init__(self, master, text):
        super().__init__(master, text, "comicsansms", master.font_size)


class Heading(GenericText):
    def __init__(self, master, text):
        super().__init__(master, text, "comicsansms", master.heading_size)


class AMLParser(HTMLParser):
    def __init__(self, master):
        super().__init__()
        self.state = OUTSIDE
        self.page = Page(master)
        self.current_paragraph = None
        self.current_line = None

    def create_paragraph(self):
        self.current_paragraph = Paragraph(self.page)
        self.current_line = None

    def feed_text(self, data):
        while data:
            self.current_line = TextLine(self.current_paragraph, data)
            data = self.current_line.extra_text

    def feed_heading1(self, data):
        Heading(self.page, data)

    def feed_image(self, attrs):
        source = attrs[0][1]
        alignment = attrs[1][1]
        print("Image: " + source + " on the " + alignment)

    def state_machine(self, tag_type, tag, attrs):
        if tag_type is END:
            if tag == self.state:
                if self.state is NO_STATE:
                    self.state = OUTSIDE
                elif self.state is BODY:
                    self.state = NO_STATE
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

        if self.state is BODY:
            if tag_type is START:
                if tag == HEADING1:
                    self.state = HEADING1
                    return
                if tag == PARAGRAPH:
                    self.create_paragraph()
                    self.state = PARAGRAPH
                    return

        if tag_type is DATA:
            if self.state is HEADING1:
                self.feed_heading1(tag)
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


def load_aml(file):
    try:
        url = "Pages/InfoPages/" + file + ".aml"
        doc = open(url, 'r')
        log('Loaded "' + url + '"', 2)
        return doc
    except FileNotFoundError:
        log('Attempted to load nonexistent file "' + file + '"', 0)


def run(file):
    print(config.screen_x)
    master = window_elements.MasterWindow()

    window = window_elements.Subwindow(master)

    parser = AMLParser(window)

    doc = load_aml(file)

    for line in doc:
        parser.feed(line)
    parser.close_state_machine()

    master.set_window(window)
    window_elements.run_master(master)
