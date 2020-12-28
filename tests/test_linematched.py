import unittest
from helpers import db, irc, backends, web, misc
from helpers.misc import Release

channel = "#linematched"
config = misc.Config(
    config_file="linematched.toml",
    irc_channels=[channel],
    irc_users=["linematcherbot"],
    backends={
        b[0]: backends.Backend(b[0], b[1])
        for b in [
            ("line_sonarr", "lineapison"),
            ("line_lidarr", "lineapilid"),
            ("line_radarr", "lineapirad"),
        ]
    },
)


class LineMatchedTest(unittest.TestCase):
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

    def test_match_all(self):
        release = Release(
            messages=["tags: tag1|qwert|tag3 - extractone: SetRegex% : ; 2>1"],
            channel=channel,
            title="IF 2%21%3D1 tag1 qwert",
            url="matched: mfix1&_mfix2%26_SetRegex%_SetRegex%25_IS1",
            indexer="Linematched",
            backends=config.backends.keys(),
        )

        irc.announce(release)

        backends.max_announcements(self, "line_sonarr", 1)
        backends.max_announcements(self, "line_radarr", 1)
        backends.max_announcements(self, "line_lidarr", 1)
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
            backends=config.backends.keys(),
        )

        irc.announce(release)

        backends.max_announcements(self, "line_sonarr", 1)
        backends.max_announcements(self, "line_radarr", 1)
        backends.max_announcements(self, "line_lidarr", 1)
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

        backends.max_announcements(self, "line_sonarr", 0)
        backends.max_announcements(self, "line_radarr", 0)
        backends.max_announcements(self, "line_lidarr", 0)
        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)

    def test_all_variables_missing(self):
        release = Release(messages=["test - test"], channel=channel,)

        irc.announce(release)

        backends.max_announcements(self, "line_sonarr", 0)
        backends.max_announcements(self, "line_radarr", 0)
        backends.max_announcements(self, "line_lidarr", 0)
        self.assertEqual(db.nr_announcements(), 0)
        self.assertEqual(db.nr_snatches(), 0)
