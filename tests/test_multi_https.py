import unittest
from helpers import db, irc, backends, web, browser, misc
from helpers.misc import Release

channel = "#multi"
config = misc.Config(
    config_file="multi_https.toml",
    irc_channels=[channel],
    irc_users=["bipbopimalsobot"],
    backends=[
        backends.Backend("my_sonarr"),
        backends.Backend("my_lidarr"),
        backends.Backend("my_radarr"),
    ],
)


class SingleTest(unittest.TestCase):
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
            messages=[
                "Old: httpstitle",
                "Category: color tree fruit;",
                "PATH: https://example/f?id=12345",
            ],
            channel=channel,
            title="httpstitle",
            url="https://example/dl.php/12345/cfgstr/httpstitle.jpg",
            indexer="Multi",
            backends=[b.name for b in config.backends],
        )

        irc.announce(release)
        backends.max_announcements(self, "my_sonarr", 0)
        backends.max_announcements(self, "my_radarr", 0)
        backends.max_announcements(self, "my_lidarr", 0)
        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)

        irc.announce(release)
        backends.max_announcements(self, "my_sonarr", 0)
        backends.max_announcements(self, "my_radarr", 0)
        backends.max_announcements(self, "my_lidarr", 0)
        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)

        irc.announce(release)

        backends.check_rx(
            self, "my_sonarr", release,
        )
        backends.check_rx(
            self, "my_radarr", release,
        )
        backends.check_rx(
            self, "my_lidarr", release,
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self, config, release,
        )

    def test_sonarr_snatch(self):
        release = Release(
            messages=[
                "Old: second multi ",
                "Category: color;",
                "PATH: https://example/a?id=54321",
            ],
            channel=channel,
            title="second multi",
            url="https://example/dl.php/54321/cfgstr/second+multi.jpg",
            indexer="Multi",
            backends=[b.name for b in config.backends],
            snatches=["my_sonarr"],
        )

        backends.send_approved("my_sonarr", True)

        irc.announce(release)
        irc.announce(release)
        irc.announce(release)

        backends.check_rx(
            self, "my_sonarr", release,
        )
        backends.max_announcements(self, "my_radarr", 0)
        backends.max_announcements(self, "my_lidarr", 0)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self, config, release,
        )

    def test_renotify_lidarr(self):
        release = Release(
            messages=["Old: third ", "Category: fruit;", "PATH: https://ex/a?id=99"],
            channel=channel,
            title="third",
            url="https://ex/dl.php/99/cfgstr/third.jpg",
            indexer="Multi",
            backends=[b.name for b in config.backends],
            snatches=["my_radarr"],
        )

        backends.send_approved("my_radarr", True)

        irc.announce(release)
        irc.announce(release)
        irc.announce(release)

        backends.check_rx(
            self, "my_radarr", release,
        )
        backends.max_announcements(self, "my_sonarr", 1)
        backends.max_announcements(self, "my_lidarr", 1)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self, config, release,
        )

        backends.send_approved("my_lidarr", True)
        browser.renotify(self, config, table_row=1, backend="my_sonarr", success=False)
        browser.renotify(self, config, table_row=1, backend="my_radarr", success=False)
        browser.renotify(self, config, table_row=1, backend="my_lidarr", success=True)

        release.snatches.append("my_lidarr")

        backends.check_rx(
            self, "my_lidarr", release,
        )
        backends.max_announcements(self, "my_sonarr", 1)
        backends.max_announcements(self, "my_radarr", 1)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 2)

        misc.check_announced(
            self, config, release,
        )

    def test_non_capture_with_match(self):
        release = Release(
            messages=[
                "Old: some title",
                "Category: color tree fruit; misc stuff",
                "PATH: https://example/f?id=1357",
            ],
            channel=channel,
            title="some title",
            url="https://example/dl.php/1357/cfgstr/some+title.jpg",
            indexer="Multi",
            backends=[b.name for b in config.backends],
        )

        irc.announce(release)
        irc.announce(release)
        irc.announce(release)

        backends.check_rx(
            self, "my_sonarr", release,
        )
        backends.check_rx(
            self, "my_radarr", release,
        )
        backends.check_rx(
            self, "my_lidarr", release,
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self, config, release,
        )
