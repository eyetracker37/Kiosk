from html.parser import HTMLParser
from Elements import window_elements
from Utils.logger import log


class AMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == "aml":
            print("Start of AML")
        else:
            print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)

    def handle_data(self, data):
        if data != '\n':
            print("Encountered some data  :", data)


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

    window_elements.run_master(master)
