import asyncio
import unittest
from helpers import irc
from threading import Thread
import time

class SingleTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.irc_thread = Thread(target=irc.run)
        self.irc_thread.start()
        time.sleep(10)
        #test_backends.run_backends()

    @classmethod
    def tearDownClass(self):
        irc.stop()
        self.irc_thread.join()


    def test_single(self):
        print("Running single test")
        irc.announce("asdfff")
        #test_helper.sonarr_send_approved(True)

        #await test_helper.announce("this is a name  -  /cow/ ¤/(- #angry#  -  pasta and sauce")

        #await asyncio.sleep(2)

        #sr = test_helper.sonarr_received()
        #if sr == None:
        #    print("SR was None")
        #else:
        #    print("SR: " + str(sr))

        #sr = test_helper.radarr_received()
        #if sr == None:
        #    print("SR was None")
        #else:
        #    print("SR: " + str(sr))

        #sr = test_helper.lidarr_received()
        #if sr == None:
        #    print("SR was None")
        #else:
        #    print("SR: " + str(sr))
        #return True
