''' This module is responsible for loading the driver config and directing the instructions to a relevant driver. The idea is for tests to
    interact with this module directly instead of a specific driver, this gives us the option to use other drivers and not just selenium, or
    if we change from selenium to another driver, our tests will not need to change, since we reference this interface and not selenium directly.'''

import time
import os
from os.path                                    import realpath, dirname

from selenium                                   import webdriver, __version__
from selenium.webdriver.common.action_chains    import ActionChains
from selenium.webdriver.common.keys             import Keys
from selenium.webdriver.support                 import expected_conditions as EC
from selenium.webdriver.support.ui              import WebDriverWait

from webdriver_manager.chrome                   import ChromeDriverManager
from webdriver_manager.utils                    import ChromeType
from webdriver_manager.firefox                  import GeckoDriverManager
from webdriver_manager.microsoft                import IEDriverManager
from webdriver_manager.microsoft                import EdgeChromiumDriverManager
from webdriver_manager.opera                    import OperaDriverManager

from utilities.json_helper                      import LoadJson, GetJsonValue
from core.core_details                          import TestDefinition


CURRENT_DIR = dirname(realpath(__file__))


class LocateBy:
    ''' A class allowing easier reference to a locate by method when selecting ways to interact with an element '''
    ID = 'id'
    CLASSNAME = 'class name'
    XPATH = 'xpath'
    CSS_SELECTOR = 'css selector'
    TAG_NAME = 'tag name'
    LINK_TEXT = 'link text'


class Browsers:
    ''' A holding class for browser names to ensure values are consistent throughout the framework. '''
    CHROME = 'chrome'
    CHROMIUM = 'chromium'
    FIREFOX = 'firefox'
    IE = 'ie'
    EDGE = 'edge'
    OPERA = 'opera'


class Hooks:
    ''' This class is used to control, read and provide access to the hooks provided in a json file. The json file must follow a particular
        structure for it to be compatible with this hook class. You can see an example json file already in the directory /driver/hooks '''
    def __init__(self, hook_file_name):
        self.hook_file = f'{CURRENT_DIR}\\hooks\\{hook_file_name}.json'
        self.hooks = LoadJson.using_filepath(self.hook_file)

    def get_hook(self, hook_name):
        ''' Pass in the name of the hook. This method returns 2 values, the 1st is the hook type (xpath, id, classname) and the
            2nd is the actual hook locator/value '''
        hook = self.hooks.get(hook_name)
        hook_type = hook.get('type')
        hook_value = hook.get('value')
        return hook_type, hook_value

    def get_hook_type(self, hook_name):
        ''' Pass in the hooks name and get returned the type of hook it is. '''
        return self.get_hook(hook_name)[0]

    def get_hook_value(self, hook_name):
        ''' Pass in the hooks name and get returned the type of hook it is. '''
        return self.get_hook(hook_name)[1]


class DriverHelper:
    ''' This class holds all methods related to assisting the driver actions class by keeping any setup and config related work out of the
        actions class. '''
    def __init__(self):
        self.driver_config = LoadJson.using_filepath(CURRENT_DIR + '\\driver_config.json')

        self.driver_name = GetJsonValue.by_key(self.driver_config, 'driverName')
        self.capability_dir = GetJsonValue.by_key(self.driver_config, 'capabilityDir')
        self.max_window_default = GetJsonValue.by_key(self.driver_config, 'maxWindowDefault')


    def load_capability(self, platform, capability):
        ''' Pass in the platform and the capability name. This method returns a dictionary object of the capability. It will first determine
            what driver to use, for example selenium, then it will load the capability according to that driver. '''
        if not os.path.exists(f'{CURRENT_DIR}\\{self.capability_dir}\\{platform}\\{capability}.json'):
            raise Exception('Capability Not Found!')

        else:
            cap_file = LoadJson.using_filepath(f'{CURRENT_DIR}\\{self.capability_dir}\\{platform}\\{capability}.json')
            caps = {
                'seleniumVersion': __version__,
                'deviceName': cap_file['deviceName'],
                'browserName': cap_file['browserName'],
                'platformVersion': cap_file['platformVersion'],
                'platformName': cap_file['platformName'],
                'rotatable': cap_file['rotatable'],
                'deviceOrientation': cap_file['deviceOrientation'],
                'privateDevicesOnly': False,
                'phoneOnly': False,
                'tabletOnly': False
            }
            return caps


    def load_driver(self, capabilities):
        ''' This method will load and return the driver. It depends on the capability of the test, for example it references the browser name
            in the capability file. '''
        if capabilities['browserName'] == Browsers.CHROME:
            driver = webdriver.Chrome(ChromeDriverManager().install())
        elif capabilities['browserName'] == Browsers.CHROMIUM:
            driver = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        elif capabilities['browserName'] == Browsers.FIREFOX:
            driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        elif capabilities['browserName'] == Browsers.IE:
            driver = webdriver.Ie(IEDriverManager().install())
        elif capabilities['browserName'] == Browsers.EDGE:
            driver = webdriver.Edge(EdgeChromiumDriverManager().install())
        elif capabilities['browserName'] == Browsers.OPERA:
            # If opera is not installed in its default directory, this may throw an exception, workaround is on the pip site.
            driver = webdriver.Opera(executable_path=OperaDriverManager().install())
        else:
            raise Exception('Unable to identify browser to load driver, check your capability file contains the correct value for browser name.')

        # If we set the max window to default we will automatically set the browser window to maximise on driver load
        if self.max_window_default is True:
            driver.maximize_window()

        return driver


