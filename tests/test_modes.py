import unittest
from helpers import db, irc, backends, web, misc

channel = "#simple1"
config = misc.Config(
    config_file="modes.toml",
    irc_channels=[channel],
    irc_users=["bipbopmodes"],
    backends={b[0]: backends.Backend(b[0], b[1]) for b in [("MySonarr", "sonapikey1")]},
)


class DelayTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        misc.setUpClass(config, start_browser=False)

    @classmethod
    def tearDownClass(self):
        misc.tearDownClass(config)

    @db.db_session
    def setUp(self):
        backends.clear_all_backends()
        db.clear_db()

    def tearDown(self):
        web.logout()

    # The log is checked for errors afterwards. No other checks performed
    def test_modes(self):
        # Single RFC1459 mode
        irc.mode("o", channel, add=True)
        irc.mode("o", channel, add=False)

        # Double RFC1459 modes
        irc.mode("ov", channel, add=True)
        irc.mode("ov", channel, add=False)

        # Single none-RFC1459 mode
        irc.mode("a", channel, add=True)
        irc.mode("a", channel, add=False)

        # Mixed modes
        irc.mode("ao", channel, add=True)
        irc.mode("ao", channel, add=False)
