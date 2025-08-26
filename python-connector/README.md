# Asset Connector MQTT Python

This project provides a FastAPI-based connector for interfacing with assets using AID (Asset Interface Description) and MQTT. It allows dynamic configuration and value retrieval for assets described by AID submodels.

## Features
- Set configuration for assets via `/set-config` endpoint
- Retrieve values from assets via `/get-value/{id}` endpoint
- Thread-safe storage of asset connectors
- MQTT connection management and caching

## Requirements
- Python 3.11+
- MQTT broker
- Environment variables for MQTT credentials (optional):
  - `MQTT_USERNAME`
  - `MQTT_PASSWORD`

## Installation
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd asset-connector-mqtt-python
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Start the FastAPI server:
   ```bash
   python main.py
   ```
   Or with Uvicorn:
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8090
   ```
2. Use the `/set-config` endpoint to configure an asset. 

   An Asset Connector identifiable by the Submodel Id of the AID Submodel will be initialized. The AID JSON must be included in the POST body content like in the following definition:
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
         ...
      }
   }
   ```

3. Use the `/{id}/get-value` endpoint to retrieve values from the asset using a specific AID configuration. 

   The `{id}` prefix is equal to the base64-url encoded AID Submodel id, e.g. you enter `/aHR0cHM6Ly9mbHVpZDQwLmRlL2lkcy9zbS80NzU3XzQ4NTZfODQ2NF8xNDQx/get-value` for the AID used above (an Asset Connector must be initialized with `/set-config` first before you can use it!). 
   
   The POST body content must contain the ModelReference to one of the subscribed topics (e.g. axes_position) defined in the AID:
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

> [!TIP]
> You can also discover the endpoints and request body schemata using Swagger by adding `/docs` to the base url, e.g. `http://127.0.0.1:8090/docs`.

## Project Structure
- `main.py`: FastAPI application entry point
- `core/`: Core logic for AID parsing, MQTT connection, and reference resolution
- `models/`: Data models for payloads and responses
- `resources/`: Example JSON payloads

## License
MIT
