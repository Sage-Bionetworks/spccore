# spccore
Synapse Python Client Core Package

[![Build Status](https://travis-ci.com/Sage-Bionetworks/spccore.svg?branch=master)](https://travis-ci.com/Sage-Bionetworks/spccore)

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

synapse_base_client = spccore.get_base_client()
version = synapse_base_client.get("/version")

```
