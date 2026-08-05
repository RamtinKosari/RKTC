# - Import Configuration File
from Configs import *
# - Import Log Methods
from utils.LogMethods import *
# - Import Category Normalizer
from utils.CategoryNormalizer import CategoryNormalizer

# - Ramtin Kosari Telegram Crawler Class
class RKTC:
    # - Method to Initialize RKTC Object
    def __init__(self):
        # - Telegram Client
        self.client = None
        # - Category Normalizer
        self.normalizer = CategoryNormalizer()
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
    # - Method to Check if Category is Related to Project Purpose
    def METHOD_CHECK_CATEGORY_PURPOSE(self, category_name):
        try:
            prompt = RKTC_PURPOSE_PROMPT.format(RKTC_PURPOSE, category_name)
            response = self.METHOD_CHAT(prompt)
            if response:
                normalized = response.lower()
                if "yes" in normalized:
                    return "main"
                if "no" in normalized:
                    return "other"
        except Exception as e:
            printRKTC(FAILURE, "Cannot Check Category Purpose : {}{}{}".format(ERR, e, RESET))
        return "main"
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
        # - Canonicalize Category Name
        canonical_name = self.normalizer.METHOD_CANONICALIZE(name)
        existing = self.METHOD_FIND_CATEGORY(
            categories,
            canonical_name
        )
        if existing:
            return existing
        # - Check Purpose
        category_type = self.METHOD_CHECK_CATEGORY_PURPOSE(canonical_name)
        new_category = {
            "id": len(categories) + 1,
            "name": canonical_name,
            "type": category_type
        }
        categories.append(new_category)
        printRKTC(SUCCESS, "New Category : {}{} ({}){}".format(LIGHT_INFO, canonical_name, category_type, RESET))
        return new_category
    # - Method to Update Missing Category Types
    def METHOD_UPDATE_CATEGORY_TYPES(self, categories):
        updated = False
        for category in categories:
            if "type" not in category or not category["type"]:
                category["type"] = self.METHOD_CHECK_CATEGORY_PURPOSE(category["name"])
                printRKTC(PROCESS, "Classified Category : {}{} ({}){}".format(LIGHT_INFO, category["name"], category["type"], RESET))
                updated = True
        return updated
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
    # - Main Workflow
    async def METHOD_RUN(self):
        # - Initialize Telegram Client
        self.client = TelegramClient(
            'crawler_session',
            RKTC_API_ID,
            RKTC_API_HASH,
            proxy = RKTC_PROXY,
            connection = ConnectionTcpFull
        )
        # - Open Session
        async with self.client:
            # - Load Data
            all_messages = self.METHOD_LOAD_JSON('messages.json', [])
            categories = self.METHOD_LOAD_JSON('categories.json', [])
            # - Rebuild Normalizer Index from Existing Categories
            self.normalizer.METHOD_REBUILD_INDEX(categories)
            # - Classify Missing Category Types
            if self.METHOD_UPDATE_CATEGORY_TYPES(categories):
                self.METHOD_SAVE_JSON('categories.json', categories)
                self.METHOD_BUILD_CATEGORY_MESSAGES(categories, all_messages)
            else:
                self.METHOD_BUILD_CATEGORY_MESSAGES(categories, all_messages)
            processed_ids = {
                item['id']
                for item in all_messages
            }
            start_time = time.time()
            processed_count = 0
            iteration_count = 0
            total_limit = RKTC_ITERATION_LIMIT
            durations = []
            printRKTC(SUCCESS, "Session Initialized, Starting ...")
            async for message in self.client.iter_messages(
                RKTC_TARGET_CHANNEL,
                limit = RKTC_ITERATION_LIMIT,
                min_id = 116626,
                reverse = True,
            ):
                # - Count Iteration
                iteration_count += 1
                # - Start Time
                message_start = time.time()
                # - Ignore Processed or Non-Text Messages
                if (
                    not message.text
                    or message.id in processed_ids
                ):
                    continue
                text = message.text.strip()
                msg_time = message.date.isoformat()
                parent_id = message.reply_to_msg_id
                # - Case 1 : Reply Message
                if parent_id:

                    parent = self.METHOD_FIND_MESSAGE(
                        all_messages,
                        parent_id
                    )
                    # - Parent Already Categorized, Inherit Category
                    if parent:
                        msg_obj = {
                            "id": message.id,
                            "parent_id": parent_id,
                            "timestamp": msg_time,
                            "text": text,
                            "context": "reply",
                            "category_id": parent["category_id"]
                        }
                        all_messages.append(msg_obj)
                        self.METHOD_SAVE_JSON(
                            'messages.json',
                            all_messages
                        )
                        continue
                    # - Parent is Unavailable, Ignore Invalid Messages
                    if not self.METHOD_IS_VALID_MESSAGE(text):
                        continue
                # - Case 2 : Standalone Message
                else:
                    if not self.METHOD_IS_VALID_MESSAGE(text):
                        continue
                # - AI Analysis
                printRKTC(PROCESS, "Analysing Message : {}{}{}".format(DARK_INFO, str(text[:30]).strip(), RESET))
                category_context = self.METHOD_GET_CATEGORY_NAMES(categories)
                # - Generate Prompt
                prompt = RKTC_PROMPT.format(category_context, text)
                # - Get Model's Response
                response = self.METHOD_CHAT(prompt)
                if not response:
                    continue
                # - Parse AI Response
                try:
                    category_line, keyword_line = response.split("\n", 1)
                    category_name = (category_line.replace("Category:", "").strip())
                    keywords = (keyword_line.replace("Keywords:", "").strip())
                except Exception as e:
                    printRKTC(FAILURE, "Invalid AI Response Format : {}{}{}".format(ERR, e, RESET))
                    continue
                # - Validate Category
                if (not category_name or len(category_name) < 3):
                    printRKTC(FAILURE, "Invalid Category")
                    continue
                printRKTC(SUCCESS, "Category : {}{}{}".format(LIGHT_INFO, category_name, RESET))
                printRKTC(SUCCESS, "Keywords : {}{}{}".format(LIGHT_INFO, keywords, RESET))
                # - Create / Find Category
                category = self.METHOD_ADD_CATEGORY(categories, category_name)
                # - Create Message Object
                msg_obj = {
                    "id": message.id,
                    "parent_id": parent_id,
                    "timestamp": msg_time,
                    "text": text,
                    "keywords": keywords,
                    "category_id": category["id"],
                    "context": "main"
                }
                # - Save Message
                all_messages.append(
                    msg_obj
                )
                # - Keep Chronological Order
                all_messages.sort(
                    key = lambda x: x["timestamp"]
                )
                # - Save Files
                self.METHOD_SAVE_JSON('messages.json', all_messages)
                self.METHOD_SAVE_JSON('categories.json', categories)
                message_duration = time.time() - message_start
                durations.append(message_duration)
                processed_count += 1
                average_time = sum(durations) / len(durations)
                # - Estimate Remaining Time
                remaining_iterations = total_limit - iteration_count
                if iteration_count > 0:
                    process_ratio = processed_count / iteration_count
                else:
                    process_ratio = 1.0
                estimated_remaining_processed = remaining_iterations * process_ratio
                estimated_seconds = estimated_remaining_processed * average_time
                elapsed_seconds = time.time() - start_time
                printRKTC(SUCCESS, (
                    f"{INFO}Processed: {processed_count}/{total_limit} | "    f"Iterations: {iteration_count} | "    f"Current: {message_duration:.2f}s | "    f"Average: {CYAN}{average_time:.2f}s{INFO} | "    f"Elapsed: {elapsed_seconds:.0f}s | "    f"Remaining: {YELLOW}{str(timedelta(seconds=int(estimated_seconds)))}{RESET}"
                ))
                await asyncio.sleep(0.05)
            # - Final Category Messages Rebuild
            self.METHOD_BUILD_CATEGORY_MESSAGES(categories, all_messages)
            printRKTC(SUCCESS, "Finished Processing")

# - Run Crawler
crawler = RKTC()
asyncio.run(crawler.METHOD_RUN())
