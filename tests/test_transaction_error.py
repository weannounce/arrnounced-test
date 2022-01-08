import unittest
from datetime import datetime, timedelta
from helpers import arrnounced, db, irc, backends, web, misc
from helpers.misc import Release
import time
import os

channel = "#simple1"
config = misc.Config(
    config_file="pages.toml",
    irc_channels=[channel],
    irc_users=["bipbopsimple1"],
    backends={
        b[0]: backends.Backend(b[0], b[1])
        for b in [
            ("MySonarr", "simplesonkey"),
            ("MyLidarr", "simplelidkey"),
            ("MyRadarr", "simpleradkey"),
        ]
    },
)


class TransactionErrorTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        misc.setUpClass(config)

    @classmethod
    def tearDownClass(self):
        misc.tearDownClass(config)

    @db.db_session
    def setUp(self):
        backends.clear_all_backends()
        db.clear_db()

    def tearDown(self):
        web.logout()

    def test_database_transaction_error(self):
        release = Release(
            messages=["database transaction title : some stuff"],
            channel=channel,
            title="database transaction",
            url="smth: some stuff",
            indexer="Simple1",
            backends=config.backends.keys(),
        )

        # Trigger database error by moving the db file
        os.rename("data/brain.db", "data/brain.db.tmp")
        irc.announce(release)
        os.rename("data/brain.db.tmp", "data/brain.db")

        backends.max_announcements(self, "MySonarr", 0)
        backends.max_announcements(self, "MyRadarr", 0)
        backends.max_announcements(self, "MyLidarr", 0)

        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)

    def test_database_age(self):
        old_release = Release(
            messages=[],
            channel=channel,
            title="too old",
            url="smth: some stuff",
            indexer="Simple1",
            backends=config.backends.keys(),
            snatches=["MySonarr"],
            announce_time=datetime.now() - timedelta(days=50),
        )
        db.insert_announcement(old_release, snatched=True)

        young_release = Release(
            messages=[],
            channel=channel,
            title="young",
            url="smth: some stuff",
            indexer="Simple1",
            backends=config.backends.keys(),
            snatches=["MyRadarr"],
            announce_time=datetime.now()
            - timedelta(days=49, hours=23, minutes=59, seconds=30),
        )
        db.insert_announcement(young_release, snatched=True)

        misc.check_announcements(
            self, config, [old_release, young_release], [old_release, young_release]
        )

        # Restart arrnounced to trigger purge event, instead of waiting until
        # next purge loop
        arrnounced.stop(config)
        arrnounced.run(config)
        time.sleep(2)

        misc.check_announced(self, config, young_release)
