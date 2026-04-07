# Asset Connector based on the AID Submodel

The purpose of this microservice is to connect to industrial assets (e.g., a machine, motor, sensor, etc.),
retrieve data, and even write data.
The connection to the asset can be established using a range of protocols including MQTT, HTTP, and OPC UA.
The details of the connection, i.e., base URL for the OPC UA server or MQTT broker,
are provided in an interoperabel way using the [AID submodel](https://industrialdigitaltwin.org/en/wp-content/uploads/sites/2/2024/01/IDTA-02017-1-0_Submodel_Asset-Interfaces-Description.pdf) (Asset Interfaces Description) standardized by the [IDTA](https://industrialdigitaltwin.org/en/content-hub/submodels).

An AID can specify one or more interfaces of an asset exposed via various protocols.
Each of these interfaces has one or more so-called _properties_.
These are communication _endpoints_ (e.g., MQTT topics, HTTP URLs, OPC UA nodes) that can be accessed to read/write data.

This microservice offers HTTP endpoints as well so that other services and users can interact with it.
These are:

**Add Config**
- configure the microservice with an additional AID submodel (it can handle multiple at once)
- endpoint: `/add-config`


**Get Value**
- retrieve the value of a _property_ (read from a communication _endpoint_ of an asset)
- endpoint: `/get-value`


**Set Value**
- set the value of a _property_ (write to a communication _endpoint_ of an asset)
- endpoint: `/set-value`


# Documentation

Project setup and usage: [`python_connector/README.md`](./python_connector/README.md)

Code documentation (Doxygen): []()
