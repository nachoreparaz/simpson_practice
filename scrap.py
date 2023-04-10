import requests
from bs4 import BeautifulSoup
import json

class Scrapping():
    
    def __init__(self):
      self.url = 'https://simpsonizados.me/serie/los-simpson/'
      self.__db = 'simpson_db.json'

    def get_data(self):
      req = requests.get(self.url)
      page = req.text
      soup = BeautifulSoup(page, 'lxml')
      all_episodes = soup.find_all('ul', class_='episodios')
      result = []
      temp = 1
      for i in range(0, len(all_episodes)):
          print('Realizando temporada: ', temp)
          ep_count = 1
          for j in range(1, len(all_episodes[i]) + 1):
              class_name = 'mark-' + str(j)
              episode = all_episodes[i].find('li', class_ = class_name)
              if not episode:
                continue
              dicc = {
                'Nro capitulo': episode.find('div', class_ = 'numerando').get_text().split('-')[1].strip(),
                'Nombre capitulo': ' '.join(episode.find('a').get_text().split()),
                'Temporada': episode.find('div', class_ = 'numerando').get_text().split('-')[0].strip(),
                'Fecha emision': episode.find('span', class_ = 'date').get_text(),
                'url': episode.find('a')['href']
              }
              print(dicc)
              try:
                get_resumen = requests.get(dicc['url'])
                resumen_txt = get_resumen.text
                resumen_soup = BeautifulSoup(resumen_txt, 'lxml')
                description = resumen_soup.find('p').get_text()
                dicc['Resumen'] = description
                result.append(dicc)
              except Exception as e:
                print('Error al obtener el resumen del capítulo')
              else:
                print('Episodio nro ', ep_count, ' realizado')
              finally:
                ep_count += 1
          temp +=1
        
      return result
    
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