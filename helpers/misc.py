from helpers import db, browser


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


def check_announced(test_suite, title, dl_url, indexer, backends, snatched_backends=[]):
    db.check_announced(
        test_suite, title, dl_url, indexer, backends, snatched_backends,
    )

    browser.check_announced(test_suite, title, indexer, backends, snatched_backends)
