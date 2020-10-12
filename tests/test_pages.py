import unittest
from helpers import db, irc, backends, web, misc
from helpers.misc import Release

trackers = [
    {"channel": "#simple1", "name": "Simple1", "url": "smth"},
    {"channel": "#simple2", "name": "Simple2", "url": "else"},
    {"channel": "#simple3", "name": "Simple3", "url": "or"},
]
backens = ["Sonarr", "Radarr", "Lidarr"]
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
        misc.tearDownClass(config)

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

        misc.check_announcements(self, config, releases, [])

    def test_snatches(self):

        releases = []
        snatches = []
        for i in range(90):
            tracker = trackers[i % 3]
            release = Release(
                messages=["title {} : else {}".format(i, i)],
                channel=tracker["channel"],
                title="title {}".format(i),
                url="{}: else {}".format(tracker["url"], i),
                indexer=tracker["name"],
                backends=["Sonarr", "Radarr", "Lidarr"],
            )

            if i % 3 == 0:
                backends.sonarr_send_approved(True)
                release.snatches.append("Sonarr")
                snatches.append(release)
            elif i % 5 == 0:
                backends.radarr_send_approved(True)
                release.snatches.append("Radarr")
                snatches.append(release)
            elif i % 7 == 0:
                backends.lidarr_send_approved(True)
                release.snatches.append("Lidarr")
                snatches.append(release)
            irc.announce(release, wait=0.3)
            releases.append(release)

        backends.sonarr_max_announcements(self, 90)
        backends.radarr_max_announcements(self, 90)
        backends.lidarr_max_announcements(self, 90)

        misc.check_announcements(self, config, releases, snatches)
