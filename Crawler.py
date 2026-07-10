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
    # - Method to Add New Category
    def METHOD_ADD_CATEGORY(self, categories, name):
        existing = self.METHOD_FIND_CATEGORY(
            categories,
            name
        )
        if existing:
            return existing
        new_category = {
            "id": len(categories) + 1,
            "name": name
        }
        categories.append(new_category)
        return new_category
    # - Method to Build Category Messages
    def METHOD_BUILD_CATEGORY_MESSAGES(
        self,
        categories,
        messages
    ):
        result = []
        # - Create Category Containers
        category_map = {}
        for category in categories:
            category_map[category["id"]] = {
                "category_id": category["id"],
                "category_name": category["name"],
                "messages": []
            }
        # - Find Main Messages
        message_map = {}
        for message in messages:
            message_map[message["id"]] = message
        # - Attach Main Messages
        for message in messages:
            if message["category_id"] not in category_map:
                continue
            # - Only Main Messages
            if message["parent_id"] is None:
                msg_obj = {
                    "id": message["id"],
                    "timestamp": message["timestamp"],
                    "text": message["text"],
                    "keywords": message.get(
                        "keywords",
                        ""
                    ),
                    "replies": []
                }
                category_map[
                    message["category_id"]
                ]["messages"].append(msg_obj)
        # - Attach Replies
        main_lookup = {}
        for category in category_map.values():
            for msg in category["messages"]:
                main_lookup[msg["id"]] = msg
        for message in messages:
            parent_id = message.get(
                "parent_id"
            )
            if parent_id in main_lookup:
                reply = {
                    "id": message["id"],
                    "timestamp": message["timestamp"],
                    "text": message["text"],
                    "keywords": message.get(
                        "keywords",
                        ""
                    )
                }
                main_lookup[parent_id]["replies"].append(
                    reply
                )
        # - Sort by Timestamp
        for category in category_map.values():
            category["messages"].sort(
                key = lambda x: x["timestamp"]
            )
            for message in category["messages"]:
                message["replies"].sort(
                    key = lambda x: x["timestamp"]
                )
            result.append(category)
        result.sort(
            key = lambda x: x["category_id"]
        )
        self.METHOD_SAVE_JSON(
            "category_messages.json",
            result
        )