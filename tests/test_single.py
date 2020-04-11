import asyncio
import unittest
from helpers import irc, backends
from threading import Thread
import time

class SingleTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.irc_thread = Thread(target=irc.run)
        self.irc_thread.start()
        backends.run()
        irc.ready_event.wait()

    @classmethod
    def tearDownClass(self):
        irc.stop()
        self.irc_thread.join()
        backends.stop()

    def setUp(self):
        backends.clear_all_backends()

    #def tearDown(self):


    def test_single(self):
        backends.sonarr_send_approved(True)

        irc.announce("this is a name  -  /cow/ ¤/(- #angry#  -  pasta and sauce")

        backends.check_sonarr_rx(self, "this is a name ",
        "animal: cow &mood=angry f1: first_fixed f2: fixed_second",
        "IrcSingle")

        backends.radarr_received()
        backends.lidarr_received()