class DriverActions:
    ''' This class is the main one used in tests which does the actual interaction with the driver and product under test. '''
    def __init__(self, test_definition: TestDefinition, hook_file_name=False):
        self.driver_setup = DriverHelper()
        self.test_def = test_definition
        self.caps = self.driver_setup.load_capability(test_definition.platform, test_definition.capability)
        self.driver = self.driver_setup.load_driver(self.caps)
        self.action = ActionChains(self.driver)
        self.wait = WebDriverWait(self.driver, 60)
        if hook_file_name is not False:
            self.hooks = Hooks(hook_file_name)
        else:
            self.hooks = False


    def _check_locate_by(self, hook, locate_by, new_token_value):
        '''
            This method is only used internally by the driver class. Pass in the hook name and the locate by method. It returns 2 values, the
            locator and the hook value. The 3 parameter is the new token value which will replace a token placeholder in a hook value, currently
            the token to use in a hook file is $$token$$. This token is replaced with the value of new token value that you pass in.
        '''
        # In this method, the hook parameter is the hook_name.
        if self.hooks is not False:
            if locate_by is False: # If locate_by is False that means you passed in the hook name, and its up to me to get the hook type and value
                if new_token_value is not False: # If a token value is passed in, we must first update the token value in hooks
                    locate_by, hook_value = self.hooks.get_hook(hook)
                    hook_value = hook_value.replace('$$token$$', new_token_value)
                    return locate_by, hook_value

                locate_by, hook_value = self.hooks.get_hook(hook)
                return locate_by, hook_value

        return locate_by, hook


    def launch_url(self, url):
        ''' Go to the specified url with the current driver instance. '''
        self.driver.get(url)


    def quit_the_driver(self):
        ''' Closes the driver. '''
        self.driver.quit()


    def set_browser_window_size(self, window_w, window_h):
        ''' Changes the browser window size. '''
        self.driver.set_window_size(window_w, window_h)


    def browser_back(self):
        ''' Selects the browser back button. '''
        self.driver.back()


    def execute_js_script(self, script, timeout=30):
        ''' Executes a javascript script on the open webpage, remember to add "return" to your js if you expect a return value. '''
        self.driver.set_script_timeout(timeout)
        return self.driver.execute_script(script)


    def get_current_url_in_browser(self):
        ''' Retrieves the current url in the browser and returns it as a string. '''
        return str(self.execute_js_script("return window.location.href"))


    def refresh_browser(self):
        ''' Refreshes the browser page. Like pressing F5. '''
        self.driver.refresh()


    def wait_for_element_visible(self, hook_value, locate_by=False, hook_token=False):
        ''' Pass in the locate by type, like the xpath or id, and pass in the element locator, which will be the actual id or xpath '''
        locate_by, hook_value = self._check_locate_by(hook_value, locate_by, hook_token)
        self.wait.until(EC.visibility_of_element_located((locate_by, hook_value)))
        time.sleep(0.5) # Selenium does not play well with SPA's, sometimes executes too fast and interferes with UI component rendering.


    def wait_until_element_invisible(self, hook_value, locate_by=False, hook_token=False):
        ''' Wait for an element to become invisible. '''
        locate_by, hook_value = self._check_locate_by(hook_value, locate_by, hook_token)
        self.wait.until(EC.invisibility_of_element((locate_by, hook_value)))
        time.sleep(0.5) # Selenium does not play well with SPA's, sometimes executes too fast and interferes with UI component rendering.


    def wait_until_element_clickable(self, hook_value, locate_by=False, hook_token=False):
        ''' Wait until an element is enalbed or 'clickable' '''
        locate_by, hook_value = self._check_locate_by(hook_value, locate_by, hook_token)
        self.wait.until(EC.element_to_be_clickable((locate_by, hook_value)))


    def fill_in_field(self, input_text, hook_value, locate_by=False, hook_token=False):
        '''
            Fill in the field on the webform given the locator passed in. Pass in what to locate the element by, the actual element
            locator (id or xpath etc) and then the text you wish to input into the field
        '''
        locate_by, hook_value = self._check_locate_by(hook_value, locate_by, hook_token)
        self.driver.find_element(locate_by, hook_value).send_keys(input_text)
        time.sleep(0.5) # Selenium does not play well with SPA's, sometimes executes too fast and interferes with UI component rendering.


    def clear_input(self, hook_value, locate_by=False, hook_token=False):
        '''
            Clear the value in an input element. Pass in what to locate the element by, the actual element locator (id or xpath etc).
            If you have a token in the hook file then pass in the value you want the token replaced with using the hook_token parameter.
        '''
        locate_by, hook_value = self._check_locate_by(hook_value, locate_by, hook_token)
        self.driver.find_element(locate_by, hook_value).clear()
        # TO DO: In some cases selenium does not work, need to execute js directly which works 99% of the time. Code left below to remind me:
        # document.getElementById('elementId').value = null
        time.sleep(0.5) # Selenium does not play well with SPA's, sometimes executes too fast and interferes with UI component rendering.


    def get_element_dynamic_id_by_text(self, partial_id, text_to_find):
        '''
            Returns the id number or incrementing part of the element id. That is when you pass in a partial_id,
            this method will strip off the partial id from the id it finds. This method returns a tuple, the first value
            is the entire id and the 2nd value is just the id without the partial part passed in.
        '''
        element = self.driver.find_element_by_xpath(f"//*[contains(@id, '{partial_id}') and contains(text(), '{text_to_find}')]")
        if isinstance(element, list) or isinstance(element, tuple):
            return str(element[0].get_attribute('id')).replace(partial_id, '')
        else:
            return str(element.get_attribute('id')).replace(partial_id, '')


    def select_element(self, hook_value, locate_by=False, hook_token=False):
        '''
            Simulate a user select on the given locator. Pass in what to locate the element by, the actual element locator (id or xpath etc).
            If you have a token in the hook file then pass in the value you want the token replaced with using the hook_token parameter.
        '''
        locate_by, hook_value = self._check_locate_by(hook_value, locate_by, hook_token)
        self.driver.find_element(locate_by, hook_value).click()
        time.sleep(0.5) # Selenium does not play well with SPA's, sometimes executes too fast and interferes with UI component rendering.


    def hover_over_element(self, hook_value, locate_by=False, hook_token=False):
        ''' Goes to an element and hover over it. '''
        locate_by, hook_value = self._check_locate_by(hook_value, locate_by, hook_token)
        element = self.driver.find_element(locate_by, hook_value)
        self.action.move_to_element(element).perform()


    def take_screenshot(self, directory=None, file_name=None):
        ''' Takes a screenshot and stores it under the specified directory. Passing in a file name is optional. '''
        if file_name is None:
            file_name = self.test_def.test_name

        if directory is None:
            directory = f'{self.test_def.screenshot_dir}'
            if not os.path.exists(directory):
                os.makedirs(directory)
        num_of_screenshots = len([name for name in os.listdir(directory)])
        self.driver.save_screenshot(f'{directory}{file_name}-{num_of_screenshots}.png')


    def press_enter(self):
        ''' Simulates pressing enter on the keyboard. '''
        self.action.send_keys(Keys.ENTER).perform()


    def get_element_text(self, hook_value, locate_by=False, hook_token=False):
        ''' Retrieves the element text. '''
        locate_by, hook_value = self._check_locate_by(hook_value, locate_by, hook_token)
        return self.driver.find_element(locate_by, hook_value).text


    def switch_to_tab(self, tab_num=1):
        ''' This method switches the driver control to a new tab. '''
        self.driver.switch_to_window(self.driver.window_handles[tab_num])


    def switch_to_main_tab(self):
        ''' Returns driver control to the main tab, usually with index 0. '''
        self.driver.switch_to_window(self.driver.window_handles[0])


    def close_current_tab(self):
        ''' Will close the current tab under driver control. '''
        self.driver.close()
