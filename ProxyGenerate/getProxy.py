import requests
import json
import random
from components.cfg_manager.module.env_manager import Read_env
from pathlib import Path

class ProxyRequest:
        def __init__(self):
                self.env_values = Read_env(Path(__file__).parent.joinpath(".env")).env_values

        def publicListGeneration(self, qnt=1):
                result = []
                proxies_list = json.loads(requests.get(self.env_values["URL_PROXYSCRAPE"]).content)["proxies"]
                elements = []
                print(f"proxies list have size: {len(proxies_list)}")
                for _ in range(qnt):
                        index = random.randint(0, len(proxies_list) - 1)
                        while index in elements:
                                index = random.randint(0, len(proxies_list) - 1)
                        elements.append(index)
                for i in elements:
                        proxyEl = proxies_list[i]
                        result.append({"server": proxyEl["proxy"]})
                return result
        
        def getWebShare(self, qnt=1): 
                proxies_list = requests.get(
                self.env_values["URL_WEBSHARE"],
                headers={"authorization": self.env_values["TOKEN_WEBSHARE"]}
                ).json()["results"]
                result = []
                
                elements = []
                print(f"proxies list have size: {len(proxies_list)}")
                for _ in range(qnt):
                        index = random.randint(0, len(proxies_list) - 1)
                        while index in elements:
                                index = random.randint(0, len(proxies_list) - 1)
                        elements.append(index)
                for i in elements:
                        proxyEl = proxies_list[i]
                        print("PROXY EL", proxyEl)
                        result.append({"server": proxyEl["username"] + 
                                                 ":" + proxyEl["password"] +
                                                 "@" + proxyEl["proxy_address"] +
                                                 ":" + str(proxyEl["port"])})
                return result