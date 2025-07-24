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

class TestSeries(unittest.TestCase):

    def test_get_metadata_from_series_by_id(self):
        series = alphacast.series(53804).metadata()
        print(series)

    def test_download_series_data(self):
        data = alphacast.series(53804).download_data(format="json")
        self.assertIsNotNone(data)
        print(data)
        
        


