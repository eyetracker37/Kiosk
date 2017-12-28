from html.parser import HTMLParser
from Elements import window_elements
from Utils.logger import log

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


class AMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.state = OUTSIDE

    def feed_paragraph(self, data):
        print("Paragraph: " + data)

    def feed_heading1(self, data):
        print("Heading1: " + data)

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
                    self.state = PARAGRAPH
                    return

        if tag_type is DATA:
            if self.state is HEADING1:
                self.feed_heading1(tag)
                return
            if self.state is PARAGRAPH:
                self.feed_paragraph(tag)
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
    master = window_elements.MasterWindow()

    window = window_elements.Subwindow(master)
    master.set_window(window)

    parser = AMLParser()

    doc = load_aml(file)

    for line in doc:
        parser.feed(line)
    parser.close_state_machine()
    window_elements.run_master(master)
