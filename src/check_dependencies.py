############################################
# FILENAME: check_dependencies.py
# PATH: ${SRC_DIR}/core/check_dependencies.py
# DEBUG: false
# PARENT: null
# ;BOUNDARY
# &INIT -> SOURCE_RUN == true
# @BIND SOURCE ${PATH} AS "check_dependencies"
############################################

import os
import pip._internal.req.req_file as reqFile
import pip._internal.network.session as pSession
import pkg_resources
import sys
import subprocess

DEPENDENCY_FILE = os.path.abspath("./requirements.txt")
INSTALL_MISSING_DEPENDENCIES = True
REQUIREMENTS = list()
TO_INSTALL = list()


def load_requirements() -> bool:
    if not os.path.exists(DEPENDENCY_FILE):
        return False

    pipSession = pSession.PipSession()
    REQUIREMENTS.extend(reqFile.parse_requirements(DEPENDENCY_FILE, pipSession))

    return True


def test_requirements() -> bool:
    installed = {pkg.key for pkg in pkg_resources.working_set}
    try:
        missing = {r.name for r in REQUIREMENTS} - installed
    except AttributeError:
        missing = {r.requirement for r in REQUIREMENTS} - installed

    print("Found a total of", len(installed), "installed libs")
    print(len(REQUIREMENTS), "libs required")

    if missing:
        for i in missing:
            r = None
            for j in REQUIREMENTS:
                if getattr(j, "name", getattr(j, "requirement", "")) == i:
                    r = j
                    break

            if not r:
                print("Skipping installation of \"", i, "\" - Unable find to requirement")
            else:
                TO_INSTALL.append(r)

        print("Missing", len(missing), "libs")
        print("Missing libs: ", [i.name for i in TO_INSTALL])
        return False
    return True


def install_requirements():
    print("Attempting to install", len(TO_INSTALL), "libs")

    for i in TO_INSTALL:
        if i.check_if_exists(True):
            print("Skipping installation of \"", i.name, "\" as lib already exists")
        else:
            r = str(i.req)
            print("-"*50)
            try:
                subprocess.check_call(
                    [sys.executable, '-m', 'pip', 'install', r],
                    stdout=sys.stdout, stderr=sys.stderr
                )
            except Exception as err:
                print("Failed to install \"", i.name, "\": ", err)

            print("-"*50)
    print("Installed all missing libs")

def main():
    print("#"*50)
    print("Now running 'check_dependencies.py' | PRE_CHECK=true")
    print("Status: Loading requirements from:", DEPENDENCY_FILE)

    lStatus = load_requirements()
    if not lStatus:
        print("Failed to load requirements, check requirements file")

    print("Status: Testing for missing requirements")
    tStatus = test_requirements()

    if tStatus:
        print("All dependencies are already installed, skipping installation")
    else:
        install_requirements()

    print("Dependencies have all been installed.")
    print("#" * 50)

main()
