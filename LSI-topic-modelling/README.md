# LSI topic modelling

Topic modelling POC

## Requirements

- OS capable to run Docker and Python's scientific libraries (on Windows, you'll perhaps need to use WSL or Anaconda to get the latter to work)
- Sufficient memory to load datasets into memory
- Python version 3.7 or later (might work on 3.6 as well)
- Python3 package manager; pip
- Python virtual environment; pipenv
- Docker (tested on version 19.03, but shouldn't use any version-dependant features from that, so should well work on prior versions)
- Docker-compose (tested on versions 1.24 and 1.25, but shouldn't use any version-dependant features from those, so should well work on prior versions)

## Installation

Docker and docker-compose are required to install the development version. Pipenv (installable via pip) required for out-of-container testing and running the test-client and sanitizer. Type `pipenv install` in command line at project root (folder with the Pipfile).

For API-server (app.py), run `docker-compose build` to download the required parts from Docker Hub and build the image for API-server. Every time code changes at any layer of API-server (not counting sanitizer.py or client.py), run the above build again.

## Installing sanitizer

You will need to install spaCy models for English, German, French and others manually because they are not packaged:

`pipenv run python3 -m spacy download en_core_web_sm-2.2.5 --direct`

`pipenv run python3 -m spacy download de_core_news_sm-2.2.5 --direct`

`pipenv run python3 -m spacy download fr_core_news_sm-2.2.5 --direct`

`pipenv run python3 -m spacy download xx_ent_wiki_sm-2.2.0 --direct`

## Using sanitizer

Add a test_data-directory to project root. Populate directory with a csv, json or excel-files. Run sanitizer with the command `pipenv run python sanitizer.py` with optional flags `-f` following a filename from within test_data-folder and `-c` for columns to sanitize from the chosen file. When wanting to sanitize several columns, use a comma (with no spaces) to separate column-names. If a file- or column-name has spaces in it, surround the name with quotation marks.

Example: `pipenv run python sanitizer.py -f AI_Tickets.csv -c "Short Description"`

If not using the flags/command-line arguments, a simple command-line UI asks you to choose the filename/columns. From the UI, you can choose several columns by separating their numbers with spaces.

Running sanitizer creates a file with the same name in the training_data-folder, but its suffix replaced with '.json' and any spaces in its name replaced with an underscore. These sanitized files are used for the application training via client and for validating/reviewing the returned similarity-results.  
Use either docker/docker-compose (runs on gunicorn-server) or pipenv (runs on flask's internal development server) to run the API-server and pipenv to run the client (when the API-server is up).

## Test-client (client.py)

Using the test-client might require you to add/remove/modify filenames from the 'filenames'-tuple in client.py. Also, for every filename in the tuple, you should define values for keys 'log_date', 'title' and 'body' into 'rename_dict'. The correct value for each key-value-pair is a fitting column-name from the file for which the entries are made for.

Example: `rename_dict = {"example_file.json": {"log_date": "Log date", "title": "short description", "body": "detail description"}}`

Example: `filenames = ("example_file.json")`

The test client is a one-off script to test all implemented routes (at the moment, only training_data and find_similar). Pipenv-environment required to run;  
`pipenv run python client.py`  
The client iterates through all the available files defined in filenames/rename_dict.  
When running, the client asks if you'd like to build the analyzers. On first run, press `y` to agree (on agreeing you're presented with a simple cmd-line UI, from which you can choose those columns, for which analyzers get activated/built). On subsequent client-runs, you can press anything else to just find the similarities.  
Prints the responses it gets from the API-server from route 'find_similar' and also prints the corresponding entries found from the used training_data.

## API-server

The JSON-object for a query outlines as follows:

- "log_date": 'ISO 8601'-formatted datetime-string, with optional timezone-info. [Check here](https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat) for more info, if using Python 3.7 or later to handle clientside requests.
- "dataset": Filename or some other identifier as a string.
- "title": Title of the issue as a string.
- "body": Detailed description as a string.
- "top_n": Number of desired similar document-IDs as an integer. **Optional** and used for route 'find_similar' only.
- "language": Issue's language as an [ISO-code](https://www.loc.gov/standards/iso639-2/php/code_list.php) string.

The API-server has 5 monitored routes (all of which accept POST-requests only):

- "find_similar": accepts the above-outlined json-object and returns a response json-object:  
  { "similar": [ { "document_id": Integer number, representing IDs of similar past issues, "similarity_score": Floating-point number, representing the similarity-rating of the accompanied document-ID] }.  
  Unless restricted to just one by the use of 'top_n' in the initial request, should return several ID/score-pairs in the list.
- "training_data": accepts a json-object like above, but each value is a list of its values (list-indexes of each separate list must correspond to a single issue) and without attribute 'top_n'. Used for initial training or forced retraining of the analyzers. Returns only an http-status of 200 if successful, 400 for wrongly formatted request.
- "update": accepts a similar json-object as the find_similar does, but without the attribute 'top_n'. Returns an http-statuscode of 501 (Not implemented).
- "user_suggestion": reserved for future implementation. Returns an http-statuscode of 501 (Not implemented).
- "review_results": reserved for future implementation. Returns an http-statuscode of 501 (Not implemented).
