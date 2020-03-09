import test_backends
from test_backends import sonarr_send, radarr_send, lidarr_send, clear_all_backends
import test_irc
import config

from asyncio import get_event_loop, gather, sleep
from pluginbase import PluginBase

async def test_runner():
    await test_irc.join_condition.wait()

    plugin_base = PluginBase(package='tests')
    source = plugin_base.make_plugin_source(
        searchpath=['./tests'],
        identifier='tests')

    for test_name in source.list_plugins():
        test = source.load_plugin(test_name)
        test_result = await test.run_test(test_irc.announce)
        if test_result:
            print("Test passed: " + test_name)

if __name__ == "__main__":
    #test_backends.run_backends()

    event_loop = get_event_loop()
    irc_task = test_irc.get_irc_task(
            config.irc_nickname,
            config.irc_channel,
            config.irc_server,
            config.irc_port,
            event_loop)

    atasks = gather(irc_task,
            test_runner(),
            loop=event_loop)

    event_loop.run_until_complete(atasks)
    event_loop.run_forever()
