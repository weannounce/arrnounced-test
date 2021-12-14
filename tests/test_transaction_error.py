import unittest
from helpers import db, irc, backends, web, misc
from helpers.misc import Release
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
            messages=["database transaction : some stuff"],
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

        backends.check_rx(
            self, config.backends["MySonarr"], release,
        )
        backends.check_rx(
            self, config.backends["MyRadarr"], release,
        )
        backends.check_rx(
            self, config.backends["MyLidarr"], release,
        )

        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)
