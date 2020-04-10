import asyncio
import unittest

async def run_test(test_helper):
    print("Running single test")
    #test_helper.sonarr_send_approved(True)

    await test_helper.announce("this is a name  -  /cow/ ¤/(- #angry#  -  pasta and sauce")

    await asyncio.sleep(2)

    sr = test_helper.sonarr_received()
    if sr == None:
        print("SR was None")
    else:
        print("SR: " + str(sr))

    sr = test_helper.radarr_received()
    if sr == None:
        print("SR was None")
    else:
        print("SR: " + str(sr))

    sr = test_helper.lidarr_received()
    if sr == None:
        print("SR was None")
    else:
        print("SR: " + str(sr))
    return True
