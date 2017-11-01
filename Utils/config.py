import os.path
from Utils.logger import log, update_threshold, set_write_log
import configparser

filename = "settings.ini"
settings_version = 3

use_tracker = True
verbosity = 3

screen_x = 1920
screen_y = 1080


def create_settings():
    config = configparser.ConfigParser()
    settings_file = open(filename, 'w')
    config.add_section('Settings')
    config.set('Settings', 'Version', str(settings_version))
    config.set('Settings', 'UseTracker', str(True))
    config.set('Settings', 'WriteLogs', str(False))
    config.set('Settings', 'Verbosity', '3')
    config.set('Settings', 'ResWidth', '1440')
    config.set('Settings', 'ResHeight', '900')
    config.write(settings_file)
    settings_file.close()


def initialize():
    config = configparser.ConfigParser()
    log("Loading settings", 3)

    if not os.path.isfile(filename):
        log((filename + " does not exist, creating"), 2)
        create_settings()
    config.read(filename)

    if config.get('Settings', 'Version') != str(settings_version):
        log((filename + " out of date and deleted"), 1)
        create_settings()
        config.read(filename)

    global use_tracker, verbosity, screen_x, screen_y

    use_tracker = ('True' == config.get('Settings', 'UseTracker'))

    verbosity = int(config.get('Settings', 'Verbosity'))
    update_threshold(verbosity)

    write_log = ('True' == config.get('Settings', 'WriteLogs'))
    set_write_log(write_log)

    screen_x = int(config.get('Settings', 'ResWidth'))
    screen_y = int(config.get('Settings', 'ResHeight'))
