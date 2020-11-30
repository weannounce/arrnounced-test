import unittest
from helpers import db, irc, backends, web, browser, misc
from helpers.misc import Release

channel = "#single"
config = misc.Config(
    config_file="single_multi.toml",
    web_username="admin",
    web_password="password",
    irc_channels=[channel],
    irc_users=["bipbopiambot"],
)


class SingleTest(unittest.TestCase):
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

    def test_no_match(self):
        release = Release(
            messages=["this is a name  -  cow/ ¤/(- #angry#  -  pasta and sauce"],
            channel=channel,
        )

        irc.announce(release)

        backends.sonarr_max_announcements(self, 0)
        backends.radarr_max_announcements(self, 0)
        backends.lidarr_max_announcements(self, 0)
        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)

    def test_no_snatch(self):
        release = Release(
            messages=["this is a name  -  /cow/ ¤/(- #angry#  -  pasta and sauce"],
            channel=channel,
            title="this is a name",
            url="animal: cow &mood=angry f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr", "Radarr", "Lidarr"],
        )

        irc.announce(release)

        backends.check_sonarr_rx(
            self, release,
        )
        backends.check_radarr_rx(
            self, release,
        )
        backends.check_lidarr_rx(
            self, release,
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self, config, release,
        )

    def test_sonarr_snatch(self):
        release = Release(
            messages=["son snatch  -  /dog/ ¤/(- #sad#  -  pasta"],
            channel=channel,
            title="son snatch",
            url="animal: dog &mood=sad f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr", "Radarr", "Lidarr"],
            snatches=["Sonarr"],
        )

        backends.sonarr_send_approved(True)

        irc.announce(release)

        backends.check_sonarr_rx(
            self, release,
        )

        backends.radarr_max_announcements(self, 1)
        backends.lidarr_max_announcements(self, 1)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self, config, release,
        )

    def test_radarr_snatch(self):
        release = Release(
            messages=["rad snatch  -  /cat/ ¤/(- #happy#  -  pasta"],
            channel=channel,
            title="rad snatch",
            url="animal: cat &mood=happy f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr", "Radarr", "Lidarr"],
            snatches=["Radarr"],
        )

        backends.radarr_send_approved(True)

        irc.announce(release)

        backends.check_radarr_rx(
            self, release,
        )

        backends.sonarr_max_announcements(self, 1)
        backends.lidarr_max_announcements(self, 1)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self, config, release,
        )

    def test_lidarr_snatch(self):
        release = Release(
            messages=["lid snatch  -  /rat/ ¤/(- #curios#  -  pasta"],
            channel=channel,
            title="lid snatch",
            url="animal: rat &mood=curios f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr", "Radarr", "Lidarr"],
            snatches=["Lidarr"],
        )

        backends.lidarr_send_approved(True)

        irc.announce(release)

        backends.check_lidarr_rx(
            self, release,
        )

        backends.radarr_max_announcements(self, 1)
        backends.sonarr_max_announcements(self, 1)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self, config, release,
        )

    def test_renotify_radarr(self):
        release = Release(
            messages=["son snatch2  -  /horsie/ ¤/(- #calm#  -  pasta"],
            channel=channel,
            title="son snatch2",
            url="animal: horsie &mood=calm f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr", "Radarr", "Lidarr"],
            snatches=["Sonarr"],
        )

        backends.sonarr_send_approved(True)

        irc.announce(release)

        backends.check_sonarr_rx(
            self, release,
        )

        backends.radarr_max_announcements(self, 1)
        backends.lidarr_max_announcements(self, 1)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 1)

        misc.check_announced(
            self, config, release,
        )

        backends.radarr_send_approved(True)

        browser.renotify(self, config, table_row=1, backend="Sonarr", success=False)
        browser.renotify(self, config, table_row=1, backend="Lidarr", success=False)
        browser.renotify(self, config, table_row=1, backend="Radarr", success=True)

        release.snatches.append("Radarr")

        backends.check_radarr_rx(
            self, release,
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 2)

        misc.check_announced(
            self, config, release,
        )

    def test_renotify_nonexistant(self):
        release = Release(
            messages=["title  -  /some/ ¤/(- #thing#  -  pasta"],
            channel=channel,
            title="title",
            url="animal: some &mood=thing f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr", "Radarr", "Lidarr"],
        )

        irc.announce(release)

        backends.sonarr_max_announcements(self, 1)
        backends.radarr_max_announcements(self, 1)
        backends.lidarr_max_announcements(self, 1)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self, config, release,
        )

        web.login(config)
        web.renotify(self, config, db.get_announcement(), -1)

        backends.sonarr_max_announcements(self, 1)
        backends.radarr_max_announcements(self, 1)
        backends.lidarr_max_announcements(self, 1)
        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

    def test_no_snatch_second_pattern(self):
        release = Release(
            messages=["this is some name  -  -donkey- ; =grumpy=  -  food: pizza"],
            channel=channel,
            title="this is some name",
            url="animal: donkey &mood=grumpy f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr", "Radarr", "Lidarr"],
        )

        irc.announce(release)

        backends.check_sonarr_rx(
            self, release,
        )
        backends.check_radarr_rx(
            self, release,
        )
        backends.check_lidarr_rx(
            self, release,
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self, config, release,
        )

    def test_non_capture_group_without_match(self):
        release = Release(
            messages=["yet a name - monkey - frustrated -"],
            channel=channel,
            title="yet a name",
            url="animal: monkey &mood=frustrated f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr", "Radarr", "Lidarr"],
        )

        irc.announce(release)

        backends.check_sonarr_rx(
            self, release,
        )
        backends.check_radarr_rx(
            self, release,
        )
        backends.check_lidarr_rx(
            self, release,
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self, config, release,
        )

    def test_non_capture_group_with_match(self):
        release = Release(
            messages=["naaame - bat - splendid - [apple]"],
            channel=channel,
            title="naaame",
            url="animal: bat &mood=splendid f1: first_fixed f2: fixed_second",
            indexer="Single",
            backends=["Sonarr", "Radarr", "Lidarr"],
        )

        irc.announce(release)

        backends.check_sonarr_rx(
            self, release,
        )
        backends.check_radarr_rx(
            self, release,
        )
        backends.check_lidarr_rx(
            self, release,
        )

        self.assertEqual(db.nr_announcements(), 1)
        self.assertEqual(db.nr_snatches(), 0)

        misc.check_announced(
            self, config, release,
        )
