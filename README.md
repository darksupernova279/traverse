Traverse is an automation framework built from the ground up. Its focus is on scalability, adaptability and maintainability. This is a personal project of mine and I use it for multiple projects. If there are any suggestions or feature ideas I would be keen to hear about them. Note I am quite pedantic about traverse, so any contributions are indeed welcome but I want to ensure the overall project remains consistent, easy to use, maintainable and scalable. 

__________________________________________________________________________
######** Directory Structure **######

Root(traverse)
- Top level, where the main traverse.py file sits, and its config file. All execution begins with traverse.py

traverse/core
- Core test framework features stored here, such as the test executor, test reporter, and profiler as examples.
- There would be no need to pay this directory any attention unless you plan on changing core features.

traverse/driver
- This is mainly for selenium at the moment, however, it is possible to integrate with another driver, but this would require some planning.
- Inside you will find the driver_config_json file, which handles all configurations specific to the driver, p.s. if we had to integrate another driver, we could add a config here to select the different driver instead of selenium. 
- Capabilities are where you would store your JSON objects for deices that selenium or Appium uses. Remember to add them to the correct platform folder
- "Hooks" is a directory where you can store any hooks for the product under test. There is an example JSON in there for reference with working tests. 

traverse/product
- This is where you would create a directory specifically for your product. Great for specific logic that is for your application, for example, if you have a method to retrieve all "active" users from database ABC, then you have the freedom to create a module for your product and add all custom methods there. Note there is a README.txt file in this directory. 

traverse/reports
- This is where the reports are stored, for example, driver screenshots, or HTML test results(depending on your settings)
- The location of this folder can be changed in traverse_config.json. 

traverse/tests
- This is where all the tests are stored. 
- regression.json and debug.json are always required as they are important for the automation engineer and gives an easy reference to the JSON structure and a template to start working with.
- You can create your JSON, name it what you want (please follow python standards) and you can specify what tests that pack must execute
- The structure is as follows: /traverse/tests/test_pack/test_suite.py
- Note you can name the "test_pack" and "test_suite" whatever you wish, but again, please following python standards is great. 

traverse/utilities
- Any modules, logic or code used to assist the framework, product integration or tests is stored here and imported where necessary

__________________________________________________________________________
######** Traverse Config **######

This is a useful configuration file, called "traverse_config.json" and located in the root directory of traverse. Here is a breakdown of each setting and what it does:

Reports Folder
- This is the location for the reports folder. You can change this to any directory you want. The default is "\\reports\\" which will store reports in traverse/reports

Tests Folder
- This is where tests are located. It may seem strange to want this configurable, but sometimes large integration projects with many teams will usually end up with each team managing their tests, configuring a different tests folder to point to other teams on a server can be useful when they want to quickly check the integration of a product did not break. 

Test Plan Name
- This is the name of the test plan and will be the title of the report when saved. 

Parallel Tests
- This number indicates how many tests you want to run in parallel. If this is set to 0, traverse will run 1 test at a time sequentially. If you set this to 3 it would execute 4 tests at the same time. 

Debug Enabled
- If you enable this, traverse will only run tests in the debug.json file in the tests directory

Report Type
- This changes what report will be used. 
- Set it to "HTML" to have an HTML report generated and opened in your default browser once execution is complete.
- Set is to "cmd" and the results will be shown in the console

Report On The Go
- If this is enabled, each test result will be reported to the CMD as they complete execution
- Useful if you wish to see any failures early on without waiting for all tests to complete

Nuke Reports
- If this is enabled then every time traverse is executed, ALL reports in the "reports" folder will be deleted
- Useful if you want to only see the last completed test run only

__________________________________________________________________________
######** Useful Tips **######

1. Enable Py linting in VS Code
    1.1 SELECT File >> Preferences >> Settings
    1.2 Select Workspace settings
    1.3 Open the settings.json file (Usually a small icon somewhere on the top right of the screen)
    1.4 Add the following entries to the file:
        "python.linting.pylintEnabled": true,
        "python.linting.pylintArgs": [
            "--enable=W0614",
            "--max-line-length=150"
        ]
    1.5 Save

