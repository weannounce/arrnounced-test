from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys

# from time import sleep

browser = None


def check_announced(test_suite, title, indexer, backends):
    browser.get("http://localhost:3467")
    for r in (
        browser.find_element_by_id("announced_torrents")
        .find_element_by_tag_name("tbody")
        .find_elements_by_tag_name("tr")
    ):
        cells = r.find_elements_by_tag_name("td")
        test_suite.assertEqual(len(cells), 5)
        test_suite.assertEqual(cells[1].text, indexer)
        test_suite.assertEqual(cells[2].text, title)

        web_backends = cells[3].text.split("/")
        test_suite.assertEqual(
            len(web_backends), len(backends), "Backends length does not match"
        )
        for backend in web_backends:
            test_suite.assertTrue(backend in backends)


def init():
    global browser
    opts = Options()
    opts.headless = True

    browser = Firefox(options=opts)
    browser.get("http://localhost:3467")
    browser.find_element_by_name("username").send_keys("admin")
    browser.find_element_by_name("password").send_keys("password" + Keys.ENTER)
    # browser.save_screenshot("login1.png")


def stop():
    global browser
    browser.close()
    browser = None
