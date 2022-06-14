# boolesches-ir-system

> **_NOTE:_** Before starting the application make configuration inside [configuration.py](configuration.py)

Start with `python run.py` and follow the instructions.

Alternatively with docker:
`docker build -t boolean_inr_system .`
`docker run -it boolean_inr_system`


## run some testing 

`pip install -r requirements.txt`

test with  `pytest .\tests\test_indexer.py`

https://hub.docker.com/r/mxibbls/inr

## Evaluation 

1. Creating the index takes on average 3.5 seconds.
2. Query runtimes:
   1. `blood`: 0.0 seconds
   2. `blood AND pressure`: 0.001 seconds
   3. `blood AND NOT pressure`: 0.002 seconds
   4. `blood OR pressure AND cardiovascular`: 0.002 seconds
   5. `"blood pressure"`: 0.01 seconds
   6. `diet \10 health`: 0.007 seconds
   7. `diet \10 health AND "red wine"`: 0.007 seconds
3. Spell checker results:
   1. `blod`: 0.004 seconds with 6 possible replacements 
   2. `presure`: 0.02 seconds with 1 possible replacements
   3. `analysi`: 0.019 seconds with 2 possible replacements
