from helpers import db, browser

# class Announcement():
#    def __init__


def check_announced(test_suite, title, dl_url, indexer, backends, snatched_backends=[]):
    db.check_announced(
        test_suite, title, dl_url, indexer, backends, snatched_backends,
    )

    browser.check_announced(test_suite, title, indexer, backends, snatched_backends)
