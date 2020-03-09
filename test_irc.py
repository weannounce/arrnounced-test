import logging
import pydle
import socket
import threading
import asyncio

client = None
join_condition = asyncio.Event()
msg_condition = threading.Condition()
BotBase = pydle.featurize(pydle.features.RFC1459Support, pydle.features.TLSSupport)

async def announce(message):
    global client
    await client.send_message(message)

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

    #event_loop = get_event_loop()
    client = IRC(nickname, channel, event_loop)
    return client.connect(server, port)
    #atasks = gather(client.connect(server, port),
    #        m_loop(),
    #        loop=event_loop)

    #event_loop.run_until_complete(atasks)
    #event_loop.run_forever()

    #irc_thread = threading.Thread(target=event_loop.run_forever)
    #irc_thread.start()

    #client.run(server, port)
    #irc_thread = threading.Thread(target=client.run, args=(server, port))
    #irc_thread.start()
