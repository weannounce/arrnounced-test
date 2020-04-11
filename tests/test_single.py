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


    def test_single(self):
        print("Running single test")
        backends.sonarr_send_approved(True)

        irc.announce("this is a name  -  /cow/ ¤/(- #angry#  -  pasta and sauce")

        sr = backends.sonarr_received()
        self.assertNotEqual(sr, None, "Not received by Sonarr")
        self.assertEqual(sr["title"], "this is a name ")
        self.assertEqual(sr["downloadUrl"], "animal: cow &mood=angry f1: first_fixed f2: fixed_second")

        sr = backends.radarr_received()
        if sr == None:
            print("SR was None")
        else:
            print("SR: " + str(sr))

        sr = backends.lidarr_received()
        if sr == None:
            print("SR was None")
        else:
            print("SR: " + str(sr))
