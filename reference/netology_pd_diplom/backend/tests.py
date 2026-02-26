from django.urls import reverse
from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status


class ShopThrottleTestCase(APITestCase):

    def setUp(self):
        cache.clear()

    def test_anon_throttle_limit(self):
        url = reverse("backend:shops")

        responses = []

        for i in range(40):
            response = self.client.get(url)
            responses.append(response.status_code)

        print(responses)

        # Проверяем, что хотя бы один запрос дал 429
        self.assertIn(status.HTTP_429_TOO_MANY_REQUESTS, responses)