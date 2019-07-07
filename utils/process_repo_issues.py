from itertools import compress
from ast import literal_eval
import re
from collections import Counter
import json
import warnings

import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import pos_tag

from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS


from wordcloud import WordCloud
import matplotlib.pyplot as plt


# Suppress pandas's warning
warnings.simplefilter(action='ignore', category=Warning)


def read_repo_issues_summary_data(csv_path):

    df_orig = pd.read_csv(csv_path)

    # --- Cast date columns to datetime
    cols_date = ['createdAt', 'closedAt', 'firstCommentCreatedAt']
    df_orig[cols_date] = df_orig[cols_date].apply(pd.to_datetime)

    # --- Cast labels column to list
    df_orig['labels'] = df_orig['labels'].apply(literal_eval)

    # --- Fill na of the text columns with ''
    cols_text = ['title', 'contents']
    df_orig[cols_text] = df_orig[cols_text].fillna('')

    return df_orig

def process_texts(issue_text, custom_stopwords=None):
    '''
    Process text
    
    Input argument:
        issue_text: a list of interested text in each issue
        
    Optional input argument:
        custom_stopwords: a dictionary which contains
            {
            'before_process': <a list of stopwords applied before start processing>
            'after_process': <a list of stopwords applied getting the processed texts>
            }
    Output argument:
        list_joined_text: a list of all processed texts
    '''
    
    # -----
    # Remove stopwords before start processing
    
    if custom_stopwords and ('before_process' in custom_stopwords):
        
        stopwords_before_process = custom_stopwords['before_process']
        
        new_text = []
        for cur_text in issue_text:
            for cur_rep in stopwords_before_process:
                cur_text = cur_text.replace(cur_rep, ' ')
            new_text.append(cur_text)

        issue_text = new_text
        
    # -----
    
    issue_words = [word_tokenize(x) for x in issue_text]

    # Case Normalization

    issue_words = [[x.lower() for x in words] for words in issue_words]

    # Remove punctuation characters
    issue_words = [[x for x in words if len(re.findall(r"^\w+", x)) > 0] for words in issue_words]

    # Remove text with just a number
    issue_words = [[x for x in words if len(re.findall(r"^\d+", x)) == 0] for words in issue_words]

    # repo_stopwords = stopwords.words("english")
    repo_stopwords = list(ENGLISH_STOP_WORDS)

    issue_words = [[w for w in words if w not in repo_stopwords] for words in issue_words]

    # --- Part of speech tagging
    pv_tags_words = [pos_tag(words) for words in issue_words]

    lemmatizer = WordNetLemmatizer()

    # Get current text
    final_clean_tokens = []
    for cur_pv_tags_words in pv_tags_words:

        cur_clean_tokens = []
        for cur_tag in cur_pv_tags_words:

            cur_text = cur_tag[0]

            # Get a corresponding part of speech that will be used with the lemmatizer
            w_tag = get_wordnet_pos(cur_tag[1])

            # lemmatize the text with pos and append it to clean_tokens
            clean_tok = lemmatizer.lemmatize(cur_text, w_tag)
            cur_clean_tokens.append(clean_tok)

        final_clean_tokens.append(cur_clean_tokens)
        
    # from nltk.stem.porter import PorterStemmer

    # # Reduce words to their stems
    # [PorterStemmer().stem(w) for w in issue_words[0]]
    # issue_words = [[PorterStemmer().stem(w) for w in words] for words in issue_words]

    # Remove a single character
    issue_words = [[x for x in words if len(re.findall(r"^\w$", x)) == 0] for words in issue_words]
    
    
    # -----
    # Remove stopwords before start processing
    
    if custom_stopwords and ('after_process' in custom_stopwords):
        
        stopwords_after_process = custom_stopwords['after_process']
        issue_words = [[x for x in words if not any([x.startswith(cur_stopword) for cur_stopword in stopwords_after_process])] for words in issue_words]
    
    # -----
    # Flatten list
    
    # https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
    list_joined_text = [item for sublist in issue_words for item in sublist]
    
    return list_joined_text

# --- For internal use

def get_wordnet_pos(tag):
    ''' 
    Get a TreeBank tag from the specified WordNet part of speech name
    Args:
    tag: string. WordNet part of speech name.
    Returns:
    A corresponding TreeBank tag
    '''

    treebank_tag = ''
    # Refer to 
    # https://stackoverflow.com/questions/15586721/wordnet-lemmatization-and-pos-tagging-in-python

    if tag.startswith('J'):
        # Adjective
        treebank_tag = wordnet.ADJ

    elif tag.startswith('V'):
        # Verb
        treebank_tag = wordnet.VERB

    elif tag.startswith('N'):
        # Noun
        treebank_tag = wordnet.NOUN

    elif tag.startswith('R'):
        # Adverb
        treebank_tag = wordnet.ADV

    else:
        # Use Noun as a default output if none of above matches
        treebank_tag = wordnet.NOUN

    return treebank_tag

