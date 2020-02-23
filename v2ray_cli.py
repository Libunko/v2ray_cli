#! /usr/bin/python3

import os
import configparser
from subscribe import Subscribe

cfg_pathname = "./cfg.conf"
json_template_pathname = "./config.json.template"

if __name__ == "__main__":
    cfg = configparser.ConfigParser()
    cfg.read(cfg_pathname, encoding='UTF-8')

    if cfg["subscribe"]["url"] == "":
        url = input("Please Enter The Subscription Aadress: ")
        cfg["subscribe"] = {"url": url}
        with open(cfg_pathname, 'w') as cfg_file:
            cfg.write(cfg_file)
    else:
        url = cfg["subscribe"]["url"]
        
    sub = Subscribe(url, json_template_pathname)
    