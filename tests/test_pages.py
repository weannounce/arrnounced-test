import unittest
import time
from helpers import db, backends, web, misc
from helpers.misc import Release

trackers = [
    {"channel": "#simple1", "name": "Simple1", "url": "smth"},
    {"channel": "#simple2", "name": "Simple2", "url": "else"},
    {"channel": "#simple3", "name": "Simple3", "url": "or"},
]
config = misc.Config(
    config_file="pages.toml",
    irc_channels=[t["channel"] for t in trackers],
    irc_users=["bipbopsimple1", "bipbopsimple2", "bipbopsimple3"],
    backends={
        b[0]: backends.Backend(b[0], b[1])
        for b in [
            ("MySonarr", "simplesonkey"),
            ("MyLidarr", "simplelidkey"),
            ("MyRadarr", "simpleradkey"),
        ]
    },
)


class PagesTest(unittest.TestCase):
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
                messages=[f"title {i} : something {i}"],
                channel=tracker["channel"],
                title=f"title {i}",
                url=f"{tracker['url']}: something {i}",
                indexer=tracker["name"],
                backends=config.backends.keys(),
            )

            misc.announce_await_push(self, release, wait=0)
            releases.append(release)

        # Wait for all to complete
        time.sleep(1)

        for release in releases:
            backends.find_and_check_rx(
                self,
                config.backends["MySonarr"],
                release,
            )
            backends.find_and_check_rx(
                self,
                config.backends["MyRadarr"],
                release,
            )
            backends.find_and_check_rx(
                self,
                config.backends["MyLidarr"],
                release,
            )

        misc.check_announcements(self, config, releases, [])

    def test_snatches(self):

        releases = []
        snatches = []
        for i in range(90):
            tracker = trackers[i % 3]
            release = Release(
                messages=[f"title {i} : else {i}"],
                channel=tracker["channel"],
                title=f"title {i}",
                url=f"{tracker['url']}: else {i}",
                indexer=tracker["name"],
                backends=config.backends.keys(),
            )

            if i % 3 == 0:
                backends.send_approved_title("MySonarr", release, True)
                release.snatches.append("MySonarr")
                snatches.append(release)
            elif i % 5 == 0:
                backends.send_approved_title("MyRadarr", release, True)
                release.snatches.append("MyRadarr")
                snatches.append(release)
            elif i % 7 == 0:
                backends.send_approved_title("MyLidarr", release, True)
                release.snatches.append("MyLidarr")
                snatches.append(release)
            misc.announce_await_push(self, release, wait=0)
            releases.append(release)

        # Wait for all to complete
        time.sleep(1)

        backends.max_announcements(self, "MySonarr", 90)
        backends.max_announcements(self, "MyRadarr", 90)
        backends.max_announcements(self, "MyLidarr", 90)

        misc.check_announcements(self, config, releases, snatches)
