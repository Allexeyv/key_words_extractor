import glob
import yake
import nltk
import pandas as pd
from fire import Fire


class WordExtractor:
    """Class provides extracting key words (interesting words) from a list of text files using YAKE! algorithm.
    
    Attributes:
        lang (str, optional): A parameter to determin text language. Defaults to 'en' (English).
        num_of_keywords (int, optional): How many key words should be in the result from a sentence. Defaults to 3.
        keyword_limit_in_final_table (int, optional): A filter parameter for the result table. Cuts unpopular words. Defaults to 3.
        keyword_list (dict): Stores all extracted key words from text. Data for the result table. {'keyword': {'count': 0, 'source': [], 'sentence': []}}
        keyword_list_filtered (dict): Stores only popular key words, the limit is in the than keyword_limit_in_final_table parameter.
        blacklist (list): Unwanted key words.
    """

    def __init__(self, lang: str='en', num_of_keywords: int=3, keyword_limit_in_final_table: int=3):
        self.max_ngram_size = 1
        self.deduplication_threshold = 0.9
        self.custom_kw_extractor = yake.KeywordExtractor(
            lan=lang,
            n=self.max_ngram_size,
            dedupLim=self.deduplication_threshold,
            top=num_of_keywords,
        )
        self.keyword_limit_in_result = keyword_limit_in_final_table
        self.keyword_list = {}
        self.keyword_list_filtered = {}
        self.blacklist = ['year', 'years', 'day', 'time', 'make', 'made', 'easy', 'hard', 'stop', 'good', 'looked',
                        'long', 'making', 'left', 'stand', 'pass', 'true', 'ago', 'longer', 'times', 'turned', 'greater', 
                        'and', 'thing', 'told', 'thought', 'changed', 'words', 'fact'
        ]

    def _clean_text(self, text: str) -> str:
        """Prepares text for the future operations.
        Args:
            text (str): Text to clean.
        Returns:
            text (str): Cleaned text.
        """
        if 'al Qaeda' in text:
            text = text.replace('al Qaeda', 'alqaeda')
        return text

    def _extract_keywords(self, text: str) -> list:
        """Extract key words from text.
        Args:
            text (str): Text to extract key words from.
        Returns:
            keyword_list (list): Keyword list.
        """
        keyword_list = []
        text = self._clean_text(text)
        keywords = self.custom_kw_extractor.extract_keywords(text)
        for data in keywords:
            keyword_list.append(data[0])
        return keyword_list

    def _get_sentences(self, file_name: str) -> list:
        """Gets sentences from a file
        Args:
            file_name (str): Text file name
        Returns:
            sentences (list): Sentences from a file
        """
        with open(file_name, 'r', encoding="utf8") as f:
            text = f.read()
            sentences = nltk.sent_tokenize(text)
        return sentences

    def _make_sentence_list(self, file_list: list) -> list:
        """Makes sentences from a list of files.
        Args:
            file_list (list): list of files
        Returns:
            sentence_list (list): sentence list
        """
        sentence_list = []
        for file_name in file_list:
            sentences = self._get_sentences(file_name)
            for sentence in sentences:
                sentence_list.append({'sentence': sentence, 'source': file_name})
        return sentence_list

    def _add_kw_to_dict(self, word: str, source: str, sentence: str) -> None:
        """Adds data to self.keyword_list
        Args:
            word (str): _description_
            source (str): _description_
            sentence (str): _description_
        """
        if self.keyword_list.get(word):
            self.keyword_list[word]['count'] += 1
            if source not in self.keyword_list[word]['source']:
                self.keyword_list[word]['source'].append(source)
            self.keyword_list[word]['sentence'].append(sentence)
        else:
            self.keyword_list[word] = {
                'count': 1,
                'source': [source],
                'sentence': [sentence],
            }

    def _filter_rows(self) -> None:
        """Filter rows to remove not popular key words
        """
        for k, v in self.keyword_list.items():
            if k in self.blacklist:
                continue
            if v['count'] >= self.keyword_limit_in_result:
                self.keyword_list_filtered[k] = v

    def process_file_list(self, file_list: list) -> None:
        """Extract key words from list of text files and stores them into self.keyword_list and self.keyword_list_filtered
        Args:
            file_list (list): list of text files
        """
        sentences = self._make_sentence_list(file_list)
        for row in sentences:
            key_words = self._extract_keywords(row['sentence'])
            for word in key_words:
                self._add_kw_to_dict(word.lower(), row['source'], row['sentence'])
        self._filter_rows()


def main(folder, lang='en', num_of_keywords=3, keyword_limit_in_final_table=3):
    """Launches the program.
    """
    nltk.download('punkt')
    file_list = glob.glob(f'{folder}/*txt')
    WE = WordExtractor(lang=lang, num_of_keywords=num_of_keywords, keyword_limit_in_final_table=keyword_limit_in_final_table)
    WE.process_file_list(file_list)
    df = pd.DataFrame(WE.keyword_list_filtered).transpose()
    df = df.sort_values(by=['count'], ascending=False)
    df = df.reset_index().rename({'index': 'word'}, axis=1)
    df.to_csv('key_words_extracted.csv', sep='\t', encoding='utf-8')
    print('The result csv is ready.')

if __name__ == '__main__':
    Fire(main)
