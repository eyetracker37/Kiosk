from html.parser import HTMLParser
from Elements import window_elements
from Elements.aml_elements import Page, Paragraph, Footer, Title, TextLine, Image, Heading
from Utils.logger import log

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


class AMLParser(HTMLParser):
    def __init__(self, master):
        super().__init__()

        self.state = OUTSIDE  # Where we are in AML state machine
        self.page = Page(master)  # Page the parser is drawing on
        self.current_paragraph = None  # Paragraph currently being written to
        self.current_line = None  # Line currently being written to
        self.title = None  # Title at top
        self.footer = None  # Return header at bottom
        self.directory = None  # Location of AML and other files

    # Loads AML file and generates page
    def load_aml(self, file):
        # Loads "Pages/InfoPages/$file/$file.aml
        try:
            self.directory = "Pages/InfoPages/" + file + "/"
            url = self.directory + file + ".aml"
            doc = open(url, 'r')
            log('Loaded "' + url + '"', 2)
        except FileNotFoundError:
            log('Attempted to load nonexistent file "' + file + '"', 0)
            return False

        # Feed document line by line into parser
        for line in doc:
            self.feed(line)

        # Append return to map footer
        self.create_footer()

        # Will return true if state machine is in state OUTSIDE and can be closed
        return self.close_state_machine()

    # Footer at bottom of page to return to map
    def create_footer(self):
        self.footer = Footer(self.page)

    # Title over image header.bmp
    def create_title(self, title):
        self.title = Title(self.page, title, self.directory)
        self.page.increase_offset(self.title.height)

    # New paragraph object
    def create_paragraph(self):
        self.current_paragraph = Paragraph(self.page)
        self.current_line = None

    # Add text to current paragraph
    def feed_text(self, data):
        # If there's already a line to add to
        if self.current_line:
            # Gets remainder of whatever can't fit on current line
            data = self.current_line.append_text(data)

        # While there's text left to be added
        while data:
            self.current_line = TextLine(self.current_paragraph)  # Create a new line
            data = self.current_line.append_text(data)  # Remaining data is whatever didn't fit

    def feed_heading1(self, data):
        Heading(self.page, data)

    # Add image to paragraph with attrs [name, alignment, scale]
    def feed_image(self, attrs):
        # Get name, alignment, and scale
        name = attrs[0][1]
        alignment = attrs[1][1]
        resize = float(attrs[2][1])

        url = self.directory + name
        img = Image(self.current_paragraph, alignment, url, resize)

        # See if image can be fit in space not currently used by text on the current line
        if not self.current_line.shift(alignment, img.width + self.page.margins):
            img.shift()  # It it can't, shift the image down one line

    # Main state machine for AML parsing
    def state_machine(self, tag_type, tag, attrs):

        # Tag of the form </$tag>
        if tag_type is END:
            if tag == self.state:  # if it's ending the state the parser is currently in
                if self.state is NO_STATE:
                    self.state = OUTSIDE
                elif self.state is BODY or self.state is HEAD:
                    self.state = NO_STATE
                elif self.state is TITLE:
                    self.state = HEAD
                else:
                    self.state = BODY
                return

        # Parser is outside of any tags (not yet reached <aml>)
        if self.state is OUTSIDE:
            if tag_type is START:
                if tag == NO_STATE:
                    self.state = NO_STATE
                    return

        # Inside of <aml> but not in any specific tag
        if self.state is NO_STATE:
            if tag_type is START:
                if tag == BODY:  # Start of main body
                    self.state = BODY
                    return
                if tag == HEAD:  # Controls the text displayed on the title
                    self.state = HEAD
                    return

        # Currently just used to wrap the title
        if self.state is HEAD:
            if tag_type is START:
                if tag == TITLE:
                    self.state = TITLE
                    return

        # Inside the main body of the page
        if self.state is BODY:
            if tag_type is START:
                if tag == HEADING1:
                    self.state = HEADING1
                    return
                if tag == PARAGRAPH:
                    self.create_paragraph()
                    self.state = PARAGRAPH
                    return

        # Actual content being passed
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

        # Images can only be created inside of paragraphs
        if self.state is PARAGRAPH:
            if tag_type is START:
                if tag == IMAGE:
                    self.feed_image(attrs)
                    return

        # In case something wasn't handled by parser, usually indicates malformed AML
        log('Unhandled ' + tag_type + ' "' + tag + '" in state ' + self.state, 1)

    # Try to close the state machine
    def close_state_machine(self):
        if self.state is OUTSIDE:  # Only works if the state machine properly exited on the closing </aml>
            log("Closed AML state machine", 2)
            return True
        else:  # State machine never got outside the <aml> tags
            log("Failed to close state machine, stuck in state " + self.state, 0)
            return False

    # Callback functions from the HTML parser base class:

    def handle_starttag(self, tag, attrs):
        self.state_machine(START, tag, attrs)

    def handle_endtag(self, tag):
        self.state_machine(END, tag, None)

    def handle_data(self, data):
        if data != '\n':
            self.state_machine(DATA, data, None)


def run(master, file):
    window = window_elements.HierarchyObject(master)  # Window AML parser will draw on
    parser = AMLParser(window)  # Create instance of parser to parse text

    parser.load_aml(file)  # Load and parse the target file
