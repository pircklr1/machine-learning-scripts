import os
import pandas as pd
import argparse
from typing import Union, List, Set, Tuple


READERS = {
    ".csv": (pd.read_csv, {"delimiter": ";"}),
    ".json": (pd.read_json, {}),
    ".xlsx": (pd.read_excel, {}),
    ".xls": (pd.read_excel, {})
}


def _get_file_suffix(filename: str) -> str:
    return filename[filename.rfind("."):]


def _arg_parse() -> Tuple[str, Set[str]]:
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", default="", required=False, help="Insert a filename from test_data-folder to be parsed")
    parser.add_argument("-c", "--columns", default="", required=False, help="Insert columns to sanitize. Separate with commas")
    args = parser.parse_args()

    filename = args.filename
    columns = set(args.columns.split(","))

    return (filename, columns)


def _get_data(data_dir: str, filename: str) -> Union[pd.DataFrame, List[str]]:
    path = os.path.join(data_dir, filename)

    reader, args = READERS[_get_file_suffix(filename)]

    dataframe = reader(path, **args)
    columns = dataframe.columns.values

    return dataframe, columns


def read_data(data_dir: str) -> Union[pd.DataFrame, Set[str]]:
    """
    Takes a directory of potential data-files as a parameter. Accepts command-line argumnets for filename and for columns or without arguments, starts a simple command-line UI to choose the filename and columns.

    Returns:
        * A dataframe read from the chosen file
        * A set of chosen column-names
    """
    filenames = os.listdir(data_dir)

    filename, chosen_columns = _arg_parse()

    if filename not in filenames:
        for i, filename in enumerate(filenames):
            print(f"* {i} -> {filename}")

        file_choice = input("Choose a file, using its number from the above list -> ")

        try:
            filename = filenames[int(file_choice)]
        except (ValueError, IndexError):
            return pd.DataFrame(), set()

    dataframe, columns = _get_data(data_dir, filename)

    if not chosen_columns.issubset(columns):
        print("-------------------")

        for i, col_name in enumerate(columns):
            print(f"* {i} -> {col_name}")

        _choices = set(input("Choose columns to sanitize. Separate different column-numbers with spaces -> ").split())

        try:
            chosen_columns = set(columns[int(i)] for i in _choices)
        except (ValueError, IndexError):
            chosen_columns = set()

    return dataframe, chosen_columns, filename


if __name__ == "__main__":
    """
    Saves all column-names with their corresponding filenames from all the files from 'data_dir' to path 'columns_file'.
    """
    import json

    data_dir = "test_data"
    columns_file = "config/columns.json"
    columns_per_file = {}

    for filename in os.listdir(data_dir):
        print(f"Parsing columns from '{filename}'")
        _, columns = _get_data(data_dir, filename)
        columns_per_file[filename] = list(columns)

    with open(columns_file, "w") as f:
        json.dump(columns_per_file, f, indent=4)
