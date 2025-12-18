from playwright.sync_api import Locator, Page
import logging

def safeLocator(self, xmlPath:str, description="Não Definido")->Locator:
        def check_locator(xmlPath, description):
            try:
                self.wait_for_selector(xmlPath, timeout=5000)
                logging.info(f"Locator encontrado: {description}\n")
                return True
            except:
                logging.error(f"O locator {description} não foi encontrado. Path -> {xmlPath}")
                return False
        if not check_locator(xmlPath, description) :
            raise Exception(f"ERRO: Não foi possível encontrar o seguinte locator: {description} - Path -> {xmlPath}")
        return self.locator(xmlPath)

async def _safeLocator(self, xmlPath: str, description="Não Definido"):
    async def check_locator(xmlPath, description):
        try:
            # Apenas cria o locator e tenta acessá-lo de forma segura
            loc = self.page.locator(xmlPath)
            await loc.count()  # força verificação sem erro
            logging.info(f"Locator encontrado: {description}\n")
            return True
        except:
            logging.error(f"O locator {description} não foi encontrado. Path -> {xmlPath}")
            input("Pressione ENTER para continuar...")
            return False

    if not await check_locator(xmlPath, description):
        raise Exception(
            f"ERRO: Não foi possível encontrar o seguinte locator: {description} - Path -> {xmlPath}"
        )

    return self.page.locator(xmlPath)

Locator.safeLocator = _safeLocator
Page.safeLocator = safeLocator