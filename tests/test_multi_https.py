import unittest
from helpers import db, irc, backends, web, browser, misc
from helpers.misc import Release

channel = "#multi"
config = misc.Config(
    config_file="multi_https.cfg",
    irc_channels=[channel],
    irc_users=["bipbopimalsobot"],
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
            backends=["Sonarr", "Radarr", "Lidarr"],
        )

        irc.announce(release)
        backends.sonarr_max_announcements(self, 0)
        backends.radarr_max_announcements(self, 0)
        backends.lidarr_max_announcements(self, 0)
        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)

        irc.announce(release)
        backends.sonarr_max_announcements(self, 0)
        backends.radarr_max_announcements(self, 0)
        backends.lidarr_max_announcements(self, 0)
        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)

        irc.announce(release)

        backends.check_sonarr_rx(
            self, release,
        )
        backends.check_radarr_rx(
            self, release,
        )
        backends.check_lidarr_rx(
            self, release,
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
            backends=["Sonarr", "Radarr", "Lidarr"],
            snatches=["Sonarr"],
        )

        backends.sonarr_send_approved(True)

        irc.announce(release)
        irc.announce(release)
        irc.announce(release)

        backends.check_sonarr_rx(
            self, release,
        )
        backends.radarr_max_announcements(self, 0)
        backends.lidarr_max_announcements(self, 0)

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
            backends=["Sonarr", "Radarr", "Lidarr"],
            snatches=["Radarr"],
        )

        backends.radarr_send_approved(True)

        irc.announce(release)
        irc.announce(release)
        irc.announce(release)

        backends.check_radarr_rx(
            self, release,
        )
        backends.sonarr_max_announcements(self, 1)
        backends.lidarr_max_announcements(self, 1)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self, config, release,
        )

        backends.lidarr_send_approved(True)
        browser.renotify(self, config, table_row=1, backend="Sonarr", success=False)
        browser.renotify(self, config, table_row=1, backend="Radarr", success=False)
        browser.renotify(self, config, table_row=1, backend="Lidarr", success=True)

        release.snatches.append("Lidarr")

        backends.check_lidarr_rx(
            self, release,
        )
        backends.sonarr_max_announcements(self, 1)
        backends.radarr_max_announcements(self, 1)

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
            backends=["Sonarr", "Radarr", "Lidarr"],
        )

        irc.announce(release)
        irc.announce(release)
        irc.announce(release)

        backends.check_sonarr_rx(
            self, release,
        )
        backends.check_radarr_rx(
            self, release,
        )
        backends.check_lidarr_rx(
            self, release,
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self, config, release,
        )
