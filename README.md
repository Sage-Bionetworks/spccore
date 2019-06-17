# spccore
Synapse Python Client Core Package

## Overview

The Synapse Python Client Core package:
* Creates and manages a connection to the Synapse server
* Manages user credentials including `username` and `api_key`
* Provides simple APIs for upload and download data to/from Synapse
* Provides simple APIs for making HTTP GET/PUT/POST/DELETE requests
* Handles Synapse HTTP errors

## Usage

```python

import spccore

synapse_connection = spccore.get_connection()
version = synapse_connection.get("/version")

```
