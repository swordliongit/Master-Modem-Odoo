#
# Author: Kılıçarslan SIMSIKI
#


import os

username = ""
password = ""


def create_directory(filename):
    # Extract the directory name from the file path
    dirname = os.path.dirname(filename)
    # Create the directory if it does not exist
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def u_p_setter(u, p):
    global username, password
    username = u
    password = p
