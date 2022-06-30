from urllib.parse import urlencode
import requests 
from requests.auth import HTTPBasicAuth 
import json
import pandas as pd
import io
#from dotenv import dotenv_values
#env_settings = dotenv_values(".env")


class Datasets():       
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
    
    

    def __init__(self, api_key):
        self.api_key = api_key

    def read_all(self):    
        url = "https://api.alphacast.io/datasets"
        r = requests.get(url, auth=HTTPBasicAuth(self.api_key, ""))
        return json.loads(r.content)
    
    def read_by_name(self, dataset_name, repo_id= None):
        url = "https://api.alphacast.io/datasets"
    
        r = requests.get(url, auth=HTTPBasicAuth(self.api_key, ""))
        dataset = None
        for element in json.loads(r.content):
            if (element["name"] == dataset_name) & ((element["repositoryId"] == repo_id) | (repo_id== None)):
                return element
            #print(element)
        return dataset

    def create(self, dataset_name, repo_id, description="", returnIdIfExists= False):
        url = "https://api.alphacast.io/datasets"
        form={
            "name": dataset_name, 
            "repositoryId": repo_id,
            "description": description
        }

        exists = self.read_by_name(dataset_name)
        if exists:
            if returnIdIfExists:
                return exists
            else:
                raise ValueError("Dataset already exists: {}".format(exists["id"]))

        dataset = requests.post(url, data=form, auth=HTTPBasicAuth(self.api_key, ""))
        return json.loads(dataset.content)

    def dataset(self, dataset_id):
        return self.Dataset(dataset_id, self.api_key)

    class Dataset():

        def __init__(self, dataset_id, api_key):            
            self.dataset_id = dataset_id
            self.api_key = api_key

        def metadata(self):
            url = "https://api.alphacast.io/datasets/{}".format(self.dataset_id)
            r = requests.get(url, auth=HTTPBasicAuth(self.api_key, ""))
            return json.loads(r.content)

        def get_column_definitions(self):
            columnsUrl = 'https://api.alphacast.io/datasets/{}/columns'.format(self.dataset_id)
            r = requests.get(columnsUrl, auth=HTTPBasicAuth(self.api_key, ""))
            return json.loads(r.content)["columnDefinitions"]

        def download_data(self, format="csv", startDate=None, endDate=None, filterVariables=[], filterEntities=[]):
            dateColumnName = "Date"
            allFilters = {}
            entityQueryFilter = ""

            if filterEntities:
                entityQueryParams = []

                for entity in filterEntities:
                    entityQuery = ' or '.join([f"{entity} eq '{value}'" for value in filterEntities[entity]])
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
            url = "https://api.alphacast.io/datasets/{}/data?{}&$format={}".format(self.dataset_id, queryString, return_format)
            r = requests.get(url, auth=HTTPBasicAuth(self.api_key, ""))

            if format == "json":
                return [json.loads(jline) for jline in r.content.splitlines()]
            elif format == "pandas":
                return pd.read_csv(io.StringIO(r.content.decode("UTF-8")))
            else:    
                return r.content
        
        def upload_data_from_df(self, df, deleteMissingFromDB = False, onConflictUpdateDB = False, uploadIndex=True):
            url = "https://api.alphacast.io/datasets/{}/data?deleteMissingFromDB={}&onConflictUpdateDB={}".format(self.dataset_id, deleteMissingFromDB, onConflictUpdateDB)
            files = {'data': df.to_csv(index=uploadIndex)}
            r = requests.put(url, files=files, auth=HTTPBasicAuth(self.api_key, ""))
            return r.content

        def upload_data_from_csv(self, csv, deleteMissingFromDB = False, onConflictUpdateDB = False, uploadIndex=True):
            url = "https://api.alphacast.io/datasets/{}/data?deleteMissingFromDB={}&onConflictUpdateDB={}".format(self.dataset_id, deleteMissingFromDB, onConflictUpdateDB)
            files = {'data': csv}
            r = requests.put(url, files=files, auth=HTTPBasicAuth(self.api_key, ""))
            return r.content

        def processes(self):
            url = "https://api.alphacast.io/datasets/{}/processes".format(self.dataset_id)
            r = requests.get(url, auth=HTTPBasicAuth(self.api_key, ""))
            return r.content   

        def process(self, process_id):
            url = "https://api.alphacast.io/datasets/{}/processes/{}".format(self.dataset_id, process_id)
            r = requests.get(url, auth=HTTPBasicAuth(self.api_key, ""))
            return r.content
        
        def datestats(self):
            url = "https://api.alphacast.io/datasets/{}/date-stats".format(self.dataset_id)
            r = requests.get(url, auth=HTTPBasicAuth(self.api_key, ""))
            return r.content

        def delete(self):
            url = "https://api.alphacast.io/datasets/{}".format(self.dataset_id)
            r = requests.delete(url, auth=HTTPBasicAuth(self.api_key, ""))
            return r.content

        def initialize_columns(self, dateColumnName, entitiesColumnNames, dateFormat):
            form_data = {
                "dateColumnName": dateColumnName,
                "entitiesColumnNames": entitiesColumnNames,
                "dateFormat": dateFormat,
                "content-type": "json"
                }
            url = "https://api.alphacast.io/datasets/{}/columns/initializer".format(self.dataset_id)
            r = requests.put(url, json=form_data, auth=HTTPBasicAuth(self.api_key, ""))
            rjson = r.json()

            if r.status_code == 403:
                if(rjson["message"]):
                    raise Exception(rjson["message"])     
                raise Exception('An error occurred')

            return r.content            




class Repository():   
    # Repository Class
    # 
    # Methods:
    # read_all()
    # read_by_id(dataset_id)
    # read_by_name(dataset_name, repo_id=None)
    # create(repo_name, repo_description=None, privacy="Private", slug=None, returnIdIfExists=False)

    def __init__(self, api_key):
        self.api_key = api_key

    def read_all(self):
        url = "https://api.alphacast.io/repositories"
        r = requests.get(url, auth=HTTPBasicAuth(self.api_key, ""))
        return json.loads(r.content)

    def read_by_id(self, repository_id):
            url = "https://api.alphacast.io/repositories/{}".format(repository_id)
            r = requests.get(url, auth=HTTPBasicAuth(self.api_key, ""))
            return json.loads(r.content)

    def read_by_name(self, repo_name):
        url = "https://api.alphacast.io/repositories"
        r = requests.get(url, auth=HTTPBasicAuth(self.api_key, ""))
        repos = json.loads(r.content)
        for element in repos:
            if (element["name"] == repo_name):
                return element
        return False

    def delete(self, repository_id):
        url = "https://api.alphacast.io/repositories/{}".format(repository_id)
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

        url = "https://api.alphacast.io/repositories"
        
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
        