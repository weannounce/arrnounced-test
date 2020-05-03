import asyncio
import pydle
import socket
import time
import threading
from datetime import datetime
from . import config

expected_channels = []
expected_users = []
ready_event = threading.Event()

event_loop = None
client = None
BotBase = pydle.featurize(pydle.features.RFC1459Support, pydle.features.TLSSupport)


def notify_if_ready():
    global expected_channels
    global expected_users
    if len(expected_channels) == 0 and len(expected_users) == 0:
        ready_event.set()


def announce(release):
    global client
    global event_loop
    asyncio.run_coroutine_threadsafe(
        client.send_message(release.channel, release.messages.pop(0)), event_loop
    )
    release.announce_time = datetime.now()
    time.sleep(2)


class IRC(BotBase):
    # RECONNECT_MAX_ATTEMPTS = None

    def __init__(self, nickname, channel, event_loop):
        super().__init__(nickname, eventloop=event_loop)
        self.nickname = nickname
        self.channel = channel

    async def send_message(self, channel, message):
        await self.message(channel, message)

    async def connect(self, *args, **kwargs):
        try:
            await super().connect(*args, **kwargs)
        except socket.error:
            await self.on_disconnect(expected=False)

    async def on_connect(self):
        print("Connected to IRC")
        await super().on_connect()
        await self.join(self.channel)

    async def on_join(self, channel, user):
        await super().on_join(channel, user)
        if user == config.irc_nickname:
            if channel in expected_channels:
                expected_channels.remove(channel)
        else:
            if user in expected_users:
                expected_users.remove(user)
        notify_if_ready()

    async def on_message(self, target, source, message):
        print("Got message: " + message)

    async def on_raw_353(self, message):
        await super().on_raw_353(message)
        _, _, _, names = message.params
        for user in names.split(" "):
            if user in expected_users:
                expected_users.remove(user)
        notify_if_ready()

    # async def on_raw(self, message):
    #    print(message)
    #    await super().on_raw(message)


def get_irc_task(nickname, channel, server, port, event_loop):
    global client

    client = IRC(nickname, channel, event_loop)
    return client.connect(hostname=server, port=port)


def run():
    global event_loop
    global expected_channels
    global expected_users

    expected_channels = config.irc_channels.split(",")
    expected_users = config.irc_users

    event_loop = asyncio.new_event_loop()
    irc_task = get_irc_task(
        config.irc_nickname,
        config.irc_channels,
        config.irc_server,
        config.irc_port,
        event_loop,
    )

    event_loop.create_task(irc_task)
    event_loop.run_forever()


def stop():
    global client
    global event_loop
    print("Stopping IRC client")

    asyncio.run_coroutine_threadsafe(client.disconnect(expected=True), event_loop)

    while len(asyncio.all_tasks(event_loop)) != 0:
        time.sleep(1)
    event_loop.call_soon_threadsafe(event_loop.stop)

    while event_loop.is_running():
        time.sleep(1)
    event_loop.close()
