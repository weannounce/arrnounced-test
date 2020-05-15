import unittest
from helpers import db, irc, backends, web, misc
from helpers.misc import Release

config = misc.Config(
    config_file="pages.cfg",
    irc_channels=["#simple1", "#simple2", "#simple3"],
    irc_users=["bipbopsimple1", "bipbopsimple2", "bipbopsimple3"],
)


class DelayTest(unittest.TestCase):
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

    def test_no_snatch(self):

        for i in range(40):
            release = Release(
                messages=["title {} : stuff {}".format(i, i)],
                channel="simple1",
                title="title {}".format(i),
                url="smth: something {}".format(i),
                indexer="Simple1",
                backends=["Sonarr", "Radarr", "Lidarr"],
            )

            irc.announce(release, wait=0)
        # time.sleep(6)

        # backends.sonarr_max_announcements(self, 0)
        # backends.radarr_max_announcements(self, 0)
        # backends.lidarr_max_announcements(self, 0)

        # time.sleep(2)

        # backends.check_sonarr_rx(
        #    self, release,
        # )
        # backends.check_radarr_rx(
        #    self, release,
        # )
        # backends.check_lidarr_rx(
        #    self, release,
        # )

        # self.assertEqual(db.nr_announcements(), 1)
        # self.assertEqual(db.nr_snatches(), 0)

        # misc.check_announced(
        #    self, config, release,
        # )
