############################################
# FILENAME: check_database.py
# PATH: ${SRC_DIR}/core/check_database.py
# DEBUG: false
# PARENT: null
# ;BOUNDARY
# &INIT -> SOURCE_RUN == true
# @BIND SOURCE ${PATH} AS "check_database"
############################################

import os
import subprocess

DATABASE_FILES = [
    "user_config.sqlite",
    "guild_opts.sqlite",
    "stats.sqlite"
]
CLEAR_ON_START = False
REMOVE_EXTRAS = True
DATABASE_DIR = os.path.abspath("./src/database")
FUSER_OPTIONS = {
    "--all": False,
    "--interactive": False,
    "--inode": False,
    "--kill": True,
    "--list-signals": True,
    "--mount": True,
    "--ismountpoint": False,
    "--namespace": "",
    "--silent": False,
    "--SIGNAL": "",
    "--user": True,
    "--verbose": True,
    "--writeonly": False,
    "--version": True,
    "--ipv4": False,
    "--ipv6": False,
    "-": []
}


def checkDatabases():
    global DATABASE_DIR

    if not os.path.exists(DATABASE_DIR):
        os.mkdir("./src/database")
        DATABASE_DIR = os.path.abspath("./src/database")

    for file in (files := os.listdir(DATABASE_DIR)):
        if file not in DATABASE_FILES and REMOVE_EXTRAS:
            print("Found extra file,\"", file, "\", Removing")
            os.remove(DATABASE_DIR + "/" + file)
        elif file in DATABASE_FILES and CLEAR_ON_START:
            print("Found existing database - clearing")
            os.remove(DATABASE_DIR + "/" + file)

    MISSING_REQUIRED = [i for i in DATABASE_FILES if i not in files]
    for mfile in MISSING_REQUIRED:
        open((DATABASE_DIR + "/" + mfile), "w").close()
        print("Created missing database:", mfile)


def checkForLocks():
    ## Using the fuser command, were able to locate any database locks
    ## Alert and kill if requested
    OPTS = []
    for key in FUSER_OPTIONS:
        val = FUSER_OPTIONS[key]

        if not val:
            continue
        if type(val) == bool:
            OPTS.append(key)
        elif type(val) == list:
            OPTS.append(" ".join(val))
        else:
            OPTS.append(key + " " + val)

    for d_file in DATABASE_FILES:
        path = DATABASE_DIR + "/" + d_file
        proc = subprocess.Popen(
            ["fuser", path, *OPTS],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        print("Fuser check for:", d_file)
        print("-"*50)
        for line in proc.stdout:
            print("|", line)
        print("~"*50)
        print("@Errors: ")

        for line in proc.stderr:
            print("|", line)

        print("-"*50)


def main():
    print("#"*50)
    print("Now running 'check_database.py' | PRE_CHECK=true")
    print("Status: Verifying database files")

    checkDatabases()

    print("Status: Checking for database locks and connections")
    checkForLocks()

    print("Status: Checks have been completed")
    print("#" * 50)

main()
