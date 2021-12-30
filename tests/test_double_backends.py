import unittest
from helpers import db, backends, web, misc
from helpers.misc import Release

channel = "#simple1"
config = misc.Config(
    config_file="double_backends.toml",
    irc_channels=[channel],
    irc_users=["bipbopsimple1"],
    backends={
        b[0]: backends.Backend(b[0], b[1], b[2])
        for b in [
            ("Sonarr1", "sonapikey1", 10000),
            ("Sonarr2", "sonapikey1", 20000),
            ("Radarr1", "radapikey1", 7878),
            ("Radarr2", "radapikey2", 7879),
            ("Lidarr1", "lidapikey1", 5000),
            ("Lidarr2", "lidapikey2", 6000),
        ]
    },
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
        release = Release(
            messages=["a title : some stuff"],
            channel=channel,
            title="a title",
            url="smth: some stuff",
            indexer="Simple1",
            backends=config.backends.keys(),
        )

        misc.announce_await_push(self, release)

        for backend in config.backends.values():
            backends.check_first_rx(
                self,
                backend,
                release,
            )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self,
            config,
            release,
        )

    def test_radarr1_snatch(self):
        release = Release(
            messages=["two title : another stuff"],
            channel=channel,
            title="two title",
            url="smth: another stuff",
            indexer="Simple1",
            backends=config.backends.keys(),
            snatches=["Radarr1"],
        )

        backends.send_approved("Radarr1", True)

        misc.announce_await_push(self, release)

        backends.check_first_rx(
            self,
            config.backends["Radarr1"],
            release,
        )
        backends.max_announcements(self, "Sonarr1", 1)
        backends.max_announcements(self, "Sonarr2", 1)
        backends.max_announcements(self, "Radarr2", 1)
        backends.max_announcements(self, "Lidarr1", 1)
        backends.max_announcements(self, "Lidarr2", 1)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self,
            config,
            release,
        )

    def test_radarr2_snatch(self):
        release = Release(
            messages=["tree title : the stuff"],
            channel=channel,
            title="tree title",
            url="smth: the stuff",
            indexer="Simple1",
            backends=config.backends.keys(),
            snatches=["Radarr2"],
        )

        backends.send_approved("Radarr2", True)

        misc.announce_await_push(self, release)

        backends.check_first_rx(
            self,
            config.backends["Radarr2"],
            release,
        )
        backends.max_announcements(self, "Sonarr1", 1)
        backends.max_announcements(self, "Sonarr2", 1)
        backends.max_announcements(self, "Radarr1", 1)
        backends.max_announcements(self, "Lidarr1", 1)
        backends.max_announcements(self, "Lidarr2", 1)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self,
            config,
            release,
        )

    def test_sonarr1_snatch(self):
        release = Release(
            messages=["asdf : a stuff"],
            channel=channel,
            title="asdf",
            url="smth: a stuff",
            indexer="Simple1",
            backends=config.backends.keys(),
            snatches=["Sonarr1"],
        )

        backends.send_approved("Sonarr1", True)

        misc.announce_await_push(self, release)

        backends.check_first_rx(
            self,
            config.backends["Sonarr1"],
            release,
        )
        backends.max_announcements(self, "Sonarr2", 1)
        backends.max_announcements(self, "Radarr1", 1)
        backends.max_announcements(self, "Radarr2", 1)
        backends.max_announcements(self, "Lidarr1", 1)
        backends.max_announcements(self, "Lidarr2", 1)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self,
            config,
            release,
        )

    def test_sonarr2_snatch(self):
        release = Release(
            messages=["qwer : b stuff"],
            channel=channel,
            title="qwer",
            url="smth: b stuff",
            indexer="Simple1",
            backends=config.backends.keys(),
            snatches=["Sonarr2"],
        )

        backends.send_approved("Sonarr2", True)

        misc.announce_await_push(self, release)

        backends.check_first_rx(
            self,
            config.backends["Sonarr2"],
            release,
        )
        backends.max_announcements(self, "Sonarr1", 1)
        backends.max_announcements(self, "Radarr1", 1)
        backends.max_announcements(self, "Radarr2", 1)
        backends.max_announcements(self, "Lidarr1", 1)
        backends.max_announcements(self, "Lidarr2", 1)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self,
            config,
            release,
        )

    def test_lidarr1_snatch(self):
        release = Release(
            messages=["yuio : c stuff"],
            channel=channel,
            title="yuio",
            url="smth: c stuff",
            indexer="Simple1",
            backends=config.backends.keys(),
            snatches=["Lidarr1"],
        )

        backends.send_approved("Lidarr1", True)

        misc.announce_await_push(self, release)

        backends.check_first_rx(
            self,
            config.backends["Lidarr1"],
            release,
        )
        backends.max_announcements(self, "Sonarr1", 1)
        backends.max_announcements(self, "Sonarr2", 1)
        backends.max_announcements(self, "Radarr1", 1)
        backends.max_announcements(self, "Radarr2", 1)
        backends.max_announcements(self, "Lidarr2", 1)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self,
            config,
            release,
        )

    def test_lidarr2_snatch(self):
        release = Release(
            messages=["yuio : c stuff"],
            channel=channel,
            title="yuio",
            url="smth: c stuff",
            indexer="Simple1",
            backends=config.backends.keys(),
            snatches=["Lidarr2"],
        )

        backends.send_approved("Lidarr2", True)

        misc.announce_await_push(self, release)

        backends.check_first_rx(
            self,
            config.backends["Lidarr2"],
            release,
        )
        backends.max_announcements(self, "Sonarr1", 1)
        backends.max_announcements(self, "Sonarr2", 1)
        backends.max_announcements(self, "Radarr1", 1)
        backends.max_announcements(self, "Radarr2", 1)
        backends.max_announcements(self, "Lidarr1", 1)

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self,
            config,
            release,
        )
