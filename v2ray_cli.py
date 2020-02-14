#! /usr/bin/python3

import os
from subscribe import Subscribe

url_pathname = "./url.txt"
conf_pathname = "./config.json"

if __name__ == "__main__":
    if os.path.exists(url_pathname):
        with open(url_pathname, "r") as f:
            url = f.read()
    else:
        url = input("Please Enter The Subscription Aadress: ")
        
        with open(url_pathname, "w") as f:
            f.write(url)

    sub = Subscribe(url, conf_pathname)
    