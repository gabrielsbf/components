from playwright.sync_api import Locator, Page
import logging

def safeLocator(self, xmlPath:str, description="Não Definido")->Locator:
        def check_locator(xmlPath, description):
            try:
                if xmlPath == "input":
                    xmlPath = input(f"Digite o path do locator: {description}\n")
                logging.info(f"Locator a procurar: {description}")
                self.wait_for_selector(xmlPath, timeout=50000)
                return True
            except:
                logging.error(f"O locator {description} não foi encontrado. Path -> {xmlPath}")
                return False
        self.wait_for_load_state('domcontentloaded', timeout=50000)
        if not check_locator(xmlPath, description) :
            raise Exception(f"ERRO: Não foi possível encontrar o seguinte locator: {description} - Path -> {xmlPath}")
        return self.locator(xmlPath)

def _safeLocator(self, xmlPath:str, description="Não Definido")->Locator:
        def check_locator(xmlPath, description):
            try:
                if xmlPath == "input":
                    xmlPath = input(f"Digite o path do locator: {description}\n")
                logging.info(f"Locator a procurar: {description}\n")
                self.locator(xmlPath).nth(0).wait_for()
                logging.info(f"Locator encontrado\n")
                return True
            except:
                logging.error(f"O locator {description} não foi encontrado. Path -> {xmlPath}")
                input("Pressione ENTER para continuar...")
                return False
        if not check_locator(xmlPath, description) :
            raise Exception(f"ERRO: Não foi possível encontrar o seguinte locator: {description} - Path -> {xmlPath}")
        return self.locator(xmlPath)

Locator.safeLocator = _safeLocator
Page.safeLocator = safeLocator