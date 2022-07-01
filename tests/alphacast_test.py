import unittest
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
        
        dataset_proxy.delete()
        alphacast.repository.delete(repository["id"])
