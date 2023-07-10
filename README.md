
--------------------------------------

# Connect by Credo AI - Utility Module for Connecting to AI Governance Platform

Connect is a utility module that integrates ML assessments with the Credo AI Governance Platform.
Connect defines `evidence_containers` which function as adapters between diverse AI assessment
frameworks (or custom analyses) and Credo AI-compatible `Evidence` objects.



## Dependencies

- Credo AI Connect supports Python 3.8+
- Sphinx (optional for local docs site)


## Installation

The latest stable release (and required dependencies) can be installed from PyPI.

```
pip install credoai-connect
```

## Documentation

Documentation is hosted by [readthedocs](https://credoai-connect.readthedocs.io/en/stable/).


## Logging
Logging defaults to stdout. In order to collect all logging information into a specific file,
set the desired location to the environment variable `CREDO_CONNECT_LOG_PATH`. 



> **Warning**
> Make sure the destination has write permissions, otherwise you will get a `PermissionError` at the moment you
> attempt library import.
