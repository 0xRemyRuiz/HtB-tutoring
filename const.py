
import os, platform

# ###
# Constants
# ###
loc = str(os.getcwd())
if platform.system() == "Windows":
    loc += '\\'
# TODO: check on linux and macos
else:
    loc += '/'

