import unittest
import os
import sys

local_module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'alphacast'))
sys.path.insert(0, local_module_path)

from alphacast import Alphacast
import pandas as pd

from dotenv import dotenv_values

env_settings = dotenv_values(".env")

API_KEY = env_settings.get("API_KEY")

alphacast = Alphacast(API_KEY)

class TestDatasets(unittest.TestCase):

    def test_get_all_datasets(self):
        datasets = alphacast.datasets.read_all()
        self.assertGreater(len(datasets), 0)

    def test_upload_changes_manifest(self):
        repository = alphacast.repository.create("Test Repo", "Test Repo", "Private", "test", returnIdIfExists=True)
        dataset = alphacast.datasets.create("Test", repository["id"], "Test")
        dataset_proxy = alphacast.datasets.dataset(dataset["id"])

        df = pd.DataFrame({
            'Date': ['2022-01-01', '2022-01-02', '2022-01-03'],
            'Country': ['USA', 'France', 'Spain'],
            'Population': [230000, 42200, 242200],
            'Language': ['English', 'French', 'Spanish'],
        })

        process = dataset_proxy.upload_data_from_df(df, dateColumnName='Date', dateFormat='%Y-%m-%d', entitiesColumnNames=['Country'], stringColumnNames=['Language'])
        self.assertIsNotNone(process) 

        df = pd.DataFrame({
            'Date': ['2022-01-01', '2022-01-02', '2022-01-03'],
            'Country': ['USA', 'France', 'Spain'],
            'Population': [230000, 42200, 242200],
            'Language': ['English', 'French', 'Spanish'],
            'Income': [30000, 2200, 42200],
        })

        process = dataset_proxy.upload_data_from_df(df, uploadIndex=False, dateColumnName='Date', dateFormat='%Y-%m-%d', entitiesColumnNames=['Country'], stringColumnNames=['Language'], acceptNewColumns=True)
        self.assertIsNotNone(process) 

        dataset_proxy.delete()
        alphacast.repository.delete(repository["id"])

class TestSearch(unittest.TestCase):

    def test_search_datasets_returns_results(self):
        result = alphacast.search.datasets("GDP")
        self.assertIn("data", result)
        self.assertIsInstance(result["data"], list)
        self.assertGreater(len(result["data"]), 0)

    def test_search_datasets_pagination(self):
        page1 = alphacast.search.datasets("inflation", offset=0, length=3)
        page2 = alphacast.search.datasets("inflation", offset=3, length=3)
        self.assertEqual(len(page1["data"]), 3)
        ids_page1 = [h["id"] for h in page1["data"]]
        ids_page2 = [h["id"] for h in page2["data"]]
        self.assertEqual(len(set(ids_page1) & set(ids_page2)), 0)

    def test_search_datasets_exclude_deprecated(self):
        result = alphacast.search.datasets("GDP", exclude_deprecated=True)
        self.assertIn("data", result)


class TestSeries(unittest.TestCase):

    def test_get_metadata_from_series_by_id(self):
        series = alphacast.series(53804).metadata()
        print(series)

    def test_download_series_data(self):
        data = alphacast.series(53804).download_data(format="json")
        self.assertIsNotNone(data)
        print(data)
        
        


