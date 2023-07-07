import os
import requests
import pandas as pd
from time import perf_counter
from config.config import ClientConfig
import argparse


def request(route, data):
    """
    Request-function to test and time different routes
    """
    start = perf_counter()

    url = "http://0.0.0.0:5000"
    response = requests.post(f"{url}/{route}", json=data)

    stop = perf_counter()

    print(
        f"Response: {response.json()}\nCompleted in {round(stop - start, 2)} seconds")

    return response.json()


def _ask_columns_to_activate(dataframe: pd.DataFrame) -> list:
    columns = list(dataframe.columns.values)
    for i, column in enumerate(columns):
        print(f"{i} -> {column}")

    _choices = set(input(
        "Choose columns to analyze. Separate different column-numbers with spaces -> ").split())

    try:
        chosen_columns = set(columns[int(i)] for i in _choices)
    except (ValueError, IndexError):
        chosen_columns = set(_ask_columns_to_activate(dataframe))

    return list(chosen_columns)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Perform LSI topic modelling on given input file. Expects keys: log_date, title, body, top_n, language')
    parser.add_argument('filename', help='Path to the input file.')
    parser.add_argument('query', help='Query')

    args = parser.parse_args()

    filename = args.filename
    query = args.query

    path = os.path.join(ClientConfig.SANITIZED_FILES_DIRECTORY, filename)

    dataframe = pd.read_json(path)

    _data = dataframe  # dataframe[dataframe["language"] == "en"]
    training_data = {}

    for key in _data:
        training_data[key] = _data[key].to_list()

    try:
        confirm = input("Build analyzers? 'y' for yes, blank for no -> ")
        if confirm == "y":
            # Add a list of columns in data, for which analyzers will be started for
            training_data["dataset"] = filename[:filename.rfind(".")]
            training_data["keys"] = _ask_columns_to_activate(_data)
            print("Building analyzers...\n")
            _ = request("training_data", training_data)

        similarities = request("find_similar", query)

        for sim in similarities["similar"]:
            try:
                doc_id = sim["document_id"]
                doc_sim = sim["similarity_score"]
                print(f"\n({doc_id}, {doc_sim})")
                for key, value in training_data.items():
                    if key != "keys" and key != "dataset":
                        print(f"{key}: {value[doc_id]}")
            except (TypeError, KeyError):
                pass

        _ = request("update", query)

        # The requests below have only routes predefined and implement no functionality as of yet. If called, will return {"status": 501}
        '''
        suggestion = {}
        request("used_suggestion", suggestion)

        review = {}
        request("review_results", review)
        '''
    except requests.ConnectionError:
        print("No connection.")


if __name__ == "__main__":
    main()
