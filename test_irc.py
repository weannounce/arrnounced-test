import logging
import pydle
import socket
import threading
from asyncio import get_event_loop, gather, new_event_loop, sleep, Event

client = None
join_condition = threading.Condition()
msg_condition = threading.Condition()
BotBase = pydle.featurize(pydle.features.RFC1459Support, pydle.features.TLSSupport)
tx_msg = None

def announce(message):
    global tx_msg
    tx_msg = message
    msg_condition.notifyAll()
    #client.send_message(message)

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
        with join_condition:
            print("Joing channel " + channel)
            await super().on_join(channel, user)
            join_condition.notifyAll()

    async def on_message(self, target, source, message):
        print("Got message: " + message)

    #async def on_raw(self, message):
    #    print(message)
    #    await super().on_raw(message)

async def m_loop():
    global client
    print("m loop 1")
    while True:
        print("m loop 2")
        with msg_condition:
            print("m loop 3")
            #await msg_condition.wait()
            await sleep(50)
            print("m loop 4")
            await client.send_message(tx_msg)

def run_irc(nickname, channel, server, port):
    global client

    event_loop = new_event_loop()
    client = IRC(nickname, channel, event_loop)
    atasks = gather(client.connect(server, port),
            m_loop(),
            loop=event_loop)

    event_loop.run_until_complete(atasks)
    event_loop.run_forever()

    irc_thread = threading.Thread(target=event_loop.run_forever)
    irc_thread.start()

    #client.run(server, port)
    #irc_thread = threading.Thread(target=client.run, args=(server, port))
    #irc_thread.start()
