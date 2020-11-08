import unittest
from helpers import db, irc, backends, web, browser, misc
from helpers.misc import Release
import selenium

channel = "#single"
config = misc.Config(
    config_file="notify_sonarr.cfg", irc_channels=[channel], irc_users=["bipbopiambot"],
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
            messages=["this is a name  -  /cow/ ¤/(- #angry#  -  pasta and sauce"],
            channel=channel,
            title="this is a name",
            url="animal: cow &mood=angry f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr"],
        )

        irc.announce(release)

        backends.check_sonarr_rx(
            self, release,
        )
        backends.radarr_max_announcements(self, 0)
        backends.lidarr_max_announcements(self, 0)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self, config, release,
        )

    def test_sonarr_snatch(self):
        release = Release(
            messages=["son snatch  -  /dog/ ¤/(- #sad#  -  pasta"],
            channel=channel,
            title="son snatch",
            url="animal: dog &mood=sad f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr"],
            snatches=["Sonarr"],
        )

        backends.sonarr_send_approved(True)

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

    def test_renotify_radarr(self):
        release = Release(
            messages=["son snatch2  -  /horsie/ ¤/(- #calm#  -  pasta"],
            channel=channel,
            title="son snatch2",
            url="animal: horsie &mood=calm f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr"],
            snatches=["Sonarr"],
        )

        backends.sonarr_send_approved(True)

        irc.announce(release)

        backends.check_sonarr_rx(
            self, release,
        )

        backends.radarr_max_announcements(self, 1)
        backends.lidarr_max_announcements(self, 0)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self, config, release,
        )

        backends.radarr_send_approved(True)

        browser.renotify(self, config, table_row=1, backend="Sonarr", success=False)
        browser.renotify(self, config, table_row=1, backend="Radarr", success=True)

        self.assertRaises(
            selenium.common.exceptions.NoSuchElementException,
            browser.renotify,
            self,
            config,
            1,
            "Lidarr",
            False,
        )

        release.snatches.append("Radarr")

        backends.check_radarr_rx(
            self, release,
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 2)

        misc.check_announced(
            self, config, release,
        )
