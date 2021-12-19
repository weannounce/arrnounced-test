from helpers import db, irc, backends, browser, arrnounced
from threading import Thread


class Config:
    def __init__(
        self,
        config_file,
        irc_channels,
        irc_users,
        backends,
        web_username=None,
        web_password=None,
        web_port=3467,
    ):
        self.config_file = config_file
        self.irc_channels = irc_channels
        self.web_port = web_port
        self.web_username = web_username
        self.web_password = web_password
        self.irc_users = irc_users
        self.backends = backends


class Release:
    def __init__(
        self,
        messages=None,
        channel=None,
        title=None,
        url=None,
        indexer=None,
        backends=None,
        snatches=None,
        protocol="Torrent",
    ):
        self.messages = messages
        self.channel = channel
        self.title = title
        self.url = url
        self.indexer = indexer
        self.backends = [] if backends is None else backends
        self.snatches = [] if snatches is None else snatches
        self.protocol = protocol


def check_announced(test_suite, config, release):
    db.check_announced(
        test_suite,
        release,
    )

    browser.check_announced(test_suite, config, release)


def check_announcements(test_suite, config, releases, snatches):
    db.check_announcements(
        test_suite,
        releases,
    )

    browser.check_unordered_announcements(test_suite, config, releases)
    browser.check_unordered_snatches(test_suite, snatches)


irc_thread = None


def setUpClass(config, start_browser=True):
    global irc_thread
    irc_thread = Thread(target=irc.run, args=[config])
    irc_thread.start()
    arrnounced.run(config)
    backends.run(config)
    db.init()
    irc.ready_event.wait()

    # Browser performs login, wait for everything to start before.
    if start_browser:
        browser.init(config)


def tearDownClass(config):
    global irc_thread
    irc.stop()
    backends.stop()
    db.stop()
    browser.stop()
    irc_thread.join()
    irc.ready_event.clear()
    arrnounced.stop(config)
