============
API Reference
============

Alphacast API is organized around REST. Our API has predictable resource-oriented URLs, accepts form-encoded request bodies, returns JSON-encoded responses or CSV files, and uses standard HTTP response codes, authentication, and verbs.

All API requests must be authenticated. Please refer to :ref:`authentication`.

Authentication
-------

Alphacast API uses API keys to authenticate requests. You can contact hello@alphacast.io to get one. 

Make sure you keep your API secure. Do not share your secret API keys in publicly accessible areas such as GitHub, client-side code, and so forth.

Authentication to the API is performed via HTTP Basic Auth. Provide your API key as the basic auth username value. You do not need to provide a password.

::

  $curl https://charts.alphacast.io/api/datasets -u ak_somesomplekey:
  # The colon prevents curl from asking for a password.

All API requests must be made over HTTPS. Calls made over plain HTTP will fail. API requests without authentication will also fail.


Datasets
-------

Provides a JSON representation of all Datasets available under the user's account::

  GET https://charts.alphacast.io/api/datasets
  
  $curl https://charts.alphacast.io/api/datasets -u ak_somesamplekey:
  # The colon prevents curl from asking for a password.

Response
  
  .. code-block:: JSON

    [{
      "id": 5190,"name":"Inflation - Latin America - Inflation Explorer"
      },
      {
      "id": 5283,"name":"Monetary - Argentina - BCRA - SERIESE y BAS_Long"
    }]

Dataset CSV download
^^^^^
Allows to download all available data for a given Dataset id::

  GET https://charts.alphacast.io/api/datasets/5265.csv
  
  $curl https://charts.alphacast.io/api/datasets/5265.csv -u ak_somesamplekey:
  # The colon prevents curl from asking for a password.
  
Response
  
  .. code-block:: CSV

    Entity,Year,Public Image - Very good,Public Image - Good,Public Image - Regular,Public Image - Bad,Public Image - Very bad,Public Image - Net,Public Image - Positive,Public Image - Negative,Public Image - Net - Frente Amplio,Public Image - Net - Partido Nacional,Public Image - Net - Partido Colorado,Public Image - Net - Cabildo Abierto
    Beatriz Argimón,43830,0.17,0.28,0.26,0.16,0.1,0.19,0.46,0.27,-0.32,0.78,0.61,0.57
    Beatriz Argimón,43890,0.2,0.27,0.27,0.14,0.09,0.25,0.49,0.23,-0.27,0.81,0.4,0.71
    Beatriz Argimón,43951,0.16,0.32,0.28,0.11,0.08,0.29,0.5,0.2,-0.18,0.73,0.78,0.67
    Beatriz Argimón,44074,0.09,0.25,0.26,0.18,0.15,0,0.36,0.36,-0.51,0.61,0.54,0.38

Charts
-------
Coming soon

Entities
-------
Coming soon

Countries
-------
Coming soon

Variables
-------
Coming soon
