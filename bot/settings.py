import os
import pathlib

BASE_PATH = pathlib.Path(__file__).parent
STORAGE_DIR = os.path.join(BASE_PATH, "storage")
FILES_DIR = os.path.join(STORAGE_DIR, "files")
BOT_STORAGE = os.path.join(STORAGE_DIR, "storage.json")
TERM_OF_USE_FILEPATH = os.path.join(FILES_DIR, "terms.txt")
POLICY_FILEPATH = os.path.join(FILES_DIR, "policy.txt")
SITE_DOMAIN = ""
SITE_ID = ""
