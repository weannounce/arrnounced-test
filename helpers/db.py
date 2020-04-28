from pony.orm import Database, desc, Required, Set
from pony.orm import db_session  # noqa: F401
import os
from . import config
from datetime import datetime

db = Database()


class Announced(db.Entity):
    date = Required(datetime)
    title = Required(str)
    indexer = Required(str)
    torrent = Required(str)
    backend = Required(str)
    snatched = Set("Snatched")


class Snatched(db.Entity):
    date = Required(datetime)
    announced = Required(Announced)
    backend = Required(str)


def init():
    db.bind(
        "sqlite",
        os.path.join(os.path.realpath(config.db_path), "brain.db"),
        create_db=False,
    )
    db.generate_mapping(create_tables=False)


def stop():
    global db
    db = Database()


def clear_db():
    Announced.select().delete()
    Snatched.select().delete()


def get_date_diff(date):
    return (datetime.now() - date).total_seconds()


@db_session
def check_announced(test_suite, title, dlUrl, indexer, backends, snatched_backends=[]):
    announcements = _get_announced(1)
    test_suite.assertEqual(len(announcements), 1, "No announcement in ddatabase")
    announcement = announcements[0]

    test_suite.assertTrue(
        get_date_diff(announcement.date) < 5, "Publish date is too old"
    )
    test_suite.assertEqual(title, announcement.title, "Title is not matching")
    test_suite.assertEqual(indexer, announcement.indexer, "Indexer is not matching")
    test_suite.assertEqual(dlUrl, announcement.torrent, "Download URL is not matching")

    db_backends = announcement.backend.split("/")
    test_suite.assertEqual(
        len(db_backends), len(backends), "Backends length does not match"
    )
    for backend in backends:
        test_suite.assertTrue(backend in db_backends, "Did not find expected backend")

    test_suite.assertEqual(
        len(snatched_backends),
        len(announcement.snatched),
        "Snatched incorrect amount of times",
    )
    for snatch in announcement.snatched:
        test_suite.assertTrue(
            snatch.backend in snatched_backends, "Did not find expected backend"
        )


@db_session
def get_announce_id(index=0):
    return Announced.select().order_by(desc(Announced.id)).limit(1, offset=index)[0]


@db_session
def nr_announcements():
    return len(Announced.select().order_by(desc(Announced.id)))


@db_session
def nr_snatches():
    return len(Snatched.select().order_by(desc(Snatched.id)))


def _get_announced(limit=None):
    return Announced.select().order_by(desc(Announced.id)).limit(limit)


def _get_snatched(limit=None):
    return Snatched.select().order_by(desc(Snatched.id)).limit(limit)
