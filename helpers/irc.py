#from asyncio import get_event_loop, gather, sleep
from asyncio import new_event_loop, gather
import logging
import pydle
import socket
import asyncio
import time
from . import config


client = None
join_condition = asyncio.Event()
BotBase = pydle.featurize(pydle.features.RFC1459Support, pydle.features.TLSSupport)

event_loop = None

def run():
    global event_loop
    event_loop = new_event_loop()
    irc_task = get_irc_task(
            config.irc_nickname,
            config.irc_channel,
            config.irc_server,
            config.irc_port,
            event_loop)

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

def announce(message):
    global client
    global event_loop
    asyncio.run_coroutine_threadsafe(client.send_message(message), event_loop)
    time.sleep(2)


class IRC(BotBase):
    #RECONNECT_MAX_ATTEMPTS = None

    def __init__(self, nickname, channel, event_loop):
        super().__init__(nickname, eventloop=event_loop)
        self.nickname = nickname
        self.channel = channel

    async def send_message(self, message):
        print("sending message")
        await self.message(self.channel, message)

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
        #with join_condition:
        print("Joing channel " + channel)
        await super().on_join(channel, user)
        join_condition.set()

    async def on_message(self, target, source, message):
        print("Got message: " + message)

    #async def on_raw(self, message):
    #    print(message)
    #    await super().on_raw(message)

def get_irc_task(nickname, channel, server, port, event_loop):
    global client

    client = IRC(nickname, channel, event_loop)
    return client.connect(server, port)
