from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import time

from . import config as global_config

browser = None


def renotify(test_suite, config, table_row, backend, success):
    _get_main(config)
    action_div = browser.find_element_by_xpath(
        "//*[@id='announced_torrents']/table/tbody/tr[{}]/td[5]/div".format(table_row)
    )
    dropdown = action_div.find_element_by_xpath("a[@href='#']")
    dropdown.click()
    renotify_link = action_div.find_element_by_xpath(
        "ul/li/a[text()='{}']".format(backend)
    )
    renotify_link.click()

    time.sleep(0.5)
    _check_toastr(test_suite, backend, success)


def _check_toastr(test_suite, backend, success):
    if success:
        class_name = "toast-success"
        toastr_text = " approved the torrent this time!"
    else:
        class_name = "toast-error"
        toastr_text = " still declined this torrent..."

    toastr = browser.find_element_by_id("toast-container").find_element_by_class_name(
        class_name
    )

    test_suite.assertEqual(
        toastr.text, backend + toastr_text, "Toastr text not ok",
    )

    time.sleep(7)

    toasters = browser.find_elements_by_id("toast-container")
    test_suite.assertEqual(len(toasters), 0, "Toaster should be expired")


def check_announced(test_suite, config, release):
    check_announcements(test_suite, config, [release])
    if len(release.snatches) > 0:
        check_snatches(test_suite, [release])


def check_announcements(test_suite, config, releases):
    _get_main(config)
    table_rows = (
        browser.find_element_by_id("announced_torrents")
        .find_element_by_tag_name("tbody")
        .find_elements_by_tag_name("tr")
    )

    test_suite.assertTrue(
        len(table_rows) >= min(len(releases), global_config.webui_table_rows),
        "No announcement in web table found",
    )

    for (row, release) in zip(
        table_rows, list(reversed(releases))[: global_config.webui_table_rows]
    ):
        cells = row.find_elements_by_tag_name("td")
        test_suite.assertEqual(len(cells), 5)
        test_suite.assertEqual(cells[1].text, release.indexer)
        test_suite.assertEqual(cells[2].text, release.title)

        web_backends = cells[3].text.split("/")
        test_suite.assertEqual(
            len(web_backends), len(release.backends), "Backends length does not match"
        )
        for backend in web_backends:
            test_suite.assertTrue(backend in release.backends)

        torrent_url = cells[4].find_element_by_id("torrent_url").get_attribute("href")
        test_suite.assertEqual(
            torrent_url, release.url, "Browser torrent URL did not match"
        )


def check_snatches(test_suite, releases):
    table_rows = (
        browser.find_element_by_id("snatched_torrents")
        .find_element_by_tag_name("tbody")
        .find_elements_by_tag_name("tr")
    )

    rows_iter = iter(table_rows)
    for release in list(reversed(releases))[: global_config.webui_table_rows]:
        if len(release.snatches) == 0:
            continue

        row = next(rows_iter)
        cells = row.find_elements_by_tag_name("td")
        test_suite.assertEqual(len(cells), 4)
        test_suite.assertEqual(cells[1].text, release.indexer)
        test_suite.assertEqual(cells[2].text, release.title)
        test_suite.assertEqual(cells[3].text, release.snatches[-1])


def _get_main(config):
    global browser
    browser.get("http://localhost:" + str(config.web_port))


def init(config):
    global browser
    opts = Options()
    opts.headless = True

    browser = Firefox(options=opts)
    _get_main(config)

    if config.web_username is not None:
        browser.find_element_by_name("username").send_keys(config.web_username)
        browser.find_element_by_name("password").send_keys(
            config.web_password + Keys.ENTER
        )


def stop():
    global browser
    browser.close()
    browser = None
