''' This module is geared towards helper classes for any operations around terminal or command prompt output.
    This can be anything from color coding text to handling linus vs windows terminals '''

class ColorCodes:
    ''' A reference class to store color codes for changing text color in the terminal. Useful for reporting. '''
    # Standard Uses
    ENDC = '\033[0m' # Used to end color
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CITALIC = '\33[3m'
    WHITE = '\033[97m'
    LIGHT_GREY = '\033[37m'
    DARK_GREY = '\033[90m'
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
