import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from scrap import Scrapping


def read_mocked_file(file_name):
    path = Path(__file__).parent / 'data' / file_name

    with open(path) as f:
        return f.read()


class Test(unittest.TestCase):
    episode_1x1_summary = read_mocked_file('episode-1x1-summary.txt')

    def setUp(self):
        self.scrapper = Scrapping()

    def test_scrap_init(self):
        self.assertEqual(self.scrapper.url, 'https://simpsonizados.me/serie/los-simpson/')
        self.assertEqual(self.scrapper._Scrapping__db, 'simpson_db.json')

    @patch('scrap.requests.get')
    def test_scrap_get_data__successfully(self, mocked_request_get):
        # -- Arrange --
        mocked_request_get.side_effect = [
            MagicMock(text=read_mocked_file('page.html')),
            MagicMock(text=read_mocked_file('episode-1x1.html')),
            MagicMock(text=read_mocked_file('episode-1x2.html')),
            MagicMock(text=read_mocked_file('episode-2x1.html')),
        ]

        # -- Act --
        scrapped_episodes = self.scrapper.get_data()

        # -- Assert episode detail --
        self.assertNotEqual(len(scrapped_episodes), 0)

        first_episode = scrapped_episodes[0]

        self.assertEqual(first_episode['Nro capitulo'], '1')
        self.assertEqual(first_episode['Nombre capitulo'], 'Sin blanca Navidad')
        self.assertEqual(first_episode['Temporada'], '1')
        self.assertEqual(first_episode['Fecha emision'], 'Dec. 17, 1989')
        self.assertEqual(first_episode['url'], 'https://simpsonizados.me/capitulo/los-simpson-1x1/')
        self.assertEqual(first_episode['Resumen'], self.episode_1x1_summary)

        # -- Assert episode list --
        self.assertEqual(
            {("1", "1"), ("1", "2"), ("2", "1")},
            {(episode['Temporada'], episode['Nro capitulo']) for episode in scrapped_episodes},
        )

        # -- Assert service calls --
        self.assertEqual(mocked_request_get.call_count, 4)
        mocked_request_get.assert_any_call('https://simpsonizados.me/serie/los-simpson/')
        mocked_request_get.assert_any_call('https://simpsonizados.me/capitulo/los-simpson-1x1/')
        mocked_request_get.assert_any_call('https://simpsonizados.me/capitulo/los-simpson-1x2/')
        mocked_request_get.assert_any_call('https://simpsonizados.me/capitulo/los-simpson-2x1/')

    @patch('scrap.requests.get')
    def test_scrap_get_data__error_when_fetch_the_episodes_list(self, mocked_request_get):
        # -- Arrange --
        mocked_request_get.return_value = lambda *args, **kwargs: 1 / 0

        # -- Act & Assert --
        with self.assertRaises(Exception):
            self.scrapper.get_data()

    @patch('scrap.requests.get')
    def test_scrap_get_data__error_when_fetch_the_episode_detail(self, mocked_request_get):
        # -- Arrange --
        mocked_request_get.side_effect = [
            MagicMock(text=read_mocked_file('page.html')),
            MagicMock(text=read_mocked_file('episode-1x1.html')),
            lambda *args, **kwargs: 1 / 0,
            MagicMock(text=read_mocked_file('episode-2x1.html')),
        ]

        # -- Act --
        scrapped_episodes = self.scrapper.get_data()

        # -- Arrange --
        self.assertEqual(
            {("1", "1"), ("2", "1")},
            {(episode['Temporada'], episode['Nro capitulo']) for episode in scrapped_episodes},
        )
