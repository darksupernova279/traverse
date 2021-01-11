''' This module is responsible for loading the driver config and directing the instructions to a relevant driver. The idea is for tests to
    interact with this module directly instead of a specific driver, this gives us the option to use other drivers and not just selenium, or
    if we change from selenium to another driver, our tests will not need to change, since we reference this interface and not selenium directly.'''

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

    def replace_hook_token(self, hook_name, new_token_value):
        ''' Replaces a token placeholder in the hook file. The value you pass in will repalce the token $$token$$. This is extremely
            useful when using advanced xpaths as ways to hook into elements. '''
        hook_value = self.hooks[hook_name]['value']
        hook_value = hook_value.replace('$$token$$', new_token_value)
        self.hooks[hook_name]['value'] = hook_value




class DriverHelper:
    ''' This class holds all methods related to assisting the driver actions class by keeping any setup and config related work out of the
        actions class. '''
    def __init__(self):
        self.driver_config = LoadJson.using_filepath(CURRENT_DIR + '\\driver_config.json')

        self.driver_name = GetJsonValue.by_key(self.driver_config, 'driverName')
        self.capability_dir = GetJsonValue.by_key(self.driver_config, 'capabilityDir')
        self.screenshot_dir = GetJsonValue.by_key(self.driver_config, 'screenshotDir')
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
    def __init__(self, platform, capability, hook_file_name=False):
        self.driver_setup = DriverHelper()
        self.caps = self.driver_setup.load_capability(platform, capability)
        self.driver = self.driver_setup.load_driver(self.caps)
        self.action = ActionChains(self.driver)
        self.wait = WebDriverWait(self.driver, 60)
        if hook_file_name is not False:
            self.hooks = Hooks(hook_file_name)
        else:
            self.hooks = False


    def _check_locate_by(self, hook_value, locate_by, new_token_value):
        ''' This method is only used internally by the driver class. Pass in the hook name and the locate by method. It returns 2 values, the
            locator and the hook value. The 3 parameter is the new token value which will replace a token placeholder in a hook value, currently
            the token to use in a hook file is $$token$$. This token is replaced with the value of new token value that you pass in.'''
        # In this method, the hook_value parameter is actually the hook_name.
        if self.hooks is not False:
            if locate_by is False: # If locate_by is False that means you passed in the hook name, and its up to me to get the hook type and value
                if new_token_value is not False: # If a token value is passed in, we must first update the token value in hooks
                    self.hooks.replace_hook_token(hook_value, new_token_value)

                locate_by, hook_value = self.hooks.get_hook(hook_value)

                return locate_by, hook_value

        return locate_by, hook_value


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


    def wait_until_element_invisible(self, hook_value, locate_by=False, hook_token=False):
        ''' Wait for an element to become invisible. '''
        locate_by, hook_value = self._check_locate_by(hook_value, locate_by, hook_token)
        self.wait.until(EC.invisibility_of_element((locate_by, hook_value)))


    def fill_in_field(self, input_text, hook_value, locate_by=False, hook_token=False):
        ''' Fill in the field on the webform given the locator passed in. Pass in what to locate the element by, the actual element
            locator (id or xpath etc) and then the text you wish to input into the field  '''
        locate_by, hook_value = self._check_locate_by(hook_value, locate_by, hook_token)
        self.driver.find_element(locate_by, hook_value).send_keys(input_text)


    def select_element(self, hook_value, locate_by=False, hook_token=False):
        ''' Simulate a user select on the given locator. Pass in what to locate the element by, the actual element locator (id or xpath etc)'''
        locate_by, hook_value = self._check_locate_by(hook_value, locate_by, hook_token)
        self.driver.find_element(locate_by, hook_value).click()


    def hover_over_element(self, hook_value, locate_by=False, hook_token=False):
        ''' Goes to an element and hover over it. '''
        locate_by, hook_value = self._check_locate_by(hook_value, locate_by, hook_token)
        element = self.driver.find_element(locate_by, hook_value)
        self.action.move_to_element(element).perform()


    def take_screenshot(self, directory=None, file_name='test'):
        ''' Takes a screenshot and stores it under the specified directory. Passing in a file name is optional. '''
        if directory is None:
            directory = self.driver_setup.screenshot_dir
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
        '''  '''
        self.driver.switch_to_window(self.driver.window_handles[tab_num])


    def switch_to_main_tab(self):
        '''  '''
        self.driver.switch_to_window(self.driver.window_handles[0])


    def close_current_tab(self):
        '''  '''
        self.driver.close()
