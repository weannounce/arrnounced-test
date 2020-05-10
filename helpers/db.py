from pony.orm import Database, desc, Required, Set
from pony.orm import db_session  # noqa: F401
import os
from . import config as global_config
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
        os.path.join(os.path.realpath(global_config.db_path), "brain.db"),
        create_db=False,
    )
    db.generate_mapping(create_tables=False)


def stop():
    global db
    db = Database()


def clear_db():
    Announced.select().delete()
    Snatched.select().delete()


def get_time_diff(release, db_time):
    return abs((release.announce_time - db_time).total_seconds())


@db_session
def check_announced(test_suite, release):
    announcements = _get_announced(1)
    test_suite.assertEqual(len(announcements), 1, "No announcement in ddatabase")
    announcement = announcements[0]

    test_suite.assertTrue(
        get_time_diff(release, announcement.date) < 1, "Publish date is too old"
    )
    test_suite.assertEqual(release.title, announcement.title, "Title is not matching")
    test_suite.assertEqual(
        release.indexer, announcement.indexer, "Indexer is not matching"
    )
    test_suite.assertEqual(
        release.url, announcement.torrent, "Download URL is not matching"
    )

    db_backends = announcement.backend.split("/")
    test_suite.assertEqual(
        len(db_backends), len(release.backends), "Backends length does not match"
    )
    for backend in release.backends:
        test_suite.assertTrue(backend in db_backends, "Did not find expected backend")

    test_suite.assertEqual(
        len(release.snatches),
        len(announcement.snatched),
        "Snatched incorrect amount of times",
    )
    for snatch in announcement.snatched:
        test_suite.assertTrue(
            snatch.backend in release.snatches, "Did not find expected backend"
        )


@db_session
def get_announcement(index=0):
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
