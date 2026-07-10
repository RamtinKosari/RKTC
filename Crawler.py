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
    # - Method to Check if Message is Valid
    def METHOD_IS_VALID_MESSAGE(self, text):
        if not text:
            return False
        clean = text.strip()
        ignored_words = RKTC_IGNORED_WORDS
        if clean.lower() in ignored_words:
            return False
        if len(clean) < 20:
            return False
        return True
    # - Method to Find Message
    def METHOD_FIND_MESSAGE(self, messages, message_id):
        for msg in messages:
            if msg["id"] == message_id:
                return msg
        return None
    # - Method to Get Category Name
    def METHOD_GET_CATEGORY_NAMES(self, categories):
        return "\n".join(
            [
                f"{cat['id']}. {cat['name']}"
                for cat in categories
            ]
        )
    # - Method to Find Category
    def METHOD_FIND_CATEGORY(self, categories, name):
        for category in categories:
            if category["name"] == name:
                return category
        return None