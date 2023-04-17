from django.test import TestCase
from scrapper.models import Episode
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.reverse import reverse
from datetime import datetime

# Create your tests here.


class EpisodeTestCase(TestCase):
    episode1 = {
        "release_date": datetime.strptime("1990-25-02", "%Y-%d-%m"),
        "number": 8,
        "name": "La cabeza chiflada",
        "season_number": 1,
        "url": "https://simpsonizados.me/capitulo/los-simpson-1x8/",
        "summary": "Bart se convierte en amigo de Dolph, Jimbo y Kearney, un grupo de alborotadores locales. Tratando de impresionarlos, Bart decide cortar y robar la cabeza de la estatua de Jebediah Springfield. Al día siguiente, toda la ciudad llora por la estatua en objeto de actos de vandalismo y Bart descubre que sus nuevos amigos quieren atacar al vándalo. Esto le produce una sensación de remordimiento, luego, Bart confiesa esto a su familia y Homer y Bart retornan la cabeza hacia la estatua.",
    }
    episode2 = {
        "release_date": datetime.strptime("1991-22-08", "%Y-%d-%m"),
        "number": 16,
        "name": "El suspenso del perro de Bart",
        "season_number": 2,
        "url": "https://simpsonizados.me/capitulo/los-simpson-2x16/",
        "summary": "Después de varios destrozos y debido a su mala conducta, El Pequeño Ayudante de Santa Claus será vendido si no aprueba en la escuela canina.",
    }

    def get_url(self, random: bool = False, params=None):
        url = reverse("episode-list", request=self.request)
        if random:
            url = reverse("episode-random", request=self.request)

        if params is not None:
            url += f"?{params}"

        return url

    def setUp(self):
        self.request = APIRequestFactory().get("/")
        self.client = APIClient()
        Episode.objects.create(**self.episode1)
        Episode.objects.create(**self.episode2)

    def test_get_episode(self):
        url = self.get_url()
        episode = self.client.get(url)
        self.assertEqual(episode.status_code, status.HTTP_200_OK)
        self.assertEqual(len(episode.data["results"]), 2)
        self.assertEqual(episode.data["results"][0]["number"], 8)
        self.assertEqual(episode.data["results"][0]["season_number"], 1)
        self.assertEqual(episode.data["results"][0]["name"], "La cabeza chiflada")
        self.assertEqual(episode.data["results"][0]["release_date"], "1990-25-02")
        self.assertEqual(
            episode.data["results"][0]["url"],
            "https://simpsonizados.me/capitulo/los-simpson-1x8/",
        )
        self.assertEqual(episode.data["results"][0]["release_date"], "1990-25-02")
        self.assertEqual(
            episode.data["results"][0]["summary"],
            "Bart se convierte en amigo de Dolph, Jimbo y Kearney, un grupo de alborotadores locales. Tratando de impresionarlos, Bart decide cortar y robar la cabeza de la estatua de Jebediah Springfield. Al día siguiente, toda la ciudad llora por la estatua en objeto de actos de vandalismo y Bart descubre que sus nuevos amigos quieren atacar al vándalo. Esto le produce una sensación de remordimiento, luego, Bart confiesa esto a su familia y Homer y Bart retornan la cabeza hacia la estatua.",
        )

    def test_get_episode_per_season(self):
        url = self.get_url(params="season=1")
        episode = self.client.get(url)
        self.assertEqual(episode.status_code, status.HTTP_200_OK)
        self.assertEqual(episode.data[0]["season_number"], 1)

    def test_get_episode_per_season_when_not_passing_query(self):
        url = self.get_url(params="season")
        episode = self.client.get(url)
        self.assertEqual(episode.status_code, status.HTTP_200_OK)
        self.assertEqual(episode.data["count"], 2)

    def test_create_episode(self):
        data = {
            "release_date": "1990-13-05",
            "number": 13,
            "name": "La babysitter ataca de nuevo",
            "season_number": 1,
            "url": "https://simpsonizados.me/capitulo/los-simpson-1x13/",
            "summary": "Marge se siente poco apreciada por parte de Homer, lo cual la motiva a hacer una llamada a una emisora de radio terapeuta, la cual Homer escucha con desilución. Homer, buscando llegar al corazón de Marge, decide darle una cena en un restaurante de lujo y contrata a una niñera para cuidar de Bart y Lisa. Le envían a la Sra. Botz, la cual Bart y Lisa pronto descubrirán que es en realidad una ladrona apodada “la niñera Bandit”. Ellos son capturados por la Sra. Botz, pero con el tiempo son liberados por Maggie. Bart y Lisa capturan a la Sra. Botz y llaman a la policía. Mientras tanto, Marge y Homer vuelven a casa y encuentran a la Sra. Botz atada. Homer desconocen su verdadera identidad, la libera y la Sra Botz hace un intento de huida justo antes de que la policía le frustre. Estrella invitada: Penny Marshall.",
        }
        url = self.get_url()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Episode.objects.count(), 3)
        self.assertEqual(response.data["name"], "La babysitter ataca de nuevo")

    def test_update_episode_fields_if_episode_exist(self):
        data = {
            "release_date": "1990-25-02",
            "number": 10000,
            "name": "La cabeza chiflada",
            "season_number": 1,
            "url": "https://simpsonizados.me/capitulo/los-simpson-1x1000/",
            "summary": "Episodio Actualizado Test",
        }
        url = self.get_url()
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Episode.objects.count(), 2)
        self.assertEqual(response.data["name"], self.episode1["name"])
        self.assertNotEqual(response.data["number"], self.episode1["number"])

    def test_random_episode(self):
        url = self.get_url(random=True)
        episode = self.client.get(url)
        self.assertIsInstance(episode.data, dict)

    def test_random_episode_passing_query_season_param(self):
        url = self.get_url(random=True, params="season=2")
        episode = self.client.get(url)
        self.assertIsInstance(episode.data, dict)
        self.assertEqual(episode.data["season_number"], 2)

    def test_create_episode_error_when_not_passing_all_properties(self):
        data = {
            "release_date": "1990-13-05",
            "name": "La babysitter ataca de nuevo",
            "season_number": 1,
            "url": "https://simpsonizados.me/capitulo/los-simpson-1x13/",
        }
        url = self.get_url()
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Episode.objects.count(), 2)

    def test_get_episode_per_season_when_season_do_not_exist(self):
        url = self.get_url(params="season=90")
        episode = self.client.get(url)
        self.assertEqual(episode.status_code, status.HTTP_400_BAD_REQUEST)

    def test_random_episode_when_season_do_not_exist(self):
        url = self.get_url(random=True, params="season=90")
        episode = self.client.get(url)
        self.assertEqual(episode.status_code, status.HTTP_400_BAD_REQUEST)
