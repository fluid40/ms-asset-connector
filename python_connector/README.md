# Asset Connector MQTT Python

This project provides a FastAPI-based connector for interfacing with assets using AID (Asset Interface Description).
It allows dynamic configuration and value retrieval for assets described by AID submodels.


## Features
- Set configuration for assets via `/add-config` endpoint
- Retrieve values from assets via `/get-value` endpoint
- Write values at assets via `/set-value` endpoint
- Thread-safe storage of asset connections


## Requirements
- Python 3.11+


## Installation
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd asset-connector
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Start

1. Start the FastAPI server (from the base directory `asset-connector`):
   ```bash
   python cli.py
   ```
   
2. Or use docker
   ```bash
   docker build -t localhost/asset-connector:latest . && docker run -p 8000:8000 localhost/asset-connector:latest
   ```


## Usage

1. Use the `/add-config` endpoint to configure an asset. 
   A Connector responsible for this asset will be initialized based on the details in the AID submodel.
   The AID JSON must be included in the POST body content like in the following definition:

   ```json
   {
      "Aid": {
         <AID Submodel JSON>
      }
   }
   ```

   Example:
   ```json
   {
      "Aid": {
         "idShort": "AssetInterfacesDescription",
         "description": [
            {
            "language": "en",
            "text": "AID Sample"
            }
         ],
         "id": "https://fluid40.de/ids/sm/4757_4856_8464_1441",
         // ...
      }
   }
   ```

2. Use the `/get-value` endpoint to retrieve values from the asset using a specific AID configuration.
   A Connector must be initialized with `/add-config` first before you can use it!
   The POST body content must contain the ModelReference to one of the _properties_ (endpoints) defined in the AID.
   ```json
   {
      "Reference": {
         <ModelReference JSON>
      }
   }
   ```

   Example:
   ```json
   {
      "Reference": {
         "type": "ModelReference",
         "keys": [
            {
               "type": "Submodel",
               "value": "https://fluid40.de/ids/sm/4757_4856_8464_1441"
            },
            {
               "type": "SubmodelElementCollection",
               "value": "Interface_MQTT"
            },
            {
               "type": "SubmodelElementCollection",
               "value": "InteractionMetadata"
            },
            {
               "type": "SubmodelElementCollection",
               "value": "properties"
            },
            {
               "type": "SubmodelElementCollection",
               "value": "axes_position"
            }
         ]
      }
   }
   ```
   
3. Use the `/set-value` endpoint to set values at the asset using a specific AID configuration.
   A Connector must be initialized with `/add-config` first before you can use it!
   The POST body content must contain the ModelReference to one of the _properties_
   (endpoints) defined in the AID and the new data.
   ```json
   {
      "Reference": {
         <ModelReference JSON>
      },
      "Value": "..."
   }
   ```

   Example:
   ```json
   {
      "Reference": {
         "type": "ModelReference",
         "keys": [
            {
               "type": "Submodel",
               "value": "https://fluid40.de/ids/sm/4757_4856_8464_1441"
            },
            {
               "type": "SubmodelElementCollection",
               "value": "Interface_MQTT"
            },
            {
               "type": "SubmodelElementCollection",
               "value": "InteractionMetadata"
            },
            {
               "type": "SubmodelElementCollection",
               "value": "properties"
            },
            {
               "type": "SubmodelElementCollection",
               "value": "axes_position"
            }
         ]
      },
      "Value": "new-value"
   }
   ```

> [!TIP]
> You can also discover the endpoints and request body schemata using Swagger by adding `/docs` to the base url, e.g., [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs).

> [!TIP]
> The provided AID Submodels serve as the only means of configuration for the Asset Connector.
> You thus have to make sure that the asset endpoints are reachable from this microservice.
> If the service runs containerized,
> having a base address like `http://localhost` in an AID will most probably fail
> since it points to the container itself.

# Project Structure
- `main.py`: FastAPI application entry point
- `core/`: Core logic for AID parsing and reference resolution
- `models/`: Data models for payloads and responses
- `requests/`: Example JSON payloads
- `mqtt`, `opc_ua`, `http_connector`: Protocol-specific implementations of the communication logic

# License
MIT
