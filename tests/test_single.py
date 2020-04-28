import unittest
from helpers import db, irc, backends, web, browser
from threading import Thread

channel = "#single"


class SingleTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.irc_thread = Thread(target=irc.run)
        self.irc_thread.start()
        backends.run()
        irc.ready_event.wait()
        db.init()
        browser.init()

    @classmethod
    def tearDownClass(self):
        irc.stop()
        self.irc_thread.join()
        backends.stop()
        db.stop()
        browser.stop()

    @db.db_session
    def setUp(self):
        backends.clear_all_backends()
        db.clear_db()

    def tearDown(self):
        web.logout()

    def test_no_match(self):
        irc.announce(
            channel, "this is a name  -  cow/ ¤/(- #angry#  -  pasta and sauce"
        )

        backends.sonarr_max_announcements(self, 0)
        backends.radarr_max_announcements(self, 0)
        backends.lidarr_max_announcements(self, 0)
        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)

    def test_no_snatch(self):
        irc.announce(
            channel, "this is a name  -  /cow/ ¤/(- #angry#  -  pasta and sauce"
        )

        backends.check_sonarr_rx(
            self,
            "this is a name",
            "animal: cow &mood=angry f1: first_fixed f2: fixed_second",
            "Single",
        )
        backends.check_radarr_rx(
            self,
            "this is a name",
            "animal: cow &mood=angry f1: first_fixed f2: fixed_second",
            "Single",
        )
        backends.check_lidarr_rx(
            self,
            "this is a name",
            "animal: cow &mood=angry f1: first_fixed f2: fixed_second",
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        db.check_announced(
            self,
            "this is a name",
            "animal: cow &mood=angry f1: first_fixed f2: fixed_second",
            "Single",
            ["Sonarr", "Radarr", "Lidarr"],
        )

        browser.check_announced(
            self, "this is a name", "Single", ["Sonarr", "Radarr", "Lidarr"],
        )

    def test_sonarr_snatch(self):
        backends.sonarr_send_approved(True)

        irc.announce(channel, "son snatch  -  /dog/ ¤/(- #sad#  -  pasta")

        backends.check_sonarr_rx(
            self,
            "son snatch",
            "animal: dog &mood=sad f1: first_fixed f2: fixed_second",
            "Single",
        )

        backends.radarr_max_announcements(self, 1)
        backends.lidarr_max_announcements(self, 1)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        db.check_announced(
            self,
            "son snatch",
            "animal: dog &mood=sad f1: first_fixed f2: fixed_second",
            "Single",
            ["Sonarr", "Radarr", "Lidarr"],
            ["Sonarr"],
        )

    def test_radarr_snatch(self):
        backends.radarr_send_approved(True)

        irc.announce(channel, "rad snatch  -  /cat/ ¤/(- #happy#  -  pasta")

        backends.check_radarr_rx(
            self,
            "rad snatch",
            "animal: cat &mood=happy f1: first_fixed f2: fixed_second",
            "Single",
        )

        backends.sonarr_max_announcements(self, 1)
        backends.lidarr_max_announcements(self, 1)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        db.check_announced(
            self,
            "rad snatch",
            "animal: cat &mood=happy f1: first_fixed f2: fixed_second",
            "Single",
            ["Sonarr", "Radarr", "Lidarr"],
            ["Radarr"],
        )

    def test_lidarr_snatch(self):
        backends.lidarr_send_approved(True)

        irc.announce(channel, "lid snatch  -  /rat/ ¤/(- #curios#  -  pasta")

        backends.check_lidarr_rx(
            self,
            "lid snatch",
            "animal: rat &mood=curios f1: first_fixed f2: fixed_second",
        )

        backends.radarr_max_announcements(self, 1)
        backends.sonarr_max_announcements(self, 1)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        db.check_announced(
            self,
            "lid snatch",
            "animal: rat &mood=curios f1: first_fixed f2: fixed_second",
            "Single",
            ["Sonarr", "Radarr", "Lidarr"],
            ["Lidarr"],
        )

    def test_renotify_radarr(self):
        backends.sonarr_send_approved(True)
        backends.sonarr_send_approved(True)

        irc.announce(channel, "son snatch2  -  /horsie/ ¤/(- #calm#  -  pasta")

        backends.check_sonarr_rx(
            self,
            "son snatch2",
            "animal: horsie &mood=calm f1: first_fixed f2: fixed_second",
            "Single",
        )

        backends.radarr_max_announcements(self, 1)
        backends.lidarr_max_announcements(self, 1)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        db.check_announced(
            self,
            "son snatch2",
            "animal: horsie &mood=calm f1: first_fixed f2: fixed_second",
            "Single",
            ["Sonarr", "Radarr", "Lidarr"],
            ["Sonarr"],
        )

        backends.radarr_send_approved(True)
        web.login()
        web.renotify(self, db.get_announce_id(), "Radarr")

        backends.check_radarr_rx(
            self,
            "son snatch2",
            "animal: horsie &mood=calm f1: first_fixed f2: fixed_second",
            "Single",
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 2)

        db.check_announced(
            self,
            "son snatch2",
            "animal: horsie &mood=calm f1: first_fixed f2: fixed_second",
            "Single",
            ["Sonarr", "Radarr", "Lidarr"],
            ["Sonarr", "Radarr"],
        )
