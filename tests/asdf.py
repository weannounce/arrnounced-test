import asyncio

async def run_test(test_helper):
    print("unning test")
    test_helper.sonarr_send({"name": "𝚍𝚎𝚕𝚙𝚑𝚒𝚗𝚞𝚜", "approved": True})
    test_helper.sonarr_send_approved(True)

    await test_helper.announce("[cate] Title title title  - http://asdf/qwer?id=396589 - stuff")

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
