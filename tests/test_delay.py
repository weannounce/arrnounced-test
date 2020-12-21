import unittest
from helpers import db, irc, backends, web, misc
from helpers.misc import Release
import time

channel = "#delay"
config = misc.Config(
    config_file="delay.toml",
    irc_channels=[channel],
    irc_users=["bipbopdelayed"],
    backends=[
        backends.Backend("delayed_sonarr"),
        backends.Backend("delayed_lidarr"),
        backends.Backend("delayed_radarr"),
    ],
)


class DelayTest(unittest.TestCase):
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

    def test_no_snatch(self):
        release = Release(
            messages=["title 1 - stuff 1"],
            channel=channel,
            title="title 1",
            url="stuff: stuff 1",
            indexer="Delay",
            backends=[b.name for b in config.backends],
        )

        irc.announce(release)
        time.sleep(6)

        backends.max_announcements(self, "delayed_sonarr", 0)
        backends.max_announcements(self, "delayed_radarr", 0)
        backends.max_announcements(self, "delayed_lidarr", 0)

        time.sleep(2)

        backends.check_rx(
            self, "delayed_sonarr", release,
        )
        backends.check_rx(
            self, "delayed_radarr", release,
        )
        backends.check_rx(
            self, "delayed_lidarr", release,
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self, config, release,
        )
