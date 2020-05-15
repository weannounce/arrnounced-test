import unittest
from helpers import db, irc, backends, web, misc
from helpers.misc import Release

trackers = [
    {"channel": "#simple1", "name": "Simple1", "url": "smth"},
    {"channel": "#simple2", "name": "Simple2", "url": "else"},
    {"channel": "#simple3", "name": "Simple3", "url": "or"},
]
config = misc.Config(
    config_file="pages.cfg",
    irc_channels=[t["channel"] for t in trackers],
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

        releases = []
        for i in range(90):
            tracker = trackers[i % 3]
            release = Release(
                messages=["title {} : something {}".format(i, i)],
                channel=tracker["channel"],
                title="title {}".format(i),
                url="{}: something {}".format(tracker["url"], i),
                indexer=tracker["name"],
                backends=["Sonarr", "Radarr", "Lidarr"],
            )

            irc.announce(release, wait=0.3)
            releases.append(release)

        for release in releases:
            backends.check_sonarr_rx(
                self, release,
            )
            backends.check_radarr_rx(
                self, release,
            )
            backends.check_lidarr_rx(
                self, release,
            )

        db.check_announcements(self, releases)

        # misc.check_announced(
        #   self, config, release,
        # )
