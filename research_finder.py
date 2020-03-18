# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 21:45:45 2020

@author: Radin
"""

import pandas as pd
import json
import glob

class ResearchFinder():
    """
    Class that will return a list of articles related to the query, ranked by
    importance and relevance
    Will also return a summary of an article
    """
    
    def __init__(self):
        self.all_metadata = None
        self.all_jsons = None
        self.data = None
        
    def json_parser(self, file_path):
        """
        Given a JSON filepath, returns dictionary containing relevant paper data
        """
        with open(file_path) as file:
            parsed_data = {}
            data = json.load(file)
            parsed_data['paper_id'] = data['paper_id']
            parsed_data['title'] = data['metadata']['title']
            abstract = []
            body_text = []
            bib_entries = []
            for paragraph in data['abstract']:
                abstract.append(paragraph['text'])
            for paragraph in data['body_text']:
                body_text.append(paragraph['text'])
            for citation in data['bib_entries'].values():
                bib_entries.append(citation['title'])
            parsed_data['abstract'] = '\n'.join(abstract)
            parsed_data['body_text'] = '\n'.join(body_text)
            parsed_data['bib_entries'] = bib_entries
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
                        'bib_entries': []
                        }
            for i, file_path in enumerate(self.all_jsons):
                if i % (len(self.all_jsons) // 10) == 0:
                    print(f'Processing index: {i} of {len(self.all_jsons)}')
                article_data = self.json_parser(file_path)
                data_dict['paper_id'].append(article_data['paper_id'])
                data_dict['title'].append(article_data['title'])
                data_dict['abstract'].append(article_data['abstract'])
                data_dict['body_text'].append(article_data['body_text'])
                data_dict['bib_entries'].append(article_data['bib_entries'])
                
            self.data = pd.DataFrame(data_dict, columns=['paper_id',
                                                         'title',
                                                         'abstract', 
                                                         'body_text',
                                                         'bib_entries'])
        return self.data
    
if __name__ == '__main__':
    rf = ResearchFinder()
    data = rf.get_data()