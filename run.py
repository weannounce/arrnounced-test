import test_backends
from test_backends import sonarr_send, radarr_send, lidarr_send, clear_all_backends
import test_irc
import config

#test_backends.run_backends()

test_irc.run_irc(
        config.irc_nickname,
        config.irc_channel,
        config.irc_server,
        config.irc_port)

print("EVERYTHING IS RUNNING")

with test_irc.join_condition:
    print("waiting")
    test_irc.join_condition.wait()

print("done waiting")

test_irc.announce("test message")
