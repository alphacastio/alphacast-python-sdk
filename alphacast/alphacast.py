import gzip
from urllib.parse import urlencode
import requests 
from requests.auth import HTTPBasicAuth 
import json
import pandas as pd
import io
from typing import List

BASE_URL = "https://api.alphacast.io"

class Base():
    def __init__(self, api_key):
        self.api_key = api_key

    def _get(self, path):
        url = f"{BASE_URL}{path}"
        r = requests.get(url, auth=HTTPBasicAuth(self.api_key, ""))

        if not r.ok:
            try:
                rjson = r.json()
                if rjson.get("message"):
                    raise Exception(f"{r.status_code}: {rjson['message']}")
            except:
                pass
            raise Exception(f'API failed with status code {r.status_code}')

        return r


class Datasets(Base):       
    # Dataset Class
    # 
    # Methods:
    # read_all()
    # read_by_id(dataset_id)
    # read_by_name(dataset_name, repo_id=None)
    # create_dataset(self, dataset_name, repo_id, description):
    # dataset().metadata
    # dataset().download_data
    # dataset().upload_data_from_df
    # dataset().upload_data_from_csv()
    # dataset().processes()
    # dataset().process(process_id)
    # dataset().datestats
    # dataset().initialize_columns(dateColumnName, entitiesColumnNames, dateFormat)
    
    def read_all(self):    
        r = self._get("/datasets")
        return json.loads(r.content)
    
    def read_by_name(self, dataset_name, repo_id= None):

        r = self._get("/datasets")
        dataset = None
        for element in json.loads(r.content):
            if (element["name"] == dataset_name) & ((element["repositoryId"] == repo_id) | (repo_id== None)):
                return element
            #print(element)
        return dataset

    def create(self, dataset_name, repo_id, description="", returnIdIfExists= False):
        url = f"{BASE_URL}/datasets"
        form={
            "name": dataset_name, 
            "repositoryId": repo_id,
            "description": description
        }

        previous_dataset = self.read_by_name(dataset_name)
        if previous_dataset and previous_dataset['repositoryId'] == repo_id:
            if returnIdIfExists:
                return previous_dataset
            else:
                raise ValueError("Dataset already exists: {}".format(previous_dataset["id"]))

        dataset = requests.post(url, data=form, auth=HTTPBasicAuth(self.api_key, ""))
        return json.loads(dataset.content)

    def dataset(self, dataset_id):
        return self.Dataset(dataset_id, self.api_key)

    class Dataset(Base):

        def __init__(self, dataset_id, api_key):            
            super().__init__(api_key)
            self.dataset_id = dataset_id

        def metadata(self):
            r = self._get(f"/datasets/{self.dataset_id}")
            return json.loads(r.content)

        def get_column_definitions(self):
            r = self._get(f"/datasets/{self.dataset_id}/columns")
            return json.loads(r.content)["columnDefinitions"]

        def download_data(self, format="csv", startDate=None, endDate=None, filterVariables=[], filterEntities=[]):
            dateColumnName = "Date"
            allFilters = {}
            entityQueryFilter = ""

            if filterEntities:
                entityQueryParams = []

                for entity in filterEntities:
                    entityQuery = ' or '.join([f"'{entity}' eq '{value}'" for value in filterEntities[entity]])
                    entityQueryParams.append(f"({entityQuery})") 

                entityQueryFilter = ' and '.join(entityQueryParams)
            
            dateFilters = []
            if (startDate or endDate):
                columns = self.get_column_definitions()
                dateColumnName = [c["sourceName"] for c in columns if "dataType" in c and c["dataType"]=="Date"].pop()

                if (startDate):
                    dateFilters.append(f"'{dateColumnName}' ge {startDate.isoformat()}")

                if (endDate):
                    dateFilters.append(f"'{dateColumnName}' le {endDate.isoformat()}")

            dateFilter = (' and ' if startDate and endDate else '').join(dateFilters)
            dateAndEntityFilter = (' and ' if dateFilter and entityQueryFilter else '').join([dateFilter, entityQueryFilter])

            if (startDate or endDate or filterEntities):
                allFilters["$filter"] = dateAndEntityFilter
            
            if(len(filterVariables)):
                allFilters["$select"] = ",".join(filterVariables)

            queryString = urlencode(allFilters)

            if(queryString):
                queryString = f"&{queryString}"

            #formats ["csv", "tsv", "xlsx", "json"]            
            return_format = format
            if format == "pandas": return_format = "csv"

            r = self._get(f"/datasets/{self.dataset_id}/data?{queryString}&$format={return_format}")

            if format == "json":
                return [json.loads(jline) for jline in r.content.splitlines()]
            elif format == "pandas":
                return pd.read_csv(io.StringIO(r.content.decode("UTF-8")))
            else:    
                return r.content
        
        def upload_data_from_df(self, df, 
                deleteMissingFromDB = False, onConflictUpdateDB = False, uploadIndex=True,
                dateColumnName: str = None, dateFormat: str = None, entitiesColumnNames: List[str] = None, stringColumnNames: List[str] = None, acceptNewColumns: bool = None):
            if df.empty:
                raise "Dataframe is empty."
            return self.upload_data_from_csv(df.to_csv(index=uploadIndex), deleteMissingFromDB, onConflictUpdateDB, dateColumnName, dateFormat, entitiesColumnNames, stringColumnNames, acceptNewColumns )

        def upload_data_from_csv(self, csv, 
                deleteMissingFromDB = False, onConflictUpdateDB = False, 
                dateColumnName: str = None, dateFormat: str = None, entitiesColumnNames: List[str] = None, stringColumnNames: List[str] = None, acceptNewColumns: bool = None):

            initializer = None
            if (dateColumnName and dateFormat) or entitiesColumnNames or stringColumnNames:
                manifest = []
                if dateColumnName and dateFormat:
                    manifest.append({
                        "sourceName": dateColumnName,
                        "isEntity": True,
                        "dataType": "Date",
                        "dateFormat": dateFormat
                    })
                if entitiesColumnNames:
                    manifest += [
                        {
                            "sourceName": c,
                            "isEntity": True,
                            "dataType": "String"
                        } for c in entitiesColumnNames
                    ]
                if stringColumnNames:
                    manifest += [
                        {
                            "sourceName": c,
                            "isEntity": False,
                            "dataType": "String"
                        } for c in stringColumnNames
                    ]
                
                initializer = { "manifest": json.dumps(manifest) }
                
            url = f"{BASE_URL}/datasets/{self.dataset_id}/data?deleteMissingFromDB={deleteMissingFromDB}&onConflictUpdateDB={onConflictUpdateDB}"
            if acceptNewColumns:
                url += f"&acceptNewColumns={acceptNewColumns}"
            
            with io.BytesIO() as bio:
                with gzip.GzipFile(mode='w', fileobj=bio) as gz:
                    gz.write(csv.encode('utf-8'))

                bio.seek(0)
                    
                files = {'data': ('data.csv.gz', bio.getvalue())}
            r = requests.put(url, files=files, data=initializer, auth=HTTPBasicAuth(self.api_key, ""))
            return r.content

        def processes(self):
            r = self._get(f"/datasets/{self.dataset_id}/processes")
            return r.content   

        def process(self, process_id):
            r = self._get(f"/datasets/{self.dataset_id}/processes/{process_id}")
            return r.content
        
        def datestats(self):
            r = self._get(f"/datasets/{self.dataset_id}/date-stats")
            return r.content

        def delete(self):
            url = f"{BASE_URL}/datasets/{self.dataset_id}"
            r = requests.delete(url, auth=HTTPBasicAuth(self.api_key, ""))
            return r.content

        def initialize_columns(self, dateColumnName, entitiesColumnNames, dateFormat):
            form_data = {
                "dateColumnName": dateColumnName,
                "entitiesColumnNames": entitiesColumnNames,
                "dateFormat": dateFormat,
                "content-type": "json"
                }
            url = f"{BASE_URL}/datasets/{self.dataset_id}/columns/initializer"
            r = requests.put(url, json=form_data, auth=HTTPBasicAuth(self.api_key, ""))
            rjson = r.json()

            if r.status_code == 403:
                if(rjson["message"]):
                    raise Exception(rjson["message"])     
                raise Exception('An error occurred')

            return r.content            

        def run_connector(self, executionParam):
            url = f"{BASE_URL}/datasets/{self.dataset_id}/connector/runs"
            form={
                "executionParam": executionParam,
            }
            post = requests.post(url, data=form, auth=HTTPBasicAuth(self.api_key, ""))
            return json.loads(post.content)

        def get_connector_run(self, runId):
            r = self._get(f"/datasets/{self.dataset_id}/connector/runs/{runId}")
            return r.content   


