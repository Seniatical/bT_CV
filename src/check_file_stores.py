############################################
# FILENAME: check_file_stores.py
# PATH: ${SRC_DIR}/core/check_file_stores.py
# DEBUG: false
# PARENT: null
# ;BOUNDARY
# &INIT -> SOURCE_RUN == true
# @BIND SOURCE ${PATH} AS "check_file_stores"
############################################
import os
import pathlib

FILE_STORES = [
    ["images", []]
]
DIRS = [i[0] for i in FILE_STORES]
ENFORCE_MISSING_FILES = True
DELETE_EXTRAS = True
DELETE_EXTRA_DIRS = True
FILE_STORE_DIRECTORY = os.path.abspath("./src/storage")


def makeDirs() -> bool:
    for directory, _ in FILE_STORES:
        directory_path = f"./src/storage/{directory}"

        if not os.path.exists(directory_path):
            os.mkdir(directory_path)
            print("Created new file store directory:", directory)

    return True


def deleteExtraDirs() -> bool:
    if not DELETE_EXTRA_DIRS:
        return False

    for directory in os.listdir(FILE_STORE_DIRECTORY):
        path = FILE_STORE_DIRECTORY + "/" + directory
        if not os.path.isdir(path):
            continue
        if directory not in DIRS:
            os.rmdir(path)
            print("Removed extra file store directory at:", path)

    return True


def deleteExtraFiles() -> bool:
    if not DELETE_EXTRAS:
        return False

    for i in FILE_STORES:
        directory, files = i
        path = FILE_STORE_DIRECTORY + "/" + directory

        for j in os.listdir(path):
            if j not in files:
                path_to_j = path + "/" + j
                os.remove(path_to_j)

                print("Removed file at:", path_to_j)

    return True


def verifyFiles() -> bool:
    for i in FILE_STORES:
        directory, logged_files = i
        path = FILE_STORE_DIRECTORY + "/" + directory
        actual_files = os.listdir(path)

        missing = set(logged_files) - set(actual_files)
        if ENFORCE_MISSING_FILES and missing:
            raise FileNotFoundError(
                "Unable to locate {} missing files\nFILENAMES: {}"
                .format(len(missing), ", ".join(missing))
            )
        elif missing:
            print(
                "WARNING: Unable to locate {} missing files\nFILENAMES: {}"
                .format(len(missing), ", ".join(missing))
            )
        else:
            print("All stored content has been found")


def main():
    print("#"*50)
    print("Now running 'check_file_stores.py' | PRE_CHECK=true")
    print("Status: Building any missing directories")
    makeDirs()

    print("Status: Removing extra directories")
    print("| Ignoring if config is false")
    deleteExtraDirs()

    print("Status: Removing extra files")
    print("| Ignoring if config is false")
    deleteExtraFiles()

    print("Status: Verifying files in storage")
    verifyFiles()

    print("#" * 50)

main()
