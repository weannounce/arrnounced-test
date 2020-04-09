import test_irc
import test_backends

async def announce(message):
    await test_irc.announce(message)

def clear_all_backends():
    return test_backends.clear_all_backends()

def sonarr_received():
    return test_backends.sonarr_received()
def radarr_received():
    return test_backends.radarr_received()
def lidarr_received():
    return test_backends.lidarr_received()

def sonarr_send(response):
    test_backends.sonarr_send(response)
def radarr_send(response):
    test_backends.radarr_send(response)
def lidarr_send(response):
    test_backends.lidarr_send(response)

def sonarr_send_approved(approved):
    test_backends.sonarr_send_approved(approved)
def radarr_send_approved(approved):
    test_backends.radarr_send_approved(approved)
def lidarr_send_approved(approved):
    test_backends.lidarr_send_approved(approved)
