import argparse
from flask import Flask, jsonify, request
from flask import render_template, send_from_directory
import os
import re
import joblib
import socket
import json
import numpy as np
import pandas as pd
from prophet_model import model_train, model_predict

app = Flask(__name__)

@app.route('/running', methods=['GET','POST'])
def running():
    return jsonify(True)

@app.route('/predict', methods=['GET','POST'])
def predict():
    """
    basic predict function for the API
    """
    
    ## input checking
    if not request.json:
        print("ERROR: API (predict): did not receive request data")
        return jsonify([])

    if 'country' not in request.json:
        print("ERROR API (predict): received request, but no country found within")
        return jsonify([])

    if 'year' not in request.json:
        print("ERROR API (predict): received request, but no year found within")
        return jsonify([])

    if 'month' not in request.json:
        print("ERROR API (predict): received request, but no month found within")
        return jsonify([])
        
    if 'day' not in request.json:
        print("ERROR API (predict): received request, but no day found within")
        return jsonify([])

    ## extract the query
    query=(request.json)
    c=query.get("country")
    y=query.get("year")
    m=query.get("month")
    d=query.get("day")
    result = model_predict(c,y,m,d)
    return(jsonify(result.yhat.values[0]))

@app.route('/train', methods=['GET','POST'])
def train():
    """
    basic predict function for the API
    """

    print("... training model")
    model_train()
    print("... training complete")

    return(jsonify(True))
        
if __name__ == '__main__':

    ## parse arguments for debug mode
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", "--debug", action="store_true", help="debug flask")
    args = vars(ap.parse_args())

    if args["debug"]:
        app.run(debug=True, port=8080)
    else:
        app.run(host='0.0.0.0', threaded=True ,port=8080)

