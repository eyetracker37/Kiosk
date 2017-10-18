import os.path
from Utils.logger import log, update_threshold, set_write_log
import configparser

filename = "settings.ini"
settings_version = 3

use_tracker = True
verbosity = 3
res_width = 1440
res_height = 900

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

    global use_tracker, verbosity, res_width, res_height

    use_tracker = ('True' == config.get('Settings', 'UseTracker'))

    verbosity = int(config.get('Settings', 'Verbosity'))
    update_threshold(verbosity)

    write_log = ('True' == config.get('Settings', 'WriteLogs'))
    set_write_log(write_log)

    res_width = int(config.get('Settings', 'ResWidth'))

    res_height = int(config.get('Settings', 'ResHeight'))