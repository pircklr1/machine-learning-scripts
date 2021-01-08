# IBM AI Enterprise Workflow Capstone - Time Series Forecasting
This repository contains a time series prediction application for the IBM AI Enterprise Workflow Capstone project. 
The application utilized Facebook's Prophet algorithm, as well as datasets provided by the course.

This project contains 
* Unit tests for API, logging, and model
* run_tests.py for running all tests with a single script
* monitoring.py for performance monitoring
* Model_validation.ipynb for model comparison
* EDA.ipynb for data analysis
* Docker deployment

Usage notes
===============

All commands are from this directory.

To test app.py
---------------------

    ~$ python app.py
    
To test the model directly
----------------------------

see the code at the bottom of `prophet_model.py`

    ~$ python prophet_model.py

To build the docker container
--------------------------------

    ~$ docker build --tag prophet_app .

Check that the image is there.

    ~$ docker image ls
    
You may notice images that you no longer use. You may delete them with

    ~$ docker image rm IMAGE_ID_OR_NAME

And every once and a while if you want clean up you can

    ~$ docker system prune


To run the unittests
-------------------

Before running the unit tests launch the `app.py`.

To run only the api tests

    ~$ python unittests/ApiTests.py

To run only the model tests

    ~$ python unittests/ModelTests.py


To run all of the tests

    ~$ python run-tests.py

To run the container 
--------------------    

    ~$ docker run -p 4000:8080 prophet_app
