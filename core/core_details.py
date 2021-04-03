''' core_details is a module which holds classes realted to core features. Such as a class that holds test statuses,
    or the test definition. These classes are usually shared across core modules and re-used often, sometimes by other
    modules not related to core.  '''

import itertools


class TestStatus:
    ''' A holding class for all available test statuses. '''
    UNTESTED = 'Untested'
    PASSED = 'Passed'
    FAILED = 'Failed'
    BLOCKED = 'Blocked'
    RETEST = 'Retest'
    IN_PROGRESS = 'InProgress'


class TestDefinition:
    ''' A class used to track, and keep context of test information for preparing, setup, execution and reporting. '''
    id_itr = itertools.count()
    def __init__(self):
        self.test_id = next(self.id_itr)
        self.test_pack = None
        self.test_suite = None
        self.test_name = None
        self.platform = None
        self.capability = None # If -1 is passed in, this will not require a driver
        self.test_config_title = None
        self.test_config_value = None
        self.production_safe = False

        self.test_status = TestStatus.UNTESTED
        self.test_start_time = None
        self.test_end_time = None
        self.comments = ''

        self.screenshot_dir = None


class ReportType:
    ''' A holding class for the report types we want to use / differentiate or support. '''
    CMD = 'cmd'
    HTML = 'html'
