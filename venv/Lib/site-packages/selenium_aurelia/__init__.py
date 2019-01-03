import time

from contextlib import contextmanager


class AureliaDriver:
    # From https://github.com/aurelia/tools/blob/master/plugins/protractor.js#L22
    AURELIA_STARTED_SCRIPT = '''
var cb = arguments[arguments.length - 1];
if (window.webpackJsonp && document.querySelector("[aurelia-app]")) { cb("Aurelia composed") }
document.addEventListener("aurelia-composed", function (e) {
    cb("Aurelia App composed")
}, false);
    '''
    AURELIA_STARTED_CONDITION_TEMPLATE = '''
if ({condition}) {{ cb("Aurelia composed") }}
    '''
    # From https://github.com/aurelia/tools/blob/master/plugins/protractor.js#L34
    AURELIA_NAVIGATE_COMPLETE = '''
var cb = arguments[arguments.length - 1];
document.querySelector("[aurelia-app]")
    .aurelia.subscribeOnce("router:navigation:complete", function() {
        cb(true)
    });
    '''

    def __init__(
        self,
        selenium_webdriver,
        script_timeout=10,
        default_wait_time=2,
        wait_on_navigation=False,
        started_condition=None
    ):
        self.selenium = selenium_webdriver
        self.script_timeout = script_timeout
        self.started_condition = started_condition
        self.default_wait_time = default_wait_time
        self.wait_on_navigation = wait_on_navigation

    def load_url(self, url):
        self.selenium.get(url)
        self.selenium.set_script_timeout(self.script_timeout)
        script = self.AURELIA_STARTED_SCRIPT
        if self.started_condition:
            script += self.AURELIA_STARTED_CONDITION_TEMPLATE.format(
                condition=self.started_condition.strip()
            )
        self.selenium.execute_async_script(script)
        time.sleep(self.default_wait_time)

    def wait(self, seconds=0):
        if seconds <= 0:
            seconds = self.default_wait_time
        time.sleep(seconds)

    @contextmanager
    def navigate(self, wait=0):
        url_before_navigate = self.selenium.current_url
        yield
        if self.selenium.current_url == url_before_navigate:
            self.selenium.execute_async_script(self.AURELIA_NAVIGATE_COMPLETE)

        if self.wait_on_navigation or wait > 0:
            wait_time = wait if wait > 0 else self.default_wait_time
            self.wait(wait_time)

    def find_element_by_binding(self, attr, value, bind_type='bind'):
        selector = self._get_binding_selector(attr, value, bind_type)
        return self.selenium.find_element_by_css_selector(selector)

    def _get_binding_selector(self, attr, value, bind_type):
        return '[{attr}\\.{bind_type}="{value}"]'.format(
            attr=attr,
            value=value,
            bind_type=bind_type
        )

    def find_elements_by_binding(self, attr, value, bind_type='bind'):
        selector = self._get_binding_selector(attr, value, bind_type)
        return self.selenium.find_elements_by_css_selector(selector)

    def __getattr__(self, name):
        if hasattr(self.selenium, name):
            return getattr(self.selenium, name)
        else:
            msg = "Neither 'AureliaDriver' nor 'WebDriver' has a '{name}' attribute"
            msg = msg.format(name=name)
            raise AttributeError(msg)
