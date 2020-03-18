# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 21:45:45 2020

@author: Radin
"""

import pandas as pd
import json
import glob
import re
import requests

class ResearchFinder():
    """
    Class that will return a list of papers related to the query, ranked by
    importance and relevance
    Will also return a summary of an paper
    """
    
    def __init__(self):
        self.all_metadata = None
        self.all_jsons = None
        self.data = None
        self.citation_dict = None
        
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
            
            abstract = []
            body_text = []
            bib_entries = []
            
            init_abstract = []
            init_body_text = []
            
            for paragraph in data['abstract']:
                init_abstract.append(paragraph['text'])
                abstract.append(re.sub('[^a-zA-z0-9\s]',' ',paragraph['text']).lower())
            for paragraph in data['body_text']:
                init_body_text.append(paragraph['text'])
                body_text.append(re.sub('[^a-zA-z0-9\s]',' ',paragraph['text']).lower())
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
            for i, file_path in enumerate(self.all_jsons[1:100]):
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
            
        return self.data
    
    def find_paper(self, keywords):
        data = self.get_data()
        score = pd.Series(0, index=data.index)
        for keyword in keywords:
            score += 10 * data['title'].str.contains(keyword) \
                    + 5 * data['abstract'].str.contains(keyword) \
                    + 1 * data['body_text'].str.contains(keyword) 
        data = data.reindex(score.sort_values(ascending=False).index)
        data['score'] = score
        citation_dict = self.get_citation_dict()
        data['importance'] = pd.Series([citation_dict.get(x) for x in data['title']])
        return data[0:1000]
    
    def get_citation_dict(self):
        if self.citation_dict is None:
            citation_dict = {}
            data = self.get_data()
            for idx, row in data.iterrows():
                for citation in row['bib_entries']:
                    citation_dict[citation] = citation_dict.get(citation, 0) + 1
            self.citation_dict = citation_dict
        return self.citation_dict
    
    def summarize_paper(self, paper):
        api_key = 'A9BF13D6B0'
        url = 'https://api.smmry.com'
        data = self.get_data()
        text = data.loc[data['paper_id'] == paper, 'init_body_text'][0]
        PARAMS = {
                 'SM_API_KEY': api_key,
                 'sm_api_input':text,
                 'SM_URL': url}
        r = requests.get(url = url, params = PARAMS) 
        r.close()
        request_data = r.json()
        return request_data
    
    
if __name__ == '__main__':
    rf = ResearchFinder()
    data = rf.get_data()
    test_papers = rf.find_paper(['coronavirus', 'pregn'])
    citation_dict = rf.get_citation_dict()
    summary = rf.summarize_paper(test_papers.paper_id[0])