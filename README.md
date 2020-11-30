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