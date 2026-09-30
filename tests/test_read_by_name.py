import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from alphacast.alphacast import Alphacast


def response(body, status_code=200):
    r = MagicMock()
    r.ok = status_code < 400
    r.status_code = status_code
    r.content = json.dumps(body).encode()
    r.json.return_value = body
    return r


@patch("alphacast.alphacast.requests")
class TestReadByName(unittest.TestCase):
    """Issue #3235: read_by_name asks the API for one name instead of downloading the whole listing."""

    def setUp(self):
        self.alphacast = Alphacast("key")

    def test_dataset_lookup_sends_name_and_repository(self, requests):
        requests.get.return_value = response([{"id": 1, "name": "GDP", "repositoryId": 5}])

        dataset = self.alphacast.datasets.read_by_name("GDP", 5)

        self.assertEqual(dataset["id"], 1)
        self.assertTrue(requests.get.call_args[0][0].endswith("/datasets"))
        self.assertEqual(requests.get.call_args.kwargs["params"], {"name": "GDP", "repositoryId": 5})

    def test_dataset_lookup_without_repository_only_sends_name(self, requests):
        requests.get.return_value = response([])

        self.assertIsNone(self.alphacast.datasets.read_by_name("GDP"))
        self.assertEqual(requests.get.call_args.kwargs["params"], {"name": "GDP"})

    def test_repository_lookup_sends_name(self, requests):
        requests.get.return_value = response([{"id": 9, "name": "Macro"}])

        self.assertEqual(self.alphacast.repository.read_by_name("Macro")["id"], 9)
        self.assertTrue(requests.get.call_args[0][0].endswith("/repositories"))
        self.assertEqual(requests.get.call_args.kwargs["params"], {"name": "Macro"})

    def test_repository_lookup_returns_false_when_missing(self, requests):
        requests.get.return_value = response([])

        self.assertIs(self.alphacast.repository.read_by_name("Macro"), False)

    def test_get_raises_with_the_api_message(self, requests):
        requests.get.return_value = response({"message": "name must not be empty"}, 400)

        with self.assertRaisesRegex(Exception, "^400: name must not be empty$"):
            self.alphacast.datasets.read_by_name("")


@patch("alphacast.alphacast.requests")
class TestCreate(unittest.TestCase):

    def setUp(self):
        self.alphacast = Alphacast("key")

    def test_dataset_check_is_scoped_to_the_target_repository(self, requests):
        existing = {"id": 2, "name": "GDP", "repositoryId": 5}
        requests.get.return_value = response([existing])

        self.assertEqual(self.alphacast.datasets.create("GDP", 5, returnIdIfExists=True), existing)
        self.assertEqual(requests.get.call_args.kwargs["params"], {"name": "GDP", "repositoryId": 5})
        requests.post.assert_not_called()

    def test_dataset_raises_when_it_exists_and_the_id_is_not_requested(self, requests):
        requests.get.return_value = response([{"id": 2, "name": "GDP", "repositoryId": 5}])

        with self.assertRaisesRegex(ValueError, "Dataset already exists: 2"):
            self.alphacast.datasets.create("GDP", 5)
        requests.post.assert_not_called()

    def test_dataset_is_created_when_missing(self, requests):
        requests.get.return_value = response([])
        requests.post.return_value = response({"id": 3, "name": "GDP", "repositoryId": 5}, 201)

        self.assertEqual(self.alphacast.datasets.create("GDP", 5)["id"], 3)

    def test_dataset_raises_when_the_api_rejects_the_creation(self, requests):
        requests.get.return_value = response([])
        requests.post.return_value = response({"message": "Duplicate entry 'gdp-5'"}, 409)

        with self.assertRaisesRegex(Exception, "^409: Duplicate entry 'gdp-5'$"):
            self.alphacast.datasets.create("gdp", 5)

    def test_repository_raises_when_the_api_rejects_the_creation(self, requests):
        requests.get.return_value = response([])
        requests.post.return_value = response({"message": "Wrong team information"}, 400)

        with self.assertRaisesRegex(Exception, "^400: Wrong team information$"):
            self.alphacast.repository.create("Macro")


if __name__ == "__main__":
    unittest.main()
