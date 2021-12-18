import unittest
from helpers import db, irc, backends, web, misc
from helpers.misc import Release
import time

channel = "#delay"
config = misc.Config(
    config_file="delay.toml",
    irc_channels=[channel],
    irc_users=["bipbopdelayed"],
    backends={
        b[0]: backends.Backend(b[0], b[1])
        for b in [
            ("delayed_sonarr", "delaysonkey"),
            ("delayed_lidarr", "delaylidkey"),
            ("delayed_radarr", "delayradkey"),
        ]
    },
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
            backends=config.backends.keys(),
        )

        irc.announce(release)
        time.sleep(6)

        backends.max_announcements(self, "delayed_sonarr", 0)
        backends.max_announcements(self, "delayed_radarr", 0)
        backends.max_announcements(self, "delayed_lidarr", 0)

        time.sleep(2)

        backends.check_first_rx(
            self,
            config.backends["delayed_sonarr"],
            release,
        )
        backends.check_first_rx(
            self,
            config.backends["delayed_radarr"],
            release,
        )
        backends.check_first_rx(
            self,
            config.backends["delayed_lidarr"],
            release,
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self,
            config,
            release,
        )
