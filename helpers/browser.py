from . import config
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys

browser = None


def renotify(test_suite, table_row, backend):
    _get_main()
    action_div = browser.find_element_by_xpath(
        "//*[@id='announced_torrents']/table/tbody/tr[{}]/td[5]/div".format(table_row)
    )
    dropdown = action_div.find_element_by_xpath("a")
    dropdown.click()
    renotify_link = action_div.find_element_by_xpath(
        "ul/li/a[text()='{}']".format(backend)
    )
    renotify_link.click()


def check_announced(test_suite, title, indexer, backends, snatched_backends=[]):
    _get_main()
    table_rows = (
        browser.find_element_by_id("announced_torrents")
        .find_element_by_tag_name("tbody")
        .find_elements_by_tag_name("tr")
    )

    test_suite.assertTrue(len(table_rows) > 0, "No announcement in web table found")
    row = table_rows[0]

    cells = row.find_elements_by_tag_name("td")
    test_suite.assertEqual(len(cells), 5)
    test_suite.assertEqual(cells[1].text, indexer)
    test_suite.assertEqual(cells[2].text, title)

    web_backends = cells[3].text.split("/")
    test_suite.assertEqual(
        len(web_backends), len(backends), "Backends length does not match"
    )
    for backend in web_backends:
        test_suite.assertTrue(backend in backends)

    if len(snatched_backends) > 0:
        _check_snatch(test_suite, title, indexer, snatched_backends[0])


def _check_snatch(test_suite, title, indexer, snatched_backend):
    table_rows = (
        browser.find_element_by_id("snatched_torrents")
        .find_element_by_tag_name("tbody")
        .find_elements_by_tag_name("tr")
    )

    test_suite.assertTrue(len(table_rows) > 0, "No announcement in web table found")
    row = table_rows[0]

    cells = row.find_elements_by_tag_name("td")
    test_suite.assertEqual(len(cells), 4)
    test_suite.assertEqual(cells[1].text, indexer)
    test_suite.assertEqual(cells[2].text, title)
    test_suite.assertEqual(cells[3].text, snatched_backend)


def _get_main():
    global browser
    browser.get("http://localhost:" + str(config.arrnounced_port))


def init():
    global browser
    opts = Options()
    opts.headless = True

    browser = Firefox(options=opts)
    _get_main()
    browser.find_element_by_name("username").send_keys(config.web_username)
    browser.find_element_by_name("password").send_keys(config.web_password + Keys.ENTER)
    # browser.save_screenshot("login1.png")


def stop():
    global browser
    browser.close()
    browser = None
