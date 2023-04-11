import requests
from bs4 import BeautifulSoup
import json

class Scrapping():
    
    def __init__(self):
      self.url = 'https://simpsonizados.me/serie/los-simpson/'
      self.__db = 'simpson_db.json'

    def get_data(self):
      extracted_episodes_catalog = []

      for season_number, season in enumerate(self._extract_seasons(), start=1):        
          for episode_number, episode in enumerate(self._extract_episodes(season), start=1):
              print(f'Realizando temporada: {season_number}x{episode_number}...')

              extracted_episode = {
                'Nro capitulo': self._extract_episode_number(episode),
                'Nombre capitulo': self._extract_episode_name(episode),
                'Temporada': self._extract_season_number(episode),
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
        
      return extracted_episodes_catalog
    
    def _extract_seasons(self):
      soup = self._get_soup(self.url)
      return soup.find_all('ul', class_='episodios')

    def _extract_episode_summary(self, episode):
        soup = self._get_soup(episode['url'])
        return soup.find('p').get_text()

    def extract_episode_url(self, episode):
        return episode.find('a')['href']

    def _extract_emission_date(self, episode):
        return episode.find('span', class_ = 'date').get_text()

    def _extract_season_number(self, episode):
        return episode.find('div', class_ = 'numerando').get_text().split('-')[0].strip()

    def _extract_episode_name(self, episode):
        return ' '.join(episode.find('a').get_text().split())

    def _extract_episode_number(self, episode):
        return episode.find('div', class_ = 'numerando').get_text().split('-')[1].strip()

    def _extract_episodes(self, season):
        return season.find_all('li')

    def _get_soup(self, url):
        req = requests.get(url)
        page = req.text
        soup = BeautifulSoup(page, 'lxml')
        return soup
    
    def write(self):
      data = self.get_data()
      with open(self.__db, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    def read(self, offset = 0, limit = None):
      data = open(self.__db, 'r').read()
      data_json = json.loads(data)
      for i in range(offset, limit or len(data_json)):
        print('\n', data_json[i], '\n')


# Número del capítulo
# Nombre del capítulo
# Resumen del capítulo
# Número de temporada
# Fecha de emisión
# URL del video

def main():
    c = Scrapping()
    c.get_data()

if __name__ == '__main__':
    main()

# c.write()
# c.read(limit=3)