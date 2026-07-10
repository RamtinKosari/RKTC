# - Import Required Libraries
import datetime
import inspect
import time

# - Show Logs
SHOW_RKTC_LOGS = True

# - Reset Color
RESET = f'\033[0m'
# - Error Color
ERR = f'\033[38;2;255;200;0m'
# - Error Method Name
MERR = f'\033[38;2;242;89;18m'
# - Info Color
INFO = f"\033[38;2;106;140;150m"
# - Error Info Color
ERROR_INFO = f'\033[38;2;210;153;192m'
# - Light Info Color
LIGHT_INFO = f'\033[38;2;106;106;150m'
# - Dark Info Color
DARK_INFO = f'\033[38;2;151;152;170m'
# - Debug Terminal Output
DEBUG_INFO = f'\033[38;2;237;109;0m[DEBUG]\033[0m'
# - Failure Terminal Output
FAILURE = f'\033[38;2;255;0;0m[FAILURE]\033[0m'
# - Success Terminal Output
SUCCESS = f'\033[38;2;0;255;0m[SUCCESS]\033[0m'
# - Warning Terminal Output
WARNING = f'\033[38;2;255;255;0m[WARNING]\033[0m'
# - Info Terminal Output
PROCESS = f'\033[38;2;106;140;150m[PROCESS]\033[0m'
# - RKTC Terminal Output
CRAWLER = f'\033[38;2;143;135;241m[RKTC]\033[0m' + DARK_INFO
# - Tab
TAB = "  "

# - Yellow Color
YELLOW = f'\033[38;2;200;200;0m'
# - Cyan Color
CYAN = f'\033[38;2;0;200;200m'
# - Dark Cyan Color
D2_CYAN = f'\033[38;2;100;130;170m'
# - Green Color
GREEN = f'\033[38;2;0;255;0m'
# - Dark Green Color
DARK_GREEN = f'\033[38;2;0;100;0m'
# - Dark Red
DARK_RED = f'\033[38;2;170;0;0m'
# - Red Color
RED = f'\033[38;2;255;0;0m'
# - Dark Yellow Color
DARK_YELLOW = f'\033[38;2;150;150;0m'

# abc = "✓⚠❖⁂✘✗ ☑☐☒༻◆◈☓⬢⬡"

# - Log Disconnect and Connect
LOG_CONNECTION = False
# - Log Query Execution
LOG_QUERY_EXECUTION = False

# - Method to Print Logs
def printRKTC(*__input, **kargs):
    # - Check if Logs are Enabled
    if SHOW_RKTC_LOGS == False:
        return
    # - Check if force = True has been Passed
    if "force" in kargs:
        if kargs["force"] == True:
            # - Print Current Date and Time
            print(INFO + "(" + time.strftime("%Y-%m-%d %H:%M:%S" + f".{datetime.datetime.now().microsecond // 1000:03d}", time.localtime()) + ") " + CRAWLER, end = ' ', flush = True)
            # - Check Parameters
            for arg in __input:
                print(arg, end = ' ', flush = True)
            # - Print New Line
            print()
            return
    # - Check if Condition is True
    if "condition" in kargs:
        if kargs["condition"] == False:
            return
    # - Print Current Date and Time
    print(INFO + "(" + time.strftime("%Y-%m-%d %H:%M:%S" + f".{datetime.datetime.now().microsecond // 1000:03d}", time.localtime()) + ") " + CRAWLER, end = ' ', flush = True)
    # - Check Parameters
    for arg in __input:
        if arg == FAILURE or arg == WARNING:
            # - Detect Caller Function Name
            caller_name = inspect.currentframe().f_back.f_code.co_name
            caller_line = inspect.currentframe().f_back.f_code.co_firstlineno
            caller_file = "/".join(inspect.currentframe().f_back.f_code.co_filename.split("/")[-2:])
            error_line = inspect.currentframe().f_back.f_lineno
            if arg == FAILURE:
                print(arg, "{}Line {}{}{} of {}{}{} in {}{}{} (Defined in {}) :{}".format(DARK_RED, MERR, error_line, DARK_RED, MERR, caller_file, DARK_RED, MERR, caller_name, DARK_RED, caller_line, RESET), end=' \n{}{}╙╼{} '.format(RED, " "*34, RESET), flush = True)
            else:
                print(arg, "{}Line {}{}{} of {}{}{} in {}{}{} (Defined in {}) :{}".format(DARK_YELLOW, ERR, error_line, DARK_YELLOW, ERR, caller_file, DARK_YELLOW, ERR, caller_name, DARK_YELLOW, caller_line, RESET), end=' \n{}{}╙╼{} '.format(YELLOW, " "*34, RESET), flush = True)
        else:
            print(arg, end = ' ', flush = True)
    # - Print New Line
    print()
    return