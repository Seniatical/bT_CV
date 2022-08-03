############################################
# FILENAME: make_logs.py
# PATH: ${SRC_DIR}/core/make_logs.py
# DEBUG: false
# PARENT: null
# ;BOUNDARY
# &INIT -> SOURCE_RUN == true
# @BIND SOURCE ${PATH} AS "init_logs"
############################################

import logging
import os

DESTROY_PREV_LOGS = True
DISPLAY_TO_STDOUT = True
LOG_DIR = os.path.abspath("./src/logs")
LOG_LEVEL = logging.DEBUG
LOG_FILES = [
    "discord.log",
    "commands.log",
    "database.log"
]


def destroy_logs() -> bool:
    if not DESTROY_PREV_LOGS:
        return False

    for log_file in os.listdir(LOG_DIR):
        try:
            os.remove(os.path.join(LOG_DIR, log_file))
        except OSError as e:
            print("Failed to remove old log files:", e)
            return False
    print("Log files ", LOG_FILES, "Have been removed if present")
    return True


def create_logs() -> bool:
    if not os.path.exists(LOG_DIR):
        print("Log folder not found, creating new log folder")
        os.mkdir(LOG_DIR)

    for log_file in LOG_FILES:
        print("Attempting to create log file:", log_file)
        LOG_PATH = os.path.join(LOG_DIR, log_file)

        if os.path.exists(LOG_PATH) and not DESTROY_PREV_LOGS:
            print("Skipping \"", log_file, "\" file already exists.")
            continue

        try:
            open(LOG_PATH, "w").close()
            print("Created log file \"", log_file, "\" successfully")
        except OSError as e:
            print("Failed to create log files:", e)
            print("Skipping log file creation")
            return False
    return True


def main():
    print("#"*50)
    print("Now running 'make_logs.py' | PRE_CHECK=true")
    print("Status: Destroying old log files")

    dStatus = destroy_logs()
    if not dStatus:
        print("Log files not destroyed, either files cannot be found or option to destroy is disabled")
        print("LOG_OPTION [DESTROY_LOG_FILES] =", DESTROY_PREV_LOGS)
    else:
        print("Previous log files have been removed successfully")

    print("Status: Creating new log files, existing log files may be ignored")
    cStatus = create_logs()

    if not cStatus:
        print("Failed to create new files, either log directory cannot be found or system is lacking permissions")
    else:
        print("Log files have successfully been created")

    print("Status: Log files are ready to be used")
    print("#" * 50)


main()
