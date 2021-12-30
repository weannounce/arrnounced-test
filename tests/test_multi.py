import unittest
from helpers import db, irc, backends, web, browser, misc
from helpers.misc import Release

channel = "#multi"
config = misc.Config(
    config_file="single_multi.toml",
    web_username="admin",
    web_password="password",
    irc_channels=[channel],
    irc_users=["bipbopimalsobot"],
    backends={
        b[0]: backends.Backend(b[0], b[1])
        for b in [
            ("my_sonarr", "abcdef123"),
            ("my_lidarr", "123456789"),
            ("my_radarr", "987654321"),
        ]
    },
)


class MultiTest(unittest.TestCase):
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
                "Old: multi title",
                "Category: color tree fruit;",
                "PATH: https://example/f?id=12345",
            ],
            channel=channel,
            title="multi title",
            url="http://example/dl.php/12345/config_string/multi+title.jpg",
            indexer="Multi",
            backends=config.backends.keys(),
        )

        irc.announce(release, wait=0.5)
        backends.max_announcements(self, "my_sonarr", 0)
        backends.max_announcements(self, "my_radarr", 0)
        backends.max_announcements(self, "my_lidarr", 0)
        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)

        irc.announce(release, wait=0.5)
        backends.max_announcements(self, "my_sonarr", 0)
        backends.max_announcements(self, "my_radarr", 0)
        backends.max_announcements(self, "my_lidarr", 0)
        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)

        misc.announce_await_push(self, release)

        backends.check_first_rx(
            self,
            config.backends["my_sonarr"],
            release,
        )
        backends.check_first_rx(
            self,
            config.backends["my_radarr"],
            release,
        )
        backends.check_first_rx(
            self,
            config.backends["my_lidarr"],
            release,
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self,
            config,
            release,
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
            url="http://example/dl.php/54321/config_string/second+multi.jpg",
            indexer="Multi",
            backends=["my_sonarr"],
            snatches=["my_sonarr"],
        )

        backends.send_approved("my_sonarr", True)

        irc.announce(release)
        irc.announce(release)
        misc.announce_await_push(self, release)

        backends.check_first_rx(
            self,
            config.backends["my_sonarr"],
            release,
        )
        backends.max_announcements(self, "my_radarr", 0)
        backends.max_announcements(self, "my_lidarr", 0)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self,
            config,
            release,
        )

    def test_renotify_lidarr(self):
        release = Release(
            messages=["Old: third ", "Category: fruit;", "PATH: https://ex/a?id=99"],
            channel=channel,
            title="third",
            url="http://ex/dl.php/99/config_string/third.jpg",
            indexer="Multi",
            backends=["my_radarr"],
            snatches=["my_radarr"],
        )

        backends.send_approved("my_radarr", True)

        irc.announce(release)
        irc.announce(release)
        misc.announce_await_push(self, release)

        backends.check_first_rx(
            self,
            config.backends["my_radarr"],
            release,
        )
        backends.max_announcements(self, "my_sonarr", 0)
        backends.max_announcements(self, "my_lidarr", 0)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self,
            config,
            release,
        )

        backends.send_approved("my_lidarr", True)
        browser.renotify(self, config, table_row=1, backend="my_sonarr", success=False)
        browser.renotify(self, config, table_row=1, backend="my_radarr", success=False)
        browser.renotify(self, config, table_row=1, backend="my_lidarr", success=True)

        release.snatches.append("my_lidarr")

        backends.check_first_rx(
            self,
            config.backends["my_lidarr"],
            release,
        )
        backends.max_announcements(self, "my_sonarr", 1)
        backends.max_announcements(self, "my_radarr", 1)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 2)

        misc.check_announced(
            self,
            config,
            release,
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
            url="http://example/dl.php/1357/config_string/some+title.jpg",
            indexer="Multi",
            backends=config.backends.keys(),
        )

        irc.announce(release)
        irc.announce(release)
        misc.announce_await_push(self, release)

        backends.check_first_rx(
            self,
            config.backends["my_sonarr"],
            release,
        )
        backends.check_first_rx(
            self,
            config.backends["my_radarr"],
            release,
        )
        backends.check_first_rx(
            self,
            config.backends["my_lidarr"],
            release,
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self,
            config,
            release,
        )
