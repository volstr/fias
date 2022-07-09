import unittest
from typing import List, Dict

from starlette import status
from starlette.testclient import TestClient

from main import app


class ApiTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def _list_response(self, url: str) -> List:
        response = self.client.get(f'/api/{url}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ls = response.json()
        self.assertIsInstance(ls, list)

        return ls

    def _dict_response(self, url: str) -> Dict:
        response = self.client.get(f'/api/{url}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        obj = response.json()
        self.assertIsInstance(obj, dict)

        return obj

    def test_version(self):
        response = self.client.get('/api/version')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), dict)

    def test_levels(self):
        self._list_response('levels')

    def test_house_types(self):
        self._list_response('house_types')

    def test_apartment_types(self):
        self._list_response('apartment_types')

    def test_param_types(self):
        self._list_response('param_types')

    def test_address_types(self):
        self._list_response('address_types')

    def test_updates(self):
        self._list_response('updates')

    def test_object(self):
        response = self.client.get('/api/objects/object/test')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response.json(), dict)

    def test_find_by_kladr(self):
        response = self.client.get('/api/objects/find_by_kladr/kladr')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response.json(), dict)

    def test_adm_hierarchy(self):
        response = self.client.get('/api/objects/adm_hierarchy/test')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response.json(), dict)

    def test_mun_hierarchy(self):
        response = self.client.get('/api/objects/mun_hierarchy/test')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIsInstance(response.json(), dict)

    def test_find_adm_hierarchy(self):
        response = self.client.get('/api/objects/find/adm_hierarchy')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), dict)

    def test_find_mun_hierarchy(self):
        response = self.client.get('/api/objects/find/mun_hierarchy')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.json(), dict)
