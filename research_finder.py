# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 21:45:45 2020

@author: Radin
"""

import pandas as pd
import json
import glob
import re
import pickle
import nltk
from nltk.cluster.util import cosine_distance
from nltk.corpus import stopwords
import numpy as np
import networkx as nx


class ResearchFinder():
    """
    Class that will return a list of papers related to the query, ranked by
    importance and relevance
    Will also return a summary of an paper
    """
    
    def __init__(self, all_metadata=None, all_jsons=None, data=None, citation_dict=None, vocab={}, sentence_similarity_dict={}):
        self.all_metadata = all_metadata
        self.all_jsons = all_jsons
        self.data = data
        self.citation_dict = citation_dict
        self.vocab = vocab
        self.sentence_similarity_dict = sentence_similarity_dict
        
    def store_data(self):
        research_finder_file = open('research_finder_file', 'ab') 
      
        # source, destination 
        pickle.dump(self, research_finder_file)                      
        research_finder_file.close() 
        
    def load_data(self, kaggle=False):
        if kaggle:
            research_finder_file = open('../input/research-finder-file/research_finder_file', 'rb')
        else:
            research_finder_file = open('research_finder_file', 'rb')      
        research_finder_object = pickle.load(research_finder_file) 
        self.all_metadata = research_finder_object.all_metadata
        self.all_jsons = research_finder_object.all_jsons
        self.data = research_finder_object.data
        self.citation_dict = research_finder_object.citation_dict
#        self.vocab = research_finder_object.vocab
        research_finder_file.close() 
            
    def add_to_vocab(self, word):
        self.vocab[word] = self.vocab.get(word, 0) + 1
        
    def json_parser(self, file_path):
        """
        Given a JSON filepath, returns dictionary containing relevant paper data
        """
        with open(file_path) as file:
            parsed_data = {}
            data = json.load(file)
            parsed_data['paper_id'] = data['paper_id']
            parsed_data['init_title'] = data['metadata']['title']
            parsed_data['title'] = re.sub('[^a-zA-z0-9\s]',' ',data['metadata']['title']).lower()
            
#            for word in parsed_data['title'].split(" "):
#                self.add_to_vocab(word)
            
            abstract = []
            body_text = []
            bib_entries = []
            
            init_abstract = []
            init_body_text = []
            
            for paragraph in data['abstract']:
                init_abstract.append(paragraph['text'])
                text = re.sub('[^a-zA-z0-9\s]',' ',paragraph['text']).lower()
                abstract.append(text)
#                for word in text.split(" "):
#                    self.add_to_vocab(word)
            for paragraph in data['body_text']:
                init_body_text.append(paragraph['text'])
                text = re.sub('[^a-zA-z0-9\s]',' ',paragraph['text']).lower()
                body_text.append(text)
#                for word in text.split(" "):
#                    self.add_to_vocab(word)
            for citation in data['bib_entries'].values():
                title = re.sub('[^a-zA-z0-9\s]',' ',citation['title'])
                title = title.lower()
                bib_entries.append(title)
            parsed_data['abstract'] = '\n'.join(abstract)
            parsed_data['body_text'] = '\n'.join(body_text)
            parsed_data['bib_entries'] = bib_entries
            
            parsed_data['init_abstract'] = '\n'.join(init_abstract)
            parsed_data['init_body_text'] = '\n'.join(init_body_text)
            return parsed_data
        
    def get_data(self):
        """
        Return all data in the form of a dataframe
        """
        if self.data is None:
            self.all_metadata = pd.read_csv("CORD-19-research-challenge/2020-03-13/all_sources_metadata_2020-03-13.csv"
                                            , dtype={
                                                    'doi': str,
                                                    'pubmed_id': str,
                                                    'Microsoft Academic Paper ID': str, 
                                                    }
                                            )
            self.all_jsons = glob.glob("CORD-19-research-challenge/2020-03-13/**/*.json"
                                       , recursive=True)
            data_dict = {
                        'paper_id': [],
                        'title': [],
                        'abstract': [], 
                        'body_text': [],
                        'bib_entries': [],
                        'init_title': [],
                        'init_abstract': [], 
                        'init_body_text': [],
                        
                        }
            for i, file_path in enumerate(self.all_jsons):
                if i % (len(self.all_jsons) // 10) == 0:
                    print(f'Processing index: {i} of {len(self.all_jsons)}')
                paper_data = self.json_parser(file_path)
                data_dict['paper_id'].append(paper_data['paper_id'])
                data_dict['title'].append(paper_data['title'])
                data_dict['abstract'].append(paper_data['abstract'])
                data_dict['body_text'].append(paper_data['body_text'])
                data_dict['bib_entries'].append(paper_data['bib_entries'])
                data_dict['init_title'].append(paper_data['init_title'])
                data_dict['init_abstract'].append(paper_data['init_abstract'])
                data_dict['init_body_text'].append(paper_data['init_body_text'])
            self.data = pd.DataFrame(data_dict, columns=['paper_id',
                                                         'title',
                                                         'abstract', 
                                                         'body_text',
                                                         'bib_entries',
                                                         'init_title',
                                                         'init_abstract', 
                                                         'init_body_text'])
            self.data.drop_duplicates(['abstract'], inplace=True)
#            for stopword in stopwords.words("english"):
#                self.vocab.pop(stopword, None)
#            for k in list(self.vocab.keys()):
#                if len(k) < 2:
#                    self.vocab.pop(k)
        return self.data
    
    def find_paper(self, keywords):
        data = self.get_data()
        score = pd.Series(0, index=data.index)
        for keyword in keywords:
            tf = np.log(1 + data['title'].str.count(keyword) \
                            + data['abstract'].str.count(keyword) \
                            + data['body_text'].str.count(keyword))
            idf = np.log((len(data.index)) / (1 + (1 * data['title'].str.contains(keyword) \
                                                + 1 * data['abstract'].str.contains(keyword) \
                                                + 1 * data['body_text'].str.contains(keyword))) )
            score += tf * idf
        data = data.reindex(score.sort_values(ascending=False).index)
        data['score'] = score
        citation_dict = self.get_citation_dict()
        data['importance'] = pd.Series([citation_dict.get(x) for x in data['title']])
        return data[0:100]
    
    def get_citation_dict(self):
        if self.citation_dict is None:
            citation_dict = {}
            data = self.get_data()
            for idx, row in data.iterrows():
                for citation in row['bib_entries']:
                    citation_dict[citation] = citation_dict.get(citation, 0) + 1
            self.citation_dict = citation_dict
        return self.citation_dict
    
    def summarize_paper(self, paper_text, n_sentences):
        self.sentence_similarity_dict = {}
        tokens = nltk.tokenize.sent_tokenize(paper_text)
        sentences = []
        for sentence in tokens:
            sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
        stop_words = stopwords.words("english")
        custom_stop_words = [
                            'doi', 'preprint', 'copyright', 'peer', 'reviewed',
                            'org', 'https', 'et', 'al', 'author', 'figure', 
                            'rights', 'reserved', 'permission', 'used', 'using',
                            'biorxiv', 'fig', 'fig.', 'al.', 'di', 'la', 'il', 
                            'del', 'le', 'della', 'dei', 'delle', 'una', 'da', 
                            'dell',  'non', 'si'
                            ]
        stop_words.extend(custom_stop_words)
        summarize_text = []
        # Step 2 - Generate Similary Martix across sentences
        sentence_similarity_martix = self.build_similarity_matrix(sentences, stop_words)
        # Step 3 - Rank sentences in similarity martix
        sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
        scores = nx.pagerank(sentence_similarity_graph)
        # Step 4 - Sort the rank and pick top sentences
        ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)    
        #print("Indexes of top ranked_sentence order are ", ranked_sentence)
        for i in range(0, n_sentences):
            summarize_text.append(" ".join(ranked_sentence[i][1]))
        # Step 5 - Offcourse, output the summarize texr
        #print("Summarize Text: \n", ". ".join(summarize_text))
        return "\n".join(summarize_text)
    
    def sentence_similarity(self, sent1, sent2, stopwords_=None):    
        vectors = self.sentence_similarity_dict.get(tuple(sent1 + sent2), None)
        
        if vectors is not None:
            vector1 = vectors[0]
            vector2 = vectors[1]
            
        else:
            if stopwords_ is None:        
                stopwords_ = []     
            sent1_new = [w.lower() for w in sent1]    
            sent2_new = [w.lower() for w in sent2]     
            all_words = list(set(sent1_new + sent2_new))    
            vector1 = [0] * len(all_words)    
            vector2 = [0] * len(all_words)     
            # build the vector for the first sentence   
            for w in sent1_new:       
                if w in stopwords_:            
                    continue        
                vector1[all_words.index(w)] += 1     
            # build the vector for the second sentence    
            for w in sent2_new:        
                if w in stopwords_:           
                    continue        
                vector2[all_words.index(w)] += 1     
            self.sentence_similarity_dict[tuple(sent1 + sent2)] = (vector1, vector2)
            self.sentence_similarity_dict[tuple(sent2 + sent1)] = (vector2, vector1)
        
        return 1 - cosine_distance(vector1, vector2)
    
    def build_similarity_matrix(self, sentences, stop_words):
        # Create an empty similarity matrix
        similarity_matrix = np.zeros((len(sentences), len(sentences)))
     
        for idx1 in range(len(sentences)):
            for idx2 in range(len(sentences)):
                if idx1 == idx2: #ignore if both are same sentences
                    continue 
                similarity_matrix[idx1][idx2] = self.sentence_similarity(sentences[idx1], sentences[idx2], stop_words)
        
        return similarity_matrix


if __name__ == '__main__':
    from research_finder import ResearchFinder
    rf = ResearchFinder()
    rf.load_data(kaggle=False)
#    data = rf.get_data()
#    citation_dict = rf.get_citation_dict()
#    rf.store_data()
    test_papers = rf.find_paper(['coronavirus', 'risk', 'factor', 'covid'])
    best_title = test_papers['init_title'].iloc[0]
    summary = rf.summarize_paper(test_papers['init_body_text'].iloc[0], 7)
    