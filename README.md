# spccore
Synapse Python Client Core Package

 CI | Branch  | Build Status
 ---|---------|-------------
Travis | develop | [![Build Status develop branch](https://travis-ci.com/Sage-Bionetworks/spccore.svg?branch=develop)](https://travis-ci.com/Sage-Bionetworks/spccore)
Travis | master  | [![Build Status master branch](https://travis-ci.com/Sage-Bionetworks/spccore.svg?branch=master)](https://travis-ci.com/Sage-Bionetworks/spccore)
AppVeyor | develop | [![AppVeyor branch](https://img.shields.io/appveyor/ci/SageBionetworks/spccore/master.svg)](https://ci.appveyor.com/project/SageBionetworks/spccore)
AppVeyor | master | [![AppVeyor branch](https://img.shields.io/appveyor/ci/SageBionetworks/spccore/master.svg)](https://ci.appveyor.com/project/SageBionetworks/spccore)


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
