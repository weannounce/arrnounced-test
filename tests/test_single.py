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
        irc.join_condition.wait()
        backends.run()

    @classmethod
    def tearDownClass(self):
        irc.stop()
        self.irc_thread.join()
        backends.stop()


    def test_single(self):
        print("Running single test")
        #irc.announce("asdfff")
        #test_helper.sonarr_send_approved(True)

        irc.announce("this is a name  -  /cow/ ¤/(- #angry#  -  pasta and sauce")

        #await asyncio.sleep(2)

        sr = backends.sonarr_received()
        if sr == None:
            print("SR was None")
        else:
            print("SR: " + str(sr))

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
