import unittest
from helpers import db, irc, backends, web, misc
from helpers.misc import Release

channel = "#linematched"
config = misc.Config(
    config_file="linematched.cfg", irc_channels=[channel], irc_users=["linematcherbot"],
)


class LineMatchedTest(unittest.TestCase):
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

    def test_match_all(self):
        release = Release(
            messages=["tags: tag1|qwert|tag3 - extractone: SetRegex% : ; 2>1"],
            channel=channel,
            title="IF 2%21%3D1 tag1 qwert",
            url="matched: mfix1&_mfix2%26_SetRegex%_SetRegex%25_IS1",
            indexer="Linematched",
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

    def test_extracttags_empty_tag(self):
        release = Release(
            messages=["tags: tag1||tag2 - extractone: SetRegex : ; 1"],
            channel=channel,
            title="IF 1 tag1 tag2",
            url="matched: mfix1&_mfix2%26_SetRegex_SetRegex_IS1",
            indexer="Linematched",
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

    def test_missing_torrent_url(self):
        release = Release(
            messages=["tags: tag1||tag2 - extractone: SetRegex : ; 2"], channel=channel,
        )

        irc.announce(release)

        backends.sonarr_max_announcements(self, 0)
        backends.radarr_max_announcements(self, 0)
        backends.lidarr_max_announcements(self, 0)
        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)

    def test_all_variables_missing(self):
        release = Release(messages=["test - test"], channel=channel,)

        irc.announce(release)

        backends.sonarr_max_announcements(self, 0)
        backends.radarr_max_announcements(self, 0)
        backends.lidarr_max_announcements(self, 0)
        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)
