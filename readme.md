# Key words extractor
The program gets a folder and produces a file 'key_words_extracted.csv' with the most frequent interesting words, showing where those words appear (sentences and documents).

## Requirements
Python 3.9

# How to start
```bash
pip3 install virtualenv;
git clone git@github.com:Allexeyv/key_words_extractor.git;
cd key_words_extractor;
python3 -m venv venv;
source venv/bin/activate;
pip3 install --upgrade pip;
pip3 install -r requirements.txt;

python3 -m word_extractor --lang=en --num_of_keywords=3 --keyword_limit_in_final_table=3 --folder=test_docs
```