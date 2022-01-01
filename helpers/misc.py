import time

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
        announce_time=None,
        protocol="Torrent",
    ):
        self.messages = messages
        self.channel = channel
        self.title = title
        self.url = url
        self.indexer = indexer
        self.backends = [] if backends is None else backends
        self.snatches = [] if snatches is None else snatches
        self.announce_time = announce_time
        self.protocol = protocol


def announce_await_push(test_suite, release, wait=0.1):
    irc.announce(release)
    test_suite.assertTrue(
        backends.push_done.wait(timeout=5), "Backend pushes never completed"
    )
    backends.push_done.clear()
    time.sleep(wait)


def check_announced(test_suite, config, release):
    db.check_announced(
        test_suite,
        release,
    )

    browser.check_announced(test_suite, config, release)


def check_unordered_announcements(test_suite, config, releases, snatches):
    db.check_unordered_announcements(
        test_suite,
        releases,
    )

    browser.check_unordered_announcements(test_suite, config, releases)
    browser.check_unordered_snatches(test_suite, snatches)


def check_announcements(test_suite, config, releases, snatches):
    db.check_announcements(
        test_suite,
        releases,
    )

    browser.check_announcements(test_suite, config, releases)
    browser.check_snatches(test_suite, snatches)


irc_thread = None


def setUpClass(config, start_browser=True):
    global irc_thread
    irc_thread = Thread(target=irc.run, args=[config])
    irc_thread.start()
    backends.run(config)
    arrnounced.run(config)
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
