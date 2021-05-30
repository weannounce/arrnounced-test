from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import time

browser = None


def renotify(test_suite, config, table_row, backend, success):
    _get_main(config)
    action_div = browser.find_element_by_xpath(
        f"//*[@id='announced_torrents']/table/tbody/tr[{table_row}]/td[5]/div"
    )
    dropdown = action_div.find_element_by_xpath("a[@href='#']")
    dropdown.click()
    renotify_link = action_div.find_element_by_xpath(f"ul/li/a[text()='{backend}']")
    renotify_link.click()

    _check_toastr(test_suite, backend, success)


def _check_toastr(test_suite, backend, success):
    if success:
        class_name = "toast-success"
        toastr_text = " approved the torrent this time!"
    else:
        class_name = "toast-error"
        toastr_text = " still declined this torrent..."

    toastr = None
    for i in range(4):
        time.sleep(0.5)
        try:
            toastr = browser.find_element_by_id(
                "toast-container"
            ).find_element_by_class_name(class_name)
            break
        except NoSuchElementException:
            pass

    test_suite.assertNotEqual(toastr, None)
    test_suite.assertEqual(
        toastr.text,
        backend + toastr_text,
        "Toastr text not ok",
    )

    time.sleep(7)

    toasters = browser.find_elements_by_id("toast-container")
    test_suite.assertEqual(len(toasters), 0, "Toaster should be expired")


def check_announced(test_suite, config, release):
    check_announcements(test_suite, config, [release])
    if len(release.snatches) > 0:
        check_snatches(test_suite, [release])


def _get_announce_row(rows):
    return _get_next_row(rows, "announced-pagination", "announced_torrents")


def _get_snatch_row(rows):
    return _get_next_row(rows, "snatched-pagination", "snatched_torrents")


def _get_next_row(rows, pager_id, table_id):
    if rows is None:
        rows = []
    elif len(rows) == 0:
        try:
            browser.find_element_by_xpath(
                f"//*[@id='{pager_id}']/li[@class='page-item next']/a[text()='Next']"
            ).click()
        except NoSuchElementException:
            return None, []

    if len(rows) == 0:
        rows = (
            browser.find_element_by_id(table_id)
            .find_element_by_tag_name("tbody")
            .find_elements_by_tag_name("tr")
        )

    row = rows.pop(0) if rows else None

    return (row, rows)


def _check_announcement_cells(test_suite, cells, release):
    test_suite.assertEqual(len(cells), 5)
    test_suite.assertEqual(cells[2].text, release.title)
    test_suite.assertEqual(cells[1].text, release.indexer)

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


def check_unordered_announcements(test_suite, config, releases):
    # This function does not handle releases with the same title
    row_count = 0
    release_count = len(releases)

    releases_copy = releases.copy()
    releases_copy.reverse()

    _get_main(config)
    rows = None
    row, rows = _get_announce_row(rows)

    while row:
        cells = row.find_elements_by_tag_name("td")
        release = next(filter(lambda x: x.title == cells[2].text, releases_copy), None)
        test_suite.assertNotEqual(
            release, None, f"Row title '{cells[2].text}' was not found among releases"
        )
        releases_copy.remove(release)
        _check_announcement_cells(test_suite, cells, release)

        row_count += 1
        row, rows = _get_announce_row(rows)

    test_suite.assertEqual(
        row_count, release_count, "Found table rows is not equal to releases"
    )


def check_announcements(test_suite, config, releases):
    _get_main(config)

    rows = None
    for release in reversed(releases):
        (row, rows) = _get_announce_row(rows)
        test_suite.assertNotEqual(row, None, "Not enough releases in table")
        cells = row.find_elements_by_tag_name("td")
        _check_announcement_cells(test_suite, cells, release)


def _check_snatch_cells(test_suite, cells, release):
    test_suite.assertEqual(len(cells), 4)
    test_suite.assertEqual(cells[2].text, release.title)
    test_suite.assertEqual(cells[1].text, release.indexer)
    test_suite.assertEqual(cells[3].text, release.snatches[-1])


def check_unordered_snatches(test_suite, releases):
    # This function does not handle releases snatched several times
    row_count = 0
    release_count = len(releases)

    releases_copy = releases.copy()
    releases_copy.reverse()

    rows = None
    row, rows = _get_snatch_row(rows)

    while row:
        cells = row.find_elements_by_tag_name("td")
        release = next(filter(lambda x: x.title == cells[2].text, releases_copy), None)
        test_suite.assertNotEqual(
            release, None, f"Row title '{cells[2].text}' was not found among releases"
        )
        releases_copy.remove(release)

        _check_snatch_cells(test_suite, cells, release)

        row_count += 1
        row, rows = _get_snatch_row(rows)

    test_suite.assertEqual(
        row_count, release_count, "Found table rows is not equal to releases"
    )


def check_snatches(test_suite, releases):
    rows = None
    for release in reversed(releases):
        if len(release.snatches) == 0:
            continue
        row, rows = _get_snatch_row(rows)
        test_suite.assertNotEqual(row, None)

        cells = row.find_elements_by_tag_name("td")
        _check_snatch_cells(test_suite, cells, release)


def _get_main(config):
    global browser
    browser.get("http://localhost:" + str(config.web_port))

    # Wait for tables to fill
    time.sleep(0.5)


def get_status(config):
    global browser
    browser.get("http://localhost:" + str(config.web_port) + "/status")


def print_tracker_status(test_suite, tracker_status):
    global browser
    cells = browser.find_element_by_id(
        "indexer_" + tracker_status.type
    ).find_elements_by_tag_name("td")
    print("--- Status:")
    for i, c in enumerate(cells):
        print(i, ": ", c.text)
    # test_suite.assertEqual(len(cells), 5)
    # test_suite.assertEqual(cells[0].text, tracker_status.name)
    # test_suite.assertEqual(cells[1].text, "Yes" if tracker_status.connected else "No")


def check_tracker_status(test_suite, tracker_status):
    global browser
    cells = browser.find_element_by_id(
        "indexer_" + tracker_status.type
    ).find_elements_by_tag_name("td")
    test_suite.assertEqual(len(cells), 5)
    print("CHECKING!!!")
    test_suite.assertEqual(cells[0].text, tracker_status.name)
    test_suite.assertEqual(cells[1].text, "Yes" if tracker_status.connected else "No")


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
    if browser is not None:
        browser.close()
        browser = None
