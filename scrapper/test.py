import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime
import requests

from scrap import Scrapping


def read_mocked_file(file_name):
    path = Path(__file__).resolve().parent.parent / "data" / file_name
    with open(path) as f:
        return f.read()


class Test(unittest.TestCase):
    episode_1x1_summary = read_mocked_file("episode-1x1-summary.txt")
    api_url = "http://127.0.0.1:8000/episodes/"

    def setUp(self):
        self.scrapper = Scrapping()

    def test_scrap_init(self):
        self.assertEqual(
            self.scrapper.url, "https://simpsonizados.me/serie/los-simpson/"
        )
        self.assertEqual(self.scrapper._Scrapping__db, "simpson_db.json")

    @patch("scrap.requests.get")
    def test_scrap_get_data__successfully(self, mocked_request_get):
        # -- Arrange --
        mocked_request_get.side_effect = [
            MagicMock(text=read_mocked_file("page.html")),
            MagicMock(text=read_mocked_file("episode-1x1.html")),
            MagicMock(text=read_mocked_file("episode-1x2.html")),
            MagicMock(text=read_mocked_file("episode-2x1.html")),
        ]

        # -- Act --
        scrapped_episodes = self.scrapper.get_data()

        # -- Assert episode detail --
        self.assertNotEqual(len(scrapped_episodes), 0)

        first_episode_of_first_season = [
            episode for episode in scrapped_episodes if episode["number"] == 1
        ][0]
        date_str = "Dec. 17, 1989"
        date_datetime = datetime.strptime(date_str, "%b. %d, %Y")
        date_formated_str = date_datetime.strftime("%Y-%d-%m")
        self.assertEqual(first_episode_of_first_season["name"], "Sin blanca Navidad")
        self.assertEqual(first_episode_of_first_season["season_number"], 1)
        self.assertEqual(
            first_episode_of_first_season["release_date"], date_formated_str
        )
        self.assertEqual(
            first_episode_of_first_season["url"],
            "https://simpsonizados.me/capitulo/los-simpson-1x1/",
        )
        self.assertEqual(
            first_episode_of_first_season["summary"], self.episode_1x1_summary
        )

        # -- Assert episode list --
        self.assertEqual(
            {(1, 1), (1, 2), (2, 1)},
            {
                (episode["season_number"], episode["number"])
                for episode in scrapped_episodes
            },
        )

        # -- Assert service calls --
        self.assertEqual(mocked_request_get.call_count, 4)
        mocked_request_get.assert_any_call(
            "https://simpsonizados.me/serie/los-simpson/"
        )
        mocked_request_get.assert_any_call(
            "https://simpsonizados.me/capitulo/los-simpson-1x1/"
        )
        mocked_request_get.assert_any_call(
            "https://simpsonizados.me/capitulo/los-simpson-1x2/"
        )
        mocked_request_get.assert_any_call(
            "https://simpsonizados.me/capitulo/los-simpson-2x1/"
        )

    @patch("scrap.requests.get")
    def test_scrap_get_data__error_when_fetch_the_episodes_list(
        self, mocked_request_get
    ):
        # -- Arrange --
        mocked_request_get.return_value = lambda *args, **kwargs: 1 / 0

        # -- Act & Assert --
        with self.assertRaises(Exception):
            self.scrapper.get_data()

    @patch("scrap.requests.get")
    def test_scrap_get_data__error_when_fetch_the_episode_detail(
        self, mocked_request_get
    ):
        # -- Arrange --
        mocked_request_get.side_effect = [
            MagicMock(text=read_mocked_file("page.html")),
            MagicMock(text=read_mocked_file("episode-1x1.html")),
            lambda *args, **kwargs: 1 / 0,
            MagicMock(text=read_mocked_file("episode-2x1.html")),
        ]

        # -- Act --
        scrapped_episodes = self.scrapper.get_data()
        # -- Arrange --
        self.assertEqual(
            {(1, 1), (2, 1)},
            {
                (episode["season_number"], episode["number"])
                for episode in scrapped_episodes
            },
        )

    def test_api_request_success_when_app_running(self):
        episode_mock = {
            "release_date": "1991-22-08",
            "number": 16,
            "name": "El suspenso del perro de Bart",
            "season_number": 2,
            "url": "https://simpsonizados.me/capitulo/los-simpson-2x16/",
            "summary": "Después de varios destrozos y debido a su mala conducta, El Pequeño Ayudante de Santa Claus será vendido si no aprueba en la escuela canina.",
        }
        try:
            response = requests.get("http://localhost:8000/")
            self.assertEqual(response.status_code, 200)
            post_response = Scrapping.api_request(self, episode_mock)
            self.assertEqual(post_response.status_code, 200)
        except requests.exceptions.RequestException:
            self.fail("The app is not running")

    def test_api_request_error_when_app_not_running(self):
        try:
            response = requests.get("http://localhost:8000/")
            self.assertEqual(response.status_code, 200)
        except requests.exceptions.RequestException:
            self.fail("The app is not running")
