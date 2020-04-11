import asyncio
import unittest
from helpers import db, irc, backends
from threading import Thread
import time

channel = "#arrtstchnl"
class SingleTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.irc_thread = Thread(target=irc.run)
        self.irc_thread.start()
        backends.run()
        irc.ready_event.wait()
        db.init()

    @classmethod
    def tearDownClass(self):
        irc.stop()
        self.irc_thread.join()
        backends.stop()

    @db.db_session
    def setUp(self):
        backends.clear_all_backends()
        db.clear_db()

    @db.db_session
    def test_single(self):
        backends.sonarr_send_approved(True)

        irc.announce(channel, "this is a name  -  /cow/ ¤/(- #angry#  -  pasta and sauce")

        backends.check_sonarr_rx(self, "this is a name ",
        "animal: cow &mood=angry f1: first_fixed f2: fixed_second",
        "Single")

        backends.radarr_received()
        backends.lidarr_received()
        self.assertEqual(len(db.get_announced()), 1)
        self.assertEqual(len(db.get_snatched()), 1)

        db.check_announced(self, "this is a name",
                "animal: cow &mood=angry f1: first_fixed f2: fixed_second",
                "Single",
                ["Sonarr", "Radarr", "Lidarr"],
                ["Sonarr"])
