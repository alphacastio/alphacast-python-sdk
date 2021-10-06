# Alphacast Python Library

## Introduction

The Alphacast Python library allows you to interact with the assets hosted in Alphacast without the need to know the details of the API integration. In the current version you can interact with your repositories and datasets.

## Quick Start

Begin by installing Alphacast SDK in your console


```
    pip install alphacast
```

Then import the module in your screen and initialize the session with your API key. To find you API you need to have an Alphacast account (https://www.alphacast.io/api/auth/login). Once created, find your key in your settings (click on your user on the left menu) 


```
    from alphacast import Alphacast
    alphacast = Alphacast(YOUR_API_KEY)
```

## Repositories

All the interaction with your repositories are handled with the "repository" class. To read the metadata of all your repositories and those you have write permissions use repository.read_all()

```
    alphacast.repository.read_all()
```

To read the metadata of a single repository by id use read_by_id or read_by_name. You need to have owner, admin or write permissions to access the repo.

```
    alphacast.repository.read_by_id(repo_id)
    alphacast.repository.read_by_name(repo_name)
```

To create a repository you need to define its name, slug (optional), privacy (optional) and description (also optional). The parameter returnIdIfExists (True/False) is usen to describe the action when de repository already exists. If true, then it returns de Id.

```
    alphacast.repository.create("my first Test Repo", repo_description="This is my first Repo", slug="test-repo", privacy="Public", returnIdIfExists=True)
```

## Finding datasets

Finding and downloading data is at the core of Alphacast and is done with the "datasets" class.

To access the metadata of all your datasets (that is, those where you have owner, admin or write permission) use read_all() or read_by_name().

```
    alphacast.datasets.read_all()
    alphacast.datasets.read_by_name("dataset_name")
```
---
**NOTE** Only your dataset can be accessed with these methods. If you want to use public data you have to use the id which can be found in the url of the dataset in alphacast.io web.
---

With the id you can also access information of datasets where you have read permission (either because they are public or because you have been granted access) 

use the dataset(dataset_id).metadata() method to access the metadata.
---
alphacast.datasets.dataset(5565).metadata()
---

## Downloading data

alphacast.datasets.dataset(5565).data(format = "json")
pd.read_excel( alphacast.datasets.dataset(5565).data("xlsx"))
pd.read_csv( io.StringIO(alphacast.datasets.dataset(5565).data("csv").decode("UTF-8")))
alphacast.datasets.dataset(5565).data("pandas")

## Creating datasets and uploading data    
dataset().upload_data_from_df
dataset().upload_data_from_csv()