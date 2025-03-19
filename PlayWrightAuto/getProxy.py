import requests
import json
import random

class ProxyRequest:
        def __init__(self):
                self.URL = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&country=br&protocol=http&proxy_format=protocolipport&format=json&timeout=20000"

        def publicListGeneration(self, qnt=1):
                result = []
                proxies_list = json.loads(requests.get(self.URL).content)["proxies"]
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
                "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=25",
                headers={"Authorization": "Token nmhiuqk9owpotpjmexexcd8d4u405dojp9irp3ks"}
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