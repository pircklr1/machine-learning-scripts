from gensim import similarities, corpora, models
from gensim.test.utils import get_tmpfile
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords

from collections import defaultdict
from datetime import datetime


class SimilarityAnalyzer:
    def __init__(self, name: tuple, config: object) -> None:
        """
        Params:
            * name: Name of an instance. Used to differentiante persistent files between instances.
            * lang_code: ISO-code of the language, the analyzer will be formatted for.
        """
        self.name = "_".join(name)
        self.config = config

        if self.name.find(" ") != -1:
            self.name = "".join(self.name.split())

        self.dictionary_filename = get_tmpfile(f"{self.name}.dictionary")
        self.index_filename = get_tmpfile(f"{self.name}.index")
        self.lsi_model_filename = get_tmpfile(f"{self.name}_lsi.model")

        try:
            _language = self.config.ISOCODE_LANGUAGE_MAP[name[0]]
        except KeyError:
            _language = "english"

        # Initializing requirements for text preprocessing
        self.stoplist = self._prepare_stoplists(_language)
        self.stemmer = self._prepare_stemmer(_language)

        # Analyzer's inner errors
        self.errors = []

        self.init_time = datetime.now()
        self.update_time = None

        # Try to populate members from persistent storage.
        self.dictionary = self._get_dictionary()
        self.lsi_model = self._get_model()
        self.index = self._get_index()


    def _prepare_stemmer(self, language: str):
        stemmers = {lang: SnowballStemmer for lang in SnowballStemmer.languages}
        stemmers["english"] = WordNetLemmatizer
        
        stemmer = stemmers[language]
        try:
            return stemmer()
        except TypeError:
            return stemmer(language)
            

    def _prepare_stoplists(self, language: str):
        _stopwords = set(stopwords.words(language))
        _stopwords.update(self.config.CUSTOM_STOPWORDS)
        return _stopwords


    def train_with(self, documents: list) -> None:
        """
        Build and train a document index and a model of the words of said documents. Also saves a persistent dictionary for later use.

        Params:
            documents: A list of texts for training data
        """
        self.update_time = datetime.now()

        wordlist = self._preprocess(documents)
        self._build_dictionary_and_corpus(wordlist)
        # Save dictionary to file, for faster spin-up in the future
        self.dictionary.save(self.dictionary_filename)
        self._build_model()
        self._build_index()
        self.errors = []


    def get_state(self) -> dict:
        """
        Returns a dictionary with key 'state' of string 'OK' if given instance should work as expected, 'NOK' if not and a timestamp of initial training and of last update, with keys 'init_time' and 'update_time' respectively.
        """
        state = "OK" if len(self.errors) == 0 else "NOK"
        return {
            "name": self.name,
            "state": state, 
            "init_time": self.init_time, 
            "update_time": self.update_time
        }


    def _stem(self, text: list) -> list:
        try:
            stem = self.stemmer.lemmatize
        except AttributeError:
            stem = self.stemmer.stem

        return [stem(w) for w in text]


    def _preprocess(self, documents: list) -> list:
        # Remove common words and tokenize
        texts = [
            [word for word in str(document).lower().split() if word not in self.stoplist and len(word) > 1]
            for document in documents if len(str(document)) > 1
        ]

        if len(documents) > 1:
            # Remove words that appear only once
            frequency = defaultdict(int)
            for text in texts:
                for token in text:
                    frequency[token] += 1

            texts = [
                [token for token in text if frequency[token] > 1]
                for text in texts
            ]

        return [self._stem(text) for text in texts]


    def _build_dictionary_and_corpus(self, documents: list) -> None:
        self.dictionary = corpora.Dictionary(documents)
        self.corpus = [self.dictionary.doc2bow(text) for text in documents]


    def _get_dictionary(self):
        try:
            return corpora.Dictionary.load(self.dictionary_filename)
        except FileNotFoundError:
            self.errors.append("Dictionary not found,")
            return None


    def _get_model(self):
        # Tries to load the LSI-model
        try:
            return models.LsiModel.load(self.lsi_model_filename)
        except FileNotFoundError:
            self.errors.append("LSI-model not found.")
            return None


    def _build_model(self) -> None:
        # Create LSI-model
        self.lsi_model = models.LsiModel(self.corpus, id2word=self.dictionary, num_topics=self.config.NUM_TOPICS)

        # Save model to file, for faster spin-up in the future
        self.lsi_model.save(self.lsi_model_filename)


    def _get_index(self):
        # Tries to load a persistent document index
        try:
            return similarities.MatrixSimilarity.load(self.index_filename)
        except FileNotFoundError:
            self.errors.append("Document-index not found.")
            return None


    def _build_index(self) -> None:
        # Transform corpus to LSI space and index it
        self.index = similarities.MatrixSimilarity(self.lsi_model[self.corpus])

        # Save index to file, for faster spin-up in the future
        self.index.save(self.index_filename)


    def run_query(self, query: str) -> list:
        """
        Finds similar text-entries to query from added documents.

        Params:
            query: Text for which similar texts are wanted

        Returns a list of tuples (document-number, document-similarity)
        """
        # If dictionary not setup correctly, return a list of errors
        if self.dictionary == None:
            return self.errors

        # Run same preprocess as with training-data
        processed_query = self._preprocess([query])[0]

        # Create a bag of words from the query
        vec_bow = self.dictionary.doc2bow(processed_query)

        # Convert the query to LSI space
        vec_lsi = self.lsi_model[vec_bow]

        # Perform a similarity query against the corpus
        sims = self.index[vec_lsi]

        # (document_number, document_similarity) 2-tuples, sorted by negated similarity-value
        sims = sorted(enumerate(sims), key=lambda item: -item[1])

        results = list()

        for tup in enumerate(sims):
            s = tup[1]
            # Add a list of (document_number, document_similarity) to results-list
            results.append([s[0], float(s[1])])

        # Listify the set for better compatibility
        return results


    def update_model(self, entry: str) -> dict:
        self.update_time = datetime.now()
        #self.lsi_model.add_documents()
        return {self.name: f"Updated on {self.update_time}"}
