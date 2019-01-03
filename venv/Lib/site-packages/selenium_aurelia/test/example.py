from selenium import webdriver
from selenium_aurelia import AureliaDriver


def run_example(url, selenium_driver):
    # We create the AureliaDriver from the selenium driver.
    # We specify a complementary started condition: it is possible that your app will be loaded
    # before the AureliaDriver has the time to register the proper callback in the browser.
    # In this case, load_url will fail because of a TimeOut. To prevent this, you can specify
    # a custom condition you know is fulfilled when Aurelia is started on your application.
    # Here, we check for the spinner: if it is here, the app is loading. If it is not, the app is
    # loaded. This help reduce failures for wrong reasons.
    started_condition = '''
document.querySelector("[aurelia-app]").children[0].getAttribute('class') === 'splash'
    '''
    driver = AureliaDriver(selenium_driver, started_condition=started_condition)

    # The load url method will open the requested url in the browser and wait for Aurelia to start
    driver.load_url(url)
    # You can wait for the default time.
    driver.wait()

    # You can access selenium attribute directly with the selenium property
    assert driver.selenium.current_url == url

    # But you can also access them directly on the driver
    create_form = driver.find_element_by_id('select-heroes-form')
    name_input = create_form.find_element_by_css_selector('input')
    name_input.send_keys('Player 1')
    submit_btn = create_form.find_element_by_css_selector('button')

    # If an action will cause a navigation, call inside the navigate context manager. It will
    # ensure that the navigation is done before continuing
    with driver.navigate():
        submit_btn.click()

    # You can wait with the wait method.
    driver.wait(3)

    # You can easily get element(s) by their binding, eg src.bind="heroSrc"
    driver.find_element_by_binding('src', 'heroSrc')
    assert len(driver.find_elements_by_binding('src', 'heroSrc')) >= 1

    driver.quit()


if __name__ == '__main__':
    # Go here: http://selenium-python.readthedocs.io/api.html for the list of drivers
    run_example('https://www.arenaoftitans.com/game/create', webdriver.Firefox())
