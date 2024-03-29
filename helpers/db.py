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


@db_session
def insert_announcement(release, snatched):
    a = Announced(
        date=release.announce_time,
        title=release.title,
        torrent=release.url,
        indexer=release.indexer,
        backend="/".join(release.backends),
    )

    if snatched:
        Snatched(date=release.announce_time, announced=a, backend=release.snatches[0])


def get_time_diff(release, db_time):
    return abs((release.announce_time - db_time).total_seconds())


def check_announced(test_suite, release):
    check_announcements(test_suite, [release])


@db_session
def check_unordered_announcements(test_suite, releases):
    announcements = _get_announced()
    test_suite.assertEqual(
        len(announcements),
        len(releases),
        "Incorrect  number of announcements in database",
    )
    releases_copy = releases.copy()
    releases_copy.reverse()

    for announcement in announcements:
        release = next(
            filter(lambda x: x.title == announcement.title, releases_copy), None
        )
        test_suite.assertNotEqual(release, None, "Backend did not receive release")
        releases_copy.remove(release)
        _check_announcement(test_suite, announcement, release)


def _check_announcement(test_suite, announcement, release):
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
        f"Snatched incorrect amount of times: {release.title}",
    )
    for snatch in announcement.snatched:
        test_suite.assertTrue(
            snatch.backend in release.snatches, "Did not find expected backend"
        )


@db_session
def check_announcements(test_suite, releases):
    announcements = _get_announced()
    test_suite.assertEqual(
        len(announcements),
        len(releases),
        "Incorrect  number of announcements in database",
    )

    for (announcement, release) in zip(announcements, reversed(releases)):
        _check_announcement(test_suite, announcement, release)


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