2. Change to view output in the debug console
    2.1 Select Debug
    2.2 Select edit configuration
    2.3 Change 'integratedTerminal' to 'internalConsole'
    2.4 Save, you now get the benefit of colour coded feedback from traverso

3. Pylint not working
    3.1 Ensure your PATH variables are set up correctly in environment variables
    3.2 Upgrade pip by using python -m pip install –upgrade pip
    3.3 Also install pylint via pip, sometimes this has been missing for some reason: pip install pylint

__________________________________________________________________________
######** Prepare Your Own Test **######

This assumes you have downloaded the code and you have already opened it in your preferred IDE. If you are only interested in "Non-UI" tests, then steps 1, 2 and 6 will be all you need. If you intend to automate the UI, using a driver like selenium then all steps would apply. 

1. Check Traverse Settings
- Go to the root directory of traverse
- Open traverse_config.json
- Check settings and change as you require. Enabling debug will make it easier to write and test your tests

2. Create the Test Pack/Suite and Test Class
- Go into the directory traverse/tests
- Create a new directory, call it what you want (This is the text pack)
- Go inside your newly created directory and create a new empty .py file. Call it what you like(This is the test suite)
- Open the newly created .py file. You now need to paste the skeleton into this file. Do so by copy-pasting from an already existing test suite. This will make it ready for tests to be written. You can begin by creating a new method in this test class and starting to write your first test. 
- For reference, the code you need to copy-paste is this here:

''' This is a test module where a test class will be stored. '''

class Tests:
    ''' This test class holds test methods. The name of the class must remain exactly "Tests" for the core to pick it up. '''
    def __init__(self, traverse_config, test_definition):
        self.t_config = traverse_config
        self.t_def = test_definition


3. Bring in Selenium (If you require it for UI tests, API and DB tests don't need this)
P.S. I have not wrapped ALL selenium functions, I plan to do them as I need, but this does not mean you do not have access to selenium directly via the DriverActions class ;)
- In your test class, under the __init__ method, add this line:
    self.driver = DriverActions(self.t_def.platform, self.t_def.capability)
- You will now be able to access all selenium functions from the driver interface. 

4. Register hooks for your product
- Go to the directory: traverse/driver/hooks
- Create a new .json file, name it what you want (Preferably the name of your product)
- The structure of the json is as follows:
{
    "nameOfHook1": {
        "type": "id",
        "value": "pageTitle"
    },
    "nameOfHook2": {
        "type": "xpath",
        "value": "//*[@id="tsf"]/div[2]/div[1]/div[1]/a/img"
    }
}
- You will notice you can name your hook anything, this allows you the ability to create your naming standards or follow the same standards as your organisation.
- Once complete do not forget to let the driver interface know which hooks you want
- As an additional note, you could create multiple hook files to organise a products hooks into categories or even modules

5. Let Selenium know your hook file
- Go to your Tests class
- When declaring to selenium your hook file, add/change this line of code, found in the __init__ method:
self.driver = DriverActions(self.t_def.platform, self.t_def.capability, 'my_hook_file')
- This means selenium will load a file called my_hook_file.json, giving you access to those hooks in the test
- Q: Why do this instead of just passing the values directly to selenium? 
- A: You can pass values directly but you end up with repetitive code, you are still able to do so, as I have allowed it in the driver interface, but its cleaner and easily maintainable to use the hook files. Example:
Code using No hook file:
self.driver.select_element('homeBtn', 'homeBtn')

Code using a hook file:
self.driver.select_element('homeBtn')

6. Create a product interface for your product
- Go to the directory traverse/product
- Create a new directory titled anything you want (Usually the name of the product makes sense)
- Note there is a README.txt file in this directory as well
- Go into your newly created directory
- Create a new .py file
- This now gives you the freedom to create any class and methods you want that are specific to your product. 
- To use the methods in your tests, simply import using standard Python imports, and you may need to add it to the __init__ method of the test class, that way you can utilise any settings or configs in the test definition and/or the traverse config.
