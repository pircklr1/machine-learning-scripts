from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict

from config.config import FlaskConfig, AnalyzerConfig
from analysis.similarity_analyzer import SimilarityAnalyzer

if __name__ != "__main__":
    from logging.config import dictConfig

    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

app = Flask(__name__)
app.config.from_object(FlaskConfig)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

analyzers = {}

def filter_languages(data: dict):
    valid_languages = AnalyzerConfig.ISOCODE_LANGUAGE_MAP
    if isinstance(data["language"], list):
        languages = data["language"]
    else:
        languages = [data["language"]]

    return set([isocode for isocode in languages if isocode in valid_languages])


def register_existing_analyzers(data: dict):
    '''
    Respawns those analyzers, for which models, indexes and dictionaries have been previously been built and saved as persistent files (all three files required for respawn to succeed).
    '''
    # TODO Get rid of globals
    global analyzers

    app.logger.info("Trying to respawn previously trained analyzers...")

    _languages = filter_languages(data)
    _dataset = data["dataset"]

    aux_keys = ("top_n", "language", "dataset")
    # Filter auxiliary entries from data (to stop trying to ressurect analyzers for 'top_n' for example)
    _data = {key: data[key] for key in data if key not in aux_keys}

    for language in _languages:
        for _key in list(_data.keys()):
            key = (language, _key, _dataset)
            analyzer = SimilarityAnalyzer(key, AnalyzerConfig)
            state = analyzer.get_state()
            if state["state"] == "NOK":
                app.logger.info(f"Failed to respawn {state['name']}")
                pass
            else:
                analyzers[key] = analyzer
                app.logger.info(f"Respawned {state['name']}-analyzer")


@app.route("/find_similar", methods = ['POST'])
def find_similar():
    '''
    Tries to find similar issues from the AIC's database.
    Returns a json-object, with the key: 'similar' and a list of dictionaries of {document_id: int, similarity_score: float} as value.
    '''
    data = request.get_json()

    active_language = data["language"]
    if active_language not in AnalyzerConfig.ISOCODE_LANGUAGE_MAP:
        return jsonify({"similar": {"language": f"{active_language} not supported"}})

    # TODO Get rid of globals
    global analyzers

    try:
        top_n = int(data["top_n"])
    except KeyError:
        # If 'top_n' not specified in request, defaults to this
        top_n = AnalyzerConfig.DEFAULT_TOP_N

    # If no analyzers activated, try and respawn from persistent storage
    if len(analyzers) == 0:
        register_existing_analyzers(data)

    total = defaultdict(float)

    used_keys = []

    for key in analyzers:
        state = analyzers[key].get_state()
        if state["state"] == "NOK":
            pass

        used_keys.append(key)

        # Sum similarity-scores together for each unique ID from each distinct analyzer
        try:
            for sim in analyzers[key].run_query(data[key[1]]):
                total[sim[0]] += sim[1]
        except KeyError:
            pass

        app.logger.info(str(state))

    # Sort by highest similarity-score
    sims = sorted(total.items(), key=lambda item: item[1], reverse=True)

    # Include only top-n of the sorted similarities
    sims = sims[:top_n]

    # Rearrange similarities to dictionary-form, for increased clarity of response
    sims_dict = [{
        "document_id": sim[0], 
        "similarity_score": sim[1] / len(used_keys)
        } for sim in sims]

    return jsonify({"similar": sims_dict})


@app.route("/training_data", methods = ['POST'])
def training_data():
    '''
    Builds the analyzer-objects according to 'keys'-field in received data.
    Returns a status object.
    '''
    data = request.get_json()

    keys = data["keys"]

    _languages = filter_languages(data)

    # TODO Get rid of globals
    global analyzers

    for language in _languages:
        for _key in keys:
            key = (language, _key, data["dataset"])
            analyzers[key] = SimilarityAnalyzer(key, AnalyzerConfig)
            state = analyzers[key].get_state()

            if state["state"] == "NOK":
                app.logger.info(f"Commencing initial training of '{state['name']}'-analyzer")
            else:
                app.logger.info(f"Commencing retraining of '{state['name']}'-analyzer")

            analyzers[key].train_with(data[_key])

    return jsonify({"status": 200})


@app.route("/update", methods = ['POST'])
def update():
    '''
    Updates the analyzers for which the new data has keys for.
    Returns a status object.
    '''
    data = request.get_json()

    # TODO Get rid of globals
    global analyzers

    #app.logger.info("Updating model(s)")
    #updated = [analyzer.update_model(data[key]) for key, analyzer in analyzers.items() if key in data]
    #app.logger.info(str(updated))

    # HTTP-code 501 stands for 'Not Implemented'
    return jsonify({"status": 501})

    #return jsonify({"status": 200})


@app.route("/used_suggestion", methods = ['POST'])
def used_suggestion():
    '''
    Inform the AIC of the used inquiry_id in relation to an issue_id.
    Returns a status object.
    '''
    suggestion = request.get_json()
    app.logger.info(suggestion)
    # HTTP-code 501 stands for 'Not Implemented'
    return jsonify({"status": 501})


@app.route("/review_results", methods = ['POST'])
def review_results():
    '''
    Accepts a two-part review-object, with the first value being the inquiry_id in question and the second a rating from -1.0 to 1.0.
    Returns a status objcet.
    '''
    review = request.get_json()
    app.logger.info(review)
    # HTTP-code 501 stands for 'Not Implemented'
    return jsonify({"status": 501})


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
