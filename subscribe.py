import base64
import requests
import json
import os
import ast


class Subscribe(object):
    def __init__(self, url, json_template_pathname):
        self.__url = url    # 订阅链接
        self.__source = {}  # 订阅的各节点
        self.__node = {}    # 订阅的各节点名称
        self.__json_template_pathname = json_template_pathname
        self.__json_conf_pathname = "./config.json"
        self.update()

    def update(self):
        try:
            ret = requests.get(self.__url, headers={'user-agent': 'v2ray/1.0'})
            if ret.status_code != 200:
                print("Requests Error")
                return
        except ConnectionError:
            print("Connection Error")
            return

        all_subs = base64.b64decode(ret.text).decode().strip().split("\n")

        for item in all_subs:
            subs = []
            subs.append(item.split("://"))

            item_protocol = subs[-1][0]
            item_source = subs[-1][1]

            if item_protocol == "vmess":
                try:
                    item_source_bytes = base64.b64decode(item_source)
                    item_node = json.loads(item_source_bytes.decode("utf-8"))
                    self.__source[item_node["ps"]] = item_node
                except ValueError as e:
                    print("ValueError: %s" % e)
                    pass
            else:
                print("%s not support" % item_protocol)

        while (1):
            try:
                self.show()
                num = input("Please Enter Node Num:")
                self.sub2conf(self.__node[num], "vmess")
                break
            except KeyError as e:
                print("%s: %s" % ("Out Of Node Range", e))

    def show(self):
        num = 0
        print("num\tnode")
        for item in self.__source.keys():
            print("%d\t%s" % (num, item.encode('utf-16', 'surrogatepass').decode('utf-16')))
            self.__node[str(num)] = item
            num += 1

    def sub2conf(self, name, protocol):
        print("Node Selected: %s" % name.encode('utf-16', 'surrogatepass').decode('utf-16'))
        sub = self.__source[name]
        index = -1

        # debug sub
        # print(sub)

        try:
            with open(self.__json_template_pathname, "r") as f:
                conf = json.load(f)
        except FileNotFoundError:
            print("miss file: config.json")
            pass

        for c in conf["outbounds"]:
            if protocol == c["protocol"]:
                index = conf["outbounds"].index(c)

        if -1 == index:
            print("Unsupport protocol: %s" % protocol)
            return

        if protocol == "vmess":
            conf["outbounds"][index]["settings"]["vnext"][-1]["address"] = sub["add"]
            conf["outbounds"][index]["settings"]["vnext"][-1]["port"] = int(sub["port"])
            conf["outbounds"][index]["settings"]["vnext"][-1]["users"][-1]["id"] = sub["id"]
            conf["outbounds"][index]["settings"]["vnext"][-1]["users"][-1]["alterId"] = int(sub["aid"])
            conf["outbounds"][index]["streamSettings"]["network"] = sub["net"]

            conf["outbounds"][index]["streamSettings"]["security"] = sub["tls"]
            if sub["tls"] == "tls":
                conf["outbounds"][index]["streamSettings"]["tlssettings"] = {}
                conf["outbounds"][index]["streamSettings"]["tlssettings"]["allowInsecure"] = True
                conf["outbounds"][index]["streamSettings"]["tlssettings"]["serverName"] = sub["host"]
            else:
                conf["outbounds"][index]["streamSettings"]["tlssettings"] = {}

            if sub["net"] == "ws":
                conf["outbounds"][index]["streamSettings"]["wssettings"] = {}
                conf["outbounds"][index]["streamSettings"]["wssettings"]["connectionReuse"] = True
                conf["outbounds"][index]["streamSettings"]["wssettings"]["headers"] = {}
                conf["outbounds"][index]["streamSettings"]["wssettings"]["headers"]["Host"] = sub["host"]
                conf["outbounds"][index]["streamSettings"]["wssettings"]["path"] = sub["path"].replace('\\', '')
            else:
                conf["outbounds"][index]["streamSettings"]["wssettings"] = {}

        try:
            with open(self.__json_conf_pathname, "w") as f:
                f.write(json.dumps(conf, indent=4))
            print("Node Configure Write File OK")
        except Exception:
            print("config.json write error")
            return

        os.system("killall v2ray")
        os.system("/usr/bin/v2ray/v2ray ./config.json &")
