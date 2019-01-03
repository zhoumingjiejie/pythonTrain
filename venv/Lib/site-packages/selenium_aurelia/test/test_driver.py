import pytest

from selenium_aurelia import AureliaDriver
from unittest.mock import MagicMock


class DriverStub:
    current_url = 'http://localhost'


@pytest.fixture
def aurelia_driver():
    return AureliaDriver(MagicMock())


def test_load_url(mock, aurelia_driver):
    url = 'http://localhost/'
    sleep = MagicMock()
    mock.patch('selenium_aurelia.time.sleep', sleep)

    aurelia_driver.load_url(url)

    aurelia_driver.selenium.get.assert_called_once_with(url)
    aurelia_driver.selenium.execute_async_script.assert_called_once_with(
        aurelia_driver.AURELIA_STARTED_SCRIPT
    )
    sleep.assert_called_once_with(aurelia_driver.default_wait_time)


def test_load_url_with_started_condition(mock, aurelia_driver):
    url = 'http://localhost/'
    sleep = MagicMock()
    mock.patch('selenium_aurelia.time.sleep', sleep)
    aurelia_driver.started_condition = '''
document.querySelector("[aurelia-app]").children[0].getAttribute('class') === 'splash'
    '''
    expected_line_script = '''
if (document.querySelector("[aurelia-app]").children[0].getAttribute('class') === 'splash') { cb("Aurelia composed") }
    '''  # noqa

    aurelia_driver.load_url(url)

    aurelia_driver.selenium.get.assert_called_once_with(url)
    assert aurelia_driver.selenium.execute_async_script.called
    script = aurelia_driver.selenium.execute_async_script.call_args[0][0].strip()
    script_lines = script.split('\n')
    assert len(script_lines) == 7
    assert script_lines[-1] == expected_line_script.strip()
    sleep.assert_called_once_with(aurelia_driver.default_wait_time)


def test_default_wait(mock, aurelia_driver):
    sleep = MagicMock()
    mock.patch('selenium_aurelia.time.sleep', sleep)

    aurelia_driver.wait()

    sleep.assert_called_once_with(aurelia_driver.default_wait_time)


def test_wait(mock, aurelia_driver):
    sleep = MagicMock()
    mock.patch('selenium_aurelia.time.sleep', sleep)

    aurelia_driver.wait(42)

    sleep.assert_called_once_with(42)


def test_navigate(aurelia_driver):
    aurelia_driver.wait = MagicMock()

    aurelia_driver.selenium.current_url = 'http://localhost/url1'
    with aurelia_driver.navigate():
        pass

    aurelia_driver.selenium.execute_async_script.assert_called_once_with(
        aurelia_driver.AURELIA_NAVIGATE_COMPLETE
    )
    assert not aurelia_driver.wait.called


def test_navigate_with_wait_time(aurelia_driver):
    aurelia_driver.wait = MagicMock()

    aurelia_driver.selenium.current_url = 'http://localhost/url1'
    with aurelia_driver.navigate(wait=10):
        pass

    aurelia_driver.selenium.execute_async_script.assert_called_once_with(
        aurelia_driver.AURELIA_NAVIGATE_COMPLETE
    )
    aurelia_driver.wait.assert_called_once_with(10)


def test_navigate_with_wait_on_navigation(aurelia_driver):
    aurelia_driver.wait = MagicMock()
    aurelia_driver.wait_on_navigation = True

    aurelia_driver.selenium.current_url = 'http://localhost/url1'
    with aurelia_driver.navigate():
        pass

    aurelia_driver.selenium.execute_async_script.assert_called_once_with(
        aurelia_driver.AURELIA_NAVIGATE_COMPLETE
    )
    aurelia_driver.wait.assert_called_once_with(2)


def test_navigate_immediate_load(aurelia_driver):
    aurelia_driver.selenium.current_url = 'http://localhost/url1'
    with aurelia_driver.navigate():
        aurelia_driver.selenium.current_url = 'http://localhost/url2'

    assert not aurelia_driver.selenium.execute_async_script.called


def test_get_selenium_driver_attribute(aurelia_driver):
    aurelia_driver.selenium = DriverStub()

    url = aurelia_driver.current_url

    assert url == 'http://localhost'


def test_get_inexistant_attribute(aurelia_driver):
    aurelia_driver.selenium = DriverStub()

    with pytest.raises(AttributeError) as e:
        aurelia_driver.yolo

    assert "Neither 'AureliaDriver' nor 'WebDriver' has a 'yolo' attribute" in str(e)


def test_find_element_by_binding(aurelia_driver):
    aurelia_driver.find_element_by_binding('src', 'heroSrc')
    aurelia_driver.selenium.find_element_by_css_selector.assert_called_once_with(
        '[src\\.bind="heroSrc"]'
    )


def test_find_element_by_binding_with_bind_type(aurelia_driver):
    aurelia_driver.find_element_by_binding('src', 'heroSrc', bind_type='one-way')
    aurelia_driver.selenium.find_element_by_css_selector.assert_called_once_with(
        '[src\\.one-way="heroSrc"]'
    )


def test_find_elements_by_binding(aurelia_driver):
    aurelia_driver.find_elements_by_binding('src', 'heroSrc')
    aurelia_driver.selenium.find_elements_by_css_selector.assert_called_once_with(
        '[src\\.bind="heroSrc"]'
    )


def test_find_elements_by_binding_with_bind_type(aurelia_driver):
    aurelia_driver.find_elements_by_binding('src', 'heroSrc', bind_type='one-way')
    aurelia_driver.selenium.find_elements_by_css_selector.assert_called_once_with(
        '[src\\.one-way="heroSrc"]'
    )
