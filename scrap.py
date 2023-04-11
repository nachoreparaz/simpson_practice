import requests
from bs4 import BeautifulSoup
import json
from threading import Thread


class Scrapping:
    def __init__(self):
        self.url = 'https://simpsonizados.me/serie/los-simpson/'
        self.__db = 'simpson_db.json'

    def get_data(self):
        extracted_episodes_catalog = []

        for season in self._extract_seasons():
            episodes = self._extract_episodes_catalog(season)

            threads = [
                Thread(target=self._extract_episode, args=(episode, extracted_episodes_catalog)) for episode in episodes
            ]

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

        return extracted_episodes_catalog

    def _extract_episode(self, episode, extracted_episodes_catalog):
        episode_number = self._extract_episode_number(episode)
        season_number = self._extract_season_number(episode)

        print(f'Realizando temporada: {season_number}x{episode_number}...')

        extracted_episode = {
            'Nro capitulo': episode_number,
            'Nombre capitulo': self._extract_episode_name(episode),
            'Temporada': season_number,
            'Fecha emision': self._extract_emission_date(episode),
            'url': self.extract_episode_url(episode),
        }

        try:
            extracted_episode['Resumen'] = self._extract_episode_summary(extracted_episode)
            extracted_episodes_catalog.append(extracted_episode)
        except Exception as e:
            print('Error al obtener el resumen del capítulo', e)
        else:
            print('Episodio nro ', extracted_episode['Nro capitulo'], ' realizado')

    def _extract_seasons(self):
        soup = self._get_soup(self.url)
        return soup.find_all('ul', class_='episodios')

    def _extract_episode_summary(self, episode):
        soup = self._get_soup(episode['url'])
        return soup.find('p').get_text()

    def extract_episode_url(self, episode):
        return episode.find('a')['href']

    def _extract_emission_date(self, episode):
        return episode.find('span', class_='date').get_text()

    def _extract_season_number(self, episode):
        return episode.find('div', class_='numerando').get_text().split('-')[0].strip()

    def _extract_episode_name(self, episode):
        return ' '.join(episode.find('a').get_text().split())

    def _extract_episode_number(self, episode):
        return episode.find('div', class_='numerando').get_text().split('-')[1].strip()

    def _extract_episodes_catalog(self, season):
        return season.find_all('li')

    def _get_soup(self, url):
        req = requests.get(url)
        page = req.text
        soup = BeautifulSoup(page, 'lxml')
        return soup

    def write(self, data):
        with open(self.__db, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return self.__db

    def read(self, offset=0, limit=None):
        data = open(self.__db, 'r').read()
        data_json = json.loads(data)
        for i in range(offset, limit or len(data_json)):
            print('\n', data_json[i], '\n')


def main():
    c = Scrapping()
    extracted_episodes = c.get_data()
    filename = c.write(extracted_episodes)
    print(f"Scrapping finalizado, guardado en {filename}")


if __name__ == '__main__':
    main()
