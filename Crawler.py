# - Import Configuration File
from Configs import *
# - Import Log Methods
from utils.LogMethods import *

# - Ramtin Kosari Telegram Crawler Class
class RKTC:
    # - Method to Initialize RKTC Object
    def __init__(self):
        # - Telegram Client
        self.client = None
    # - Method to Chat with the Language Model
    def METHOD_CHAT(self, prompt):
        try:
            response = chat(
                model = RKTC_MODEL,
                options = RKTC_OPTIONS,
                messages = [{'role': 'user', 'content': prompt}]
            )
            # Accessing the response content correctly
            return response['message']['content'].strip().replace('"', '').replace("'", "")
        except Exception as e:
            printRKTC(FAILURE, "Cannot Generate Response : {}{}{}".format(ERR, e, RESET))
    # - Method to Load JSON
    def METHOD_LOAD_JSON(self, filename, default):
        if os.path.exists(filename):
            with open(filename, 'r', encoding = 'utf-8') as f:
                return json.load(f)
        return default
    # - Method to Save JSON
    def METHOD_SAVE_JSON(self, filename, data):
        with open(filename, 'w', encoding = 'utf-8') as f:
            json.dump(data, f, ensure_ascii = False, indent = 4)