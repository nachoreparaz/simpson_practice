import unittest
from django.test import Client
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime
import requests
import json

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
        self.client = Client()

    def test_scrap_init(self):
        self.assertEqual(
            self.scrapper.url, "https://simpsonizados.me/serie/los-simpson/"
        )
        self.assertEqual(self.scrapper._Scrapping__db, "simpson_db.json")

    @patch("scrap.requests.post")
    def test_scrap_get_data__successfully(self, mock_post):
        extracted_episode = {
            "number": 1,
            "name": "Sin blanca Navidad",
            "season_number": 1,
            "release_date": "1978-15-05",
            "url": "https://simpsonizados.me/capitulo/los-simpson-1x1/",
            "summary": "",
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        for _ in range(3):
            self.scrapper.api_request(extracted_episode)
        assert mock_post.call_count == 3

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

    @patch("scrap.requests.post")
    def test_api_request_error_when_not_passing_aruments(self, mock_post):
        with self.assertRaises(TypeError):
            self.scrapper.api_request()
