import unittest
import time
from helpers import browser, db, irc, backends, web, misc

# from helpers.misc import Release

# channel = "#simple1"
# irc_user = "bipbopstatus1"
# config = misc.Config(
#    config_file="status.cfg", irc_channels=[channel], irc_users=[irc_user],
# )

trackers = [
    {"channel": "#simple1", "name": "Simple1", "url": "smth"},
    {"channel": "#simple2", "name": "Simple2", "url": "else"},
    {"channel": "#simple3", "name": "Simple3", "url": "or"},
]
config = misc.Config(
    config_file="status.toml",
    irc_channels=[t["channel"] for t in trackers],
    irc_users=["bipbopstatus1", "bipbopstatus2", "bipbopstatus3"],
    backends={
        b[0]: backends.Backend(b[0], b[1])
        for b in [
            ("my_sonarr", "simplesonkey"),
            ("my_lidarr", "simplelidkey"),
            ("my_radarr", "simpleradkey"),
        ]
    },
)


class TrackerStatus:
    def __init__(self, type, name, channels, connected=True):
        self.type = type
        self.name = name
        self.channels = channels
        self.connected = connected
        self.last_ann = "Never"
        self.last_snatch = "Never"


class StatusTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        misc.setUpClass(config)
        browser.get_status(config)

    @classmethod
    def tearDownClass(self):
        misc.tearDownClass(config)

    @db.db_session
    def setUp(self):
        backends.clear_all_backends()
        db.clear_db()
        print("------------------")

    def tearDown(self):
        web.logout()

    #def test_kill_client(self):
    #    ts = TrackerStatus("simple1", "Simple1 Announcement", ["#simple1"])
    #    print("KILL test")
    #    #browser.get_status(config)

    #    #browser.check_tracker_status(self, ts)
    #    browser.print_tracker_status(self, ts)
    #    irc.kill("bipbopstatus1", "High treason")
    #    ts.connected = False
    #    #browser.check_tracker_status(self, ts)
    #    browser.print_tracker_status(self, ts)
    #    time.sleep(7)
    #    ts.connected = True
    #    #browser.check_tracker_status(self, ts)
    #    browser.print_tracker_status(self, ts)

    #def test_kick_client(self):
    #    ts = TrackerStatus("simple3", "Simple3 Announcement", ["#simple3"])
    #    print("KICK test")
    #    #browser.get_status(config)
    #    browser.print_tracker_status(self, ts)
    #    irc.kick("bipbopstatus3", ts.channels[0], "Medium treason")
    #    browser.print_tracker_status(self, ts)
    #    irc.join("bipbopstatus3", ts.channels[0])
    #    browser.print_tracker_status(self, ts)

    #def test_part_client(self):
    #    ts = TrackerStatus("simple2", "Simple2 Announcement", ["#simple2"])
    #    print("PART test")
    #    #browser.get_status(config)
    #    browser.print_tracker_status(self, ts)
    #    irc.part("bipbopstatus2", ts.channels[0], "Low treason")
    #    browser.print_tracker_status(self, ts)
    #    irc.join("bipbopstatus2", ts.channels[0])
    #    browser.print_tracker_status(self, ts)

    #def test_join_two(self):
    #    ts = TrackerStatus("simple2", "Simple2 Announcement", ["#simple2"])
    #    print("JOIN 2 test")
    #    browser.print_tracker_status(self, ts)
    #    irc.join("bipbopstatus2", "#single")
    #    browser.print_tracker_status(self, ts)
    #    irc.kick("bipbopstatus2", ts.channels[0], "Come again")
    #    browser.print_tracker_status(self, ts)

    def test_banned(self):
        ts = TrackerStatus("simple1", "Simple1 Announcement", ["#simple1"])
        irc.mode("o", ts.channels[0])
        print("BANNED test")
        irc.ban("bipbopstatus1", ts.channels[0], True)

        browser.print_tracker_status(self, ts)
        irc.part("bipbopstatus1", ts.channels[0], "you may leave")
        browser.print_tracker_status(self, ts)
        irc.invite("bipbopstatus1", ts.channels[0])
        browser.print_tracker_status(self, ts)
        irc.ban("bipbopstatus1", ts.channels[0], False)

        irc.mode("o", ts.channels[0], False)

    # def test_snatches(self):

    #    releases = []
    #    snatches = []
    #    for i in range(90):
    #        tracker = trackers[i % 3]
    #        release = Release(
    #            messages=["title {} : else {}".format(i, i)],
    #            channel=tracker["channel"],
    #            title="title {}".format(i),
    #            url="{}: else {}".format(tracker["url"], i),
    #            indexer=tracker["name"],
    #            backends=["Sonarr", "Radarr", "Lidarr"],
    #        )

    #        if i % 3 == 0:
    #            backends.sonarr_send_approved(True)
    #            release.snatches.append("Sonarr")
    #            snatches.append(release)
    #        elif i % 5 == 0:
    #            backends.radarr_send_approved(True)
    #            release.snatches.append("Radarr")
    #            snatches.append(release)
    #        elif i % 7 == 0:
    #            backends.lidarr_send_approved(True)
    #            release.snatches.append("Lidarr")
    #            snatches.append(release)
    #        irc.announce(release, wait=0.3)
    #        releases.append(release)

    #    backends.sonarr_max_announcements(self, 90)
    #    backends.radarr_max_announcements(self, 90)
    #    backends.lidarr_max_announcements(self, 90)

    #    misc.check_announcements(self, config, releases, snatches)
