import requests
from bs4 import BeautifulSoup
import json
import logging
import aiohttp
import asyncio

logging.basicConfig(level=logging.INFO)
# TODO:
# dejar una función main que invoque al Scraper al ejecutar el script por fuera de la clase


class Scrapper:
    def __init__(self):
        self.url = "https://simpsonizados.me/serie/los-simpson/"
        self.__db = "episode_filename.json"

    async def get_description(self, description_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(description_url) as response:
                response_json = await response.text()
                resumen_soup = BeautifulSoup(response_json, "lxml")
                description = resumen_soup.find("p").get_text()
                return description

    async def serialize_episode(self, extracted_episodes):
        result = []
        for i in range(0, len(extracted_episodes)):
            logging.info("\n Realizando temporada: ", i + 1, "\n")
            episode = extracted_episodes[i].find_all("li")
            for j in range(0, len(episode)):
                dicc = {
                    "Nro capitulo": episode[j]
                    .find("div", class_="numerando")
                    .get_text()
                    .split("-")[1]
                    .strip(),
                    "Nombre capitulo": episode[j].find("a").get_text(),
                    "Temporada": episode[j]
                    .find("div", class_="numerando")
                    .get_text()
                    .split("-")[0]
                    .strip(),
                    "Fecha emision": episode[j].find("span", class_="date").get_text(),
                    "url": episode[j].find("a")["href"],
                }
                logging.info(dicc)
                dicc["Descripcion"] = await self.get_description(dicc["url"])
                result.append(dicc)

        return result

    async def scrap(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                response_json = await response.text()
                soup = BeautifulSoup(response_json, "lxml")
                extracted_episodes = soup.find_all("ul", class_="episodios")
                seasons = await self.serialize_episode(extracted_episodes)
                self.write(seasons)

    def write(self, episodes):
        with open(self.__db, "w", encoding="utf-8") as f:
            json.dump(episodes, f, ensure_ascii=False, indent=4)

    def episodes(self, offset=0, limit=None):
        with open(self.__db, "r") as file:
            read_content = json.loads(file.read())
            logging.info(read_content[offset:limit])


# Número del capítulo
# Nombre del capítulo
# Resumen del capítulo
# Número de temporada
# Fecha de emisión
# URL del video

c = Scrapper()
# c.scrap()
# c.episodes(offset=2, limit=3)
# c.scrap()
# c.write()
# c.read(limit=3)
# async def main():
#     await Scrapper().scrap()
# main()
loop = asyncio.get_event_loop()
loop.run_until_complete(c.scrap())