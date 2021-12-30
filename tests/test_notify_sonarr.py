import unittest
from helpers import db, backends, web, browser, misc
from helpers.misc import Release
import selenium

channel = "#single"
config = misc.Config(
    config_file="notify_sonarr.toml",
    irc_channels=[channel],
    irc_users=["bipbopiambot"],
    backends={
        b[0]: backends.Backend(b[0], b[1])
        for b in [("my_sonarr", "abcdef123"), ("my_radarr", "987654321")]
    },
)


class SingleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        misc.setUpClass(config)

    @classmethod
    def tearDownClass(cls):
        misc.tearDownClass(config)

    @db.db_session
    def setUp(self):
        backends.clear_all_backends()
        db.clear_db()

    def tearDown(self):
        web.logout()

    def test_no_snatch(self):
        release = Release(
            messages=["this is a name  -  /cow/ ¤/(- #angry#  -  pasta and sauce"],
            channel=channel,
            title="this is a name",
            url="animal: cow &mood=angry f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["my_sonarr"],
        )

        backends.push_counter = 1
        misc.announce_await_push(self, release)

        backends.check_first_rx(
            self,
            config.backends["my_sonarr"],
            release,
        )
        backends.max_announcements(self, "my_radarr", 0)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self,
            config,
            release,
        )

    def test_sonarr_snatch(self):
        release = Release(
            messages=["son snatch  -  /dog/ ¤/(- #sad#  -  pasta"],
            channel=channel,
            title="son snatch",
            url="animal: dog &mood=sad f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["my_sonarr"],
            snatches=["my_sonarr"],
        )

        backends.send_approved("my_sonarr", True)

        misc.announce_await_push(self, release)

        backends.check_first_rx(
            self,
            config.backends["my_sonarr"],
            release,
        )

        backends.max_announcements(self, "my_radarr", 0)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self,
            config,
            release,
        )

    def test_renotify_existing_radarr(self):
        release = Release(
            messages=["son snatch2  -  /horsie/ ¤/(- #calm#  -  pasta"],
            channel=channel,
            title="son snatch2",
            url="animal: horsie &mood=calm f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["my_sonarr"],
            snatches=["my_sonarr"],
        )

        backends.send_approved("my_sonarr", True)

        misc.announce_await_push(self, release)

        backends.check_first_rx(
            self,
            config.backends["my_sonarr"],
            release,
        )

        backends.max_announcements(self, "my_radarr", 0)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self,
            config,
            release,
        )

        backends.send_approved("my_radarr", True)

        browser.renotify(self, config, table_row=1, backend="my_sonarr", success=False)
        browser.renotify(self, config, table_row=1, backend="my_radarr", success=True)

        self.assertRaises(
            selenium.common.exceptions.NoSuchElementException,
            browser.renotify,
            self,
            config,
            1,
            "my_lidarr",
            False,
        )

        release.snatches.append("my_radarr")

        backends.check_first_rx(
            self,
            config.backends["my_radarr"],
            release,
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 2)

        misc.check_announced(
            self,
            config,
            release,
        )

    def test_renotify_missing_radarr(self):
        release = Release(
            messages=["son snatch2  -  /horsie/ ¤/(- #calm#  -  pasta"],
            channel=channel,
            title="son snatch2",
            url="animal: horsie &mood=calm f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["my_sonarr"],
        )

        misc.announce_await_push(self, release)

        backends.check_first_rx(
            self,
            config.backends["my_sonarr"],
            release,
        )

        backends.max_announcements(self, "my_radarr", 0)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self,
            config,
            release,
        )

        browser.renotify(self, config, table_row=1, backend="my_sonarr", success=False)

        # Causes connection refused
        browser.renotify(
            self, config, table_row=1, backend="missing_radarr", success=False
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)
