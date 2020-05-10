import unittest
from helpers import db, irc, backends, web, browser, misc
from helpers.misc import Release

channel = "#single"
config = misc.Config(config_file="single_multi.cfg", channels=[channel])


class SingleTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        misc.setUpClass(config)

    @classmethod
    def tearDownClass(self):
        misc.tearDownClass()

    @db.db_session
    def setUp(self):
        backends.clear_all_backends()
        db.clear_db()

    def tearDown(self):
        web.logout()

    def test_no_match(self):
        release = Release(
            messages=["this is a name  -  cow/ ¤/(- #angry#  -  pasta and sauce"],
            channel=channel,
        )

        irc.announce(release)

        backends.sonarr_max_announcements(self, 0)
        backends.radarr_max_announcements(self, 0)
        backends.lidarr_max_announcements(self, 0)
        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)

    def test_no_snatch(self):
        release = Release(
            messages=["this is a name  -  /cow/ ¤/(- #angry#  -  pasta and sauce"],
            channel=channel,
            title="this is a name",
            url="animal: cow &mood=angry f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr", "Radarr", "Lidarr"],
        )

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
            self, release,
        )

    def test_sonarr_snatch(self):
        release = Release(
            messages=["son snatch  -  /dog/ ¤/(- #sad#  -  pasta"],
            channel=channel,
            title="son snatch",
            url="animal: dog &mood=sad f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr", "Radarr", "Lidarr"],
            snatches=["Sonarr"],
        )

        backends.sonarr_send_approved(True)

        irc.announce(release)

        backends.check_sonarr_rx(
            self, release,
        )

        backends.radarr_max_announcements(self, 1)
        backends.lidarr_max_announcements(self, 1)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self, release,
        )

    def test_radarr_snatch(self):
        release = Release(
            messages=["rad snatch  -  /cat/ ¤/(- #happy#  -  pasta"],
            channel=channel,
            title="rad snatch",
            url="animal: cat &mood=happy f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr", "Radarr", "Lidarr"],
            snatches=["Radarr"],
        )

        backends.radarr_send_approved(True)

        irc.announce(release)

        backends.check_radarr_rx(
            self, release,
        )

        backends.sonarr_max_announcements(self, 1)
        backends.lidarr_max_announcements(self, 1)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self, release,
        )

    def test_lidarr_snatch(self):
        release = Release(
            messages=["lid snatch  -  /rat/ ¤/(- #curios#  -  pasta"],
            channel=channel,
            title="lid snatch",
            url="animal: rat &mood=curios f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr", "Radarr", "Lidarr"],
            snatches=["Lidarr"],
        )

        backends.lidarr_send_approved(True)

        irc.announce(release)

        backends.check_lidarr_rx(
            self, release,
        )

        backends.radarr_max_announcements(self, 1)
        backends.sonarr_max_announcements(self, 1)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self, release,
        )

    def test_renotify_radarr(self):
        release = Release(
            messages=["son snatch2  -  /horsie/ ¤/(- #calm#  -  pasta"],
            channel=channel,
            title="son snatch2",
            url="animal: horsie &mood=calm f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr", "Radarr", "Lidarr"],
            snatches=["Sonarr"],
        )

        backends.sonarr_send_approved(True)

        irc.announce(release)

        backends.check_sonarr_rx(
            self, release,
        )

        backends.radarr_max_announcements(self, 1)
        backends.lidarr_max_announcements(self, 1)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self, release,
        )

        backends.radarr_send_approved(True)

        browser.renotify(self, table_row=1, backend="Sonarr", success=False)
        browser.renotify(self, table_row=1, backend="Lidarr", success=False)
        browser.renotify(self, table_row=1, backend="Radarr", success=True)

        release.snatches.append("Radarr")

        backends.check_radarr_rx(
            self, release,
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 2)

        db.check_announced(
            self, release,
        )

    def test_renotify_nonexistant(self):
        release = Release(
            messages=["title  -  /some/ ¤/(- #thing#  -  pasta"],
            channel=channel,
            title="title",
            url="animal: some &mood=thing f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr", "Radarr", "Lidarr"],
        )

        irc.announce(release)

        backends.sonarr_max_announcements(self, 1)
        backends.radarr_max_announcements(self, 1)
        backends.lidarr_max_announcements(self, 1)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self, release,
        )

        web.login()
        web.renotify(self, db.get_announcement(), "NonExistant")

        backends.sonarr_max_announcements(self, 1)
        backends.radarr_max_announcements(self, 1)
        backends.lidarr_max_announcements(self, 1)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)
