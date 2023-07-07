import re
import os
import en_core_web_sm
import de_core_news_sm
import fr_core_news_sm
import xx_ent_wiki_sm
import langdetect
import pandas as pd
import numpy as np
from time import perf_counter
from functools import partial
from multiprocessing import cpu_count, Pool

from config.config import ClientConfig, AnalyzerConfig
from misc.data_reader import read_data, _get_file_suffix

nlp_en = en_core_web_sm.load()
nlp_de = de_core_news_sm.load()
nlp_fr = fr_core_news_sm.load()
nlp_mult = xx_ent_wiki_sm.load()

nlp = {"en": nlp_en, "de": nlp_de, "fr": nlp_fr}

cores = cpu_count() #Number of CPU cores on your system
partitions = cores #Define as many partitions as you want
 

def parallelize(data, func):
    data_split = np.array_split(data, partitions)
    pool = Pool(cores)
    data = pd.concat(pool.map(func, data_split))
    pool.close()
    pool.join()
    return data


def run_on_subset(func, data_subset):
    return data_subset.map(func)


def parallelize_on_rows(data, func):
    return parallelize(data, partial(run_on_subset, func))


class Sanitizer:
    def __init__(self, data: pd.DataFrame, columns_to_sanitize: set, filename: str):
        self.columns = data.columns.values

        for column in columns_to_sanitize:
            if column not in self.columns:
                print(f"Column '{column}' destined for sanitizing, not found in data. Dropping from targets.")
                columns_to_sanitize.remove(column)

        self.language_column = "language"
        self.targets = columns_to_sanitize
        self.dataframe = data

        self._sanitize()
        _filename = filename[:filename.rfind(".")].replace(" ", "_") + ".json"
        path = os.path.join(ClientConfig.SANITIZED_FILES_DIRECTORY, _filename)
        self._dump_as_json(path)


    def _filter_email_addresses(self, text: str) -> str:
        """
        Substitute email-addresses with 'xxx@email.zz'
        """
        return re.sub(r"\S*@\S*\s?", 'xxx@email.zz ', str(text))


    def _langdetect_wrapped(self, text: str) -> str:
        """
        Wrapped langdetect to handle empty text-strings.

        Returns a string of language ISO-codes
        """
        try:
            return langdetect.detect(str(text))
        except langdetect.lang_detect_exception.LangDetectException:
            return ""


    def _sanitize_entry(self, text: str) -> str:
        """
        Attempts to find person names in text and replace them with '--retracted--' 
        """
        language = self._langdetect_wrapped(text)
        try:
            AnalyzerConfig.ISOCODE_LANGUAGE_MAP[language]
        except KeyError:
            language = "en"
            
        text = self._filter_email_addresses(text)

        try:
            doc = nlp[language](text)
        except KeyError:
            doc = nlp_mult(text)
        
        _text = doc.text
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                escaped = re.escape(ent.text)
                _text = re.sub(escaped, "--retracted--", _text)

        return {"text": _text, "language": language}


    def _sanitize(self) -> None:
        """
        Runs sanitizing per target-column in 'self.targets'
        """
        for column in self.targets:
            data = parallelize_on_rows(self.dataframe[column], self._sanitize_entry)

            texts = [entry["text"] for entry in data]
            languages = [entry["language"] for entry in data]

            self.dataframe[column] = texts
            self.dataframe[self.language_column] = languages


    def _dump_as_json(self, path: str) -> None:
        """
        Dump a dataframe as a json-file
        """
        print(f"Saved columns {self.dataframe.columns.values}, with {len(self.dataframe)} entries to {path}")
        self.dataframe.to_json(path)


if __name__ == "__main__":
    start = perf_counter()

    df, columns, filename = read_data(ClientConfig.DATA_DIRECTORY)
    print(f"Sanitizing data-columns: '{columns}'")

    # Sanitizes and dumps the data as a new json-file to project root
    _ = Sanitizer(df, columns, filename)
    
    print(f"Took {round(perf_counter() - start, 2)} seconds")