class Repository(Base):   
    # Repository Class
    # 
    # Methods:
    # read_all()
    # read_by_id(dataset_id)
    # read_by_name(dataset_name, repo_id=None)
    # create(repo_name, repo_description=None, privacy="Private", slug=None, returnIdIfExists=False)

    def read_all(self):
        r = self._get("/repositories")
        return json.loads(r.content)

    def read_by_id(self, repository_id):
        r = self._get(f"/repositories/{repository_id}")
        return json.loads(r.content)

    def read_by_name(self, repo_name):
        repos = self.read_all()
        for element in repos:
            if (element["name"] == repo_name):
                return element
        return False

    def delete(self, repository_id):
        url = f"{BASE_URL}/repositories/{repository_id}"
        r = requests.delete(url, auth=HTTPBasicAuth(self.api_key, ""))
        return r.content

    def create(self, repo_name, repo_description=None, privacy="Private", slug=None, returnIdIfExists=False):
        if not slug:
            slug = repo_name.lower().replace(" ", "-")
        if not repo_description:
            repo_description = repo_name
        
        exists = self.read_by_name(repo_name)
        if exists:
            if returnIdIfExists:
                return exists
            else:
                raise ValueError("Repository already exists: {}".format(exists["id"]))

        url = f"{BASE_URL}/repositories"
        
        form={
            "name": repo_name,
            "description": repo_description,
            "privacy": privacy,
            "slug": slug    
        }

        return json.loads(requests.post(url, data=form, auth=HTTPBasicAuth(self.api_key, "")).content)

class Alphacast():   
    # Alphacast Class(api_key)
    # 
    # Methods:
    # repository
    # dataset

    def __init__(self, api_key):
        self.api_key = api_key
        self.repository = Repository(self.api_key) 
        self.datasets = Datasets(self.api_key)    
        