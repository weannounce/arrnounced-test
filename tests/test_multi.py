import unittest
from helpers import db, irc, backends, web, browser, misc
from threading import Thread

channel = "#multi"


class SingleTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.irc_thread = Thread(target=irc.run)
        self.irc_thread.start()
        backends.run()
        db.init()
        browser.init()
        irc.ready_event.wait()

    @classmethod
    def tearDownClass(self):
        irc.stop()
        backends.stop()
        db.stop()
        browser.stop()
        self.irc_thread.join()
        irc.ready_event.clear()

    @db.db_session
    def setUp(self):
        backends.clear_all_backends()
        db.clear_db()

    def tearDown(self):
        web.logout()

    def test_no_snatch(self):
        irc.announce(channel, "Old: multi title")
        backends.sonarr_max_announcements(self, 0)
        backends.radarr_max_announcements(self, 0)
        backends.lidarr_max_announcements(self, 0)
        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)

        irc.announce(channel, "Category: color tree fruit")
        backends.sonarr_max_announcements(self, 0)
        backends.radarr_max_announcements(self, 0)
        backends.lidarr_max_announcements(self, 0)
        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)

        irc.announce(channel, "PATH: https://example/f?id=12345")

        backends.check_sonarr_rx(
            self,
            "multi title",
            "http://example/dl.php/12345/config_string/multi+title.jpg",
            "Multi",
        )
        backends.check_radarr_rx(
            self,
            "multi title",
            "http://example/dl.php/12345/config_string/multi+title.jpg",
            "Multi",
        )
        backends.check_lidarr_rx(
            self,
            "multi title",
            "http://example/dl.php/12345/config_string/multi+title.jpg",
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self,
            "multi title",
            "http://example/dl.php/12345/config_string/multi+title.jpg",
            "Multi",
            ["Sonarr", "Radarr", "Lidarr"],
        )

    def test_sonarr_snatch(self):
        backends.sonarr_send_approved(True)

        irc.announce(channel, "Old: second multi ")
        irc.announce(channel, "Category: color")
        irc.announce(channel, "PATH: https://example/a?id=54321")

        backends.check_sonarr_rx(
            self,
            "second multi",
            "http://example/dl.php/54321/config_string/second+multi.jpg",
            "Multi",
        )
        backends.radarr_max_announcements(self, 0)
        backends.lidarr_max_announcements(self, 0)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self,
            "second multi",
            "http://example/dl.php/54321/config_string/second+multi.jpg",
            "Multi",
            ["Sonarr"],
            ["Sonarr"],
        )

    def test_renotify_lidarr(self):
        backends.radarr_send_approved(True)

        irc.announce(channel, "Old: third ")
        irc.announce(channel, "Category: fruit")
        irc.announce(channel, "PATH: https://ex/a?id=99")

        backends.check_radarr_rx(
            self, "third", "http://ex/dl.php/99/config_string/third.jpg", "Multi"
        )
        backends.radarr_max_announcements(self, 0)
        backends.lidarr_max_announcements(self, 0)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self,
            "third",
            "http://ex/dl.php/99/config_string/third.jpg",
            "Multi",
            ["Radarr"],
            ["Radarr"],
        )

        backends.lidarr_send_approved(True)
        web.login()
        web.renotify(self, db.get_announce_id(), "Lidarr")

        backends.check_lidarr_rx(
            self, "third", "http://ex/dl.php/99/config_string/third.jpg"
        )
        backends.sonarr_max_announcements(self, 0)
        backends.radarr_max_announcements(self, 0)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 2)

        db.check_announced(
            self,
            "third",
            "http://ex/dl.php/99/config_string/third.jpg",
            "Multi",
            ["Radarr"],
            ["Radarr", "Lidarr"],
        )
