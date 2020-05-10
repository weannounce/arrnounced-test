from helpers import db, irc, backends, browser, arrnounced
from threading import Thread


class Config:
    def __init__(
        self, config_file, channels, web_username, web_password, web_port=3467
    ):
        self.config_file = config_file
        self.channels = channels
        self.web_port = web_port
        self.web_username = web_username
        self.web_password = web_password


class Release:
    def __init__(
        self,
        messages=None,
        channel=None,
        title=None,
        url=None,
        indexer=None,
        backends=[],
        snatches=[],
        protocol="Torrent",
    ):
        self.messages = messages
        self.channel = channel
        self.title = title
        self.url = url
        self.indexer = indexer
        self.backends = backends
        self.snatches = snatches
        self.protocol = protocol


def check_announced(test_suite, config, release):
    db.check_announced(
        test_suite, release,
    )

    browser.check_announced(test_suite, config, release)


irc_thread = None


def setUpClass(config):
    global irc_thread
    irc_thread = Thread(target=irc.run)
    irc_thread.start()
    arrnounced.run(config)
    backends.run()
    db.init()
    irc.ready_event.wait()

    # Browser performs login, wait for everything to start before.
    browser.init(config)


def tearDownClass():
    global irc_thread
    irc.stop()
    backends.stop()
    db.stop()
    browser.stop()
    irc_thread.join()
    irc.ready_event.clear()
    arrnounced.stop()
