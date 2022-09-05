from typing import Type
import pandas as pd

class Gatherer:
    def __init__(self, metadata, cache):
        self.metadata = metadata
        self.cache = cache
        #self.papers = {}
        self.papers = PapersRegistry()
        self.extracted_papers = pd.DataFrame(data=None, columns=['cord_uid','title','abstract','doi','authors','journal','publish_time','occurrences','explained_relations'])
    
    def add_papers_from_bigram(self, bigram: str, original: bool, meta_relation: str):
        uids = self.cache.get_papers_by_bigram(bigram)
        self.papers.add(uids, bigram, original, meta_relation)
        #try:
        #    self.papers[meta_relation]
        #except KeyError:
        #    self.papers[meta_relation] = {bigram:[]}
        #finally: 
        #    self.papers[meta_relation][bigram] = {'original':original, 'uids':uids}
        #print(self.papers.get_all_uids())
    
    def _extract_papers(self):
        # Initialize the structure again
        self.extracted_papers = pd.DataFrame(data=None, columns=self.extracted_papers.columns)
        grouped = self.papers.groupby(by=['cord_uid']).count()
        uids = grouped.reset_index().cord_uid.tolist()
        papers = self.metadata.get_papers(uids)
        for paper in papers:
            new_row = pd.DataFrame(data=[paper], columns=self.extracted_papers.columns)
            new_row = new_row.set_index('cord_uid')
            new_row.occurrences = grouped.relation
            new_row = new_row.reset_index()
            relations = self.papers[self.papers.cord_uid == paper['cord_uid']].relation.tolist()
            new_row.explained_relations = str(relations)
            self.extracted_papers = pd.concat([self.extracted_papers, new_row], ignore_index=True)
    
    def extract_papers(self):
        self.extracted_papers = pd.DataFrame(data=None, columns=self.extracted_papers.columns)
        self.papers.count_uids()
        papers = self.metadata.get_papers(list(self.papers.counted_uids.index))
#        for paper in papers:
#            new_row = pd.DataFrame(data=[paper], columns=self.extracted_papers.columns)
#            new_row.occurrences = self.papers.counted_uids[paper['cord_uid']]
#            new_row.explained_relations = str(self.papers.get_relations(paper['cord_uid']))
#            self.extracted_papers = pd.concat([self.extracted_papers, new_row], ignore_index=True)
        papers['occurrences'] = papers.cord_uid.apply(lambda x: self.papers.counted_uids[x])
        papers['explained_relations'] = papers.cord_uid.apply(lambda x: self.papers.get_relations(x))
        self.extracted_papers = papers



    
#    def get_paper_by_cord_uid(self, cord_uid):
#        return self.extracted_papers[self.extracted_papers.cord_uid == cord_uid]
#    
#    def get_paper_by_doi(self, doi):
#        return self.extracted_papers[self.extracted_papers.doi == doi]
#    
#    def get_papers_by_relation(self, relation):
#        uids = self.papers[self.papers.relation == relation].cord_uid.tolist()
#        result = self.extracted_papers[self.extracted_papers.cord_uid.isin(uids)]
#        return result
#    
#    def get_papers_by_meta_relation(self, meta_relation):
#        uids = self.papers[self.papers.meta_relation == meta_relation].cord_uid.tolist()
#        result = self.extracted_papers[self.extracted_papers.cord_uid.isin(uids)]
#        return result

class PapersRegistry:
    def __init__(self):
        self.meta_relations = {} # Structure: meta_relations[meta_relation][bigram]['uids'][uid] -> True
        self.counted_uids = pd.Series().value_counts()
        self.paper_bigrams = {}
    
    def add(self, uids: list[str], bigram: str, original: bool, meta_relation: str):
        try:
            self.meta_relations[meta_relation]
        except KeyError:
            self.meta_relations[meta_relation] = {bigram:[]}
        finally: 
            self.meta_relations[meta_relation][bigram] = {'original':original, 'uids':{uid:True for uid in uids}}

        for uid in uids:
            try:
                self.paper_bigrams[uid]
            except KeyError:
                self.paper_bigrams[uid] = []
            finally:
                self.paper_bigrams[uid].append(bigram)
    
    def get_uids(self, bigram: str, meta_relation: str) -> list[str]:
        try:
            return self.meta_relations[meta_relation][bigram]['uids'].keys()
        except KeyError:
            return []
    
    def get_all_uids(self):
        result = []
        for m in self.meta_relations.keys():
            for b in self.meta_relations[m].keys():
                result += list(self.meta_relations[m][b]['uids'].keys())
        return result
    
    def count_uids(self):
        self.counted_uids = pd.Series(self.get_all_uids()).value_counts()
    
    def get_relations(self, paper):
        return self.paper_bigrams[paper]

        

# --------------------------------------------------------

class Stoner:
    def __init__(self, graph_db):
        self.graph_db = graph_db
        self.meta_path = {}
        self.selected_path = []
    
    def get_meta_path(self, chain, npmi_thr:float=0):
        #self.meta_path = {}
        for first, second in zip(chain, chain[1:]):
           ms = MetaSegment(first, second)
           ms.shortest_paths=self.graph_db.get_shortest_paths(first, second, npmi_thr)
           self.meta_path[str(ms)] = ms
    
    def get_meta_paths(self, chains):
        for chain in chains:
            self.get_meta_path(chain)
    
    def show_meta_paths(self):
        for segment in self.meta_path.values():
            segment.show_paths()
            print('-------------------------')
    
    def select_path(self,indexes):
        self.selected_path = []
        for position, segment in enumerate(self.meta_path.values()):
            self.selected_path.append(segment.select_path(indexes[position]))
    
    def show_selected_path(self):
        #for segment in self.meta_path.values():
        #    segment.show_selected_path()
        segment_names = [str(x) for x in self.meta_path.values()]
        idx=0
        # Fix empty segments
        self.selected_path = [(-1, 'SKIP') if elem is None else elem for elem in self.selected_path]
        for i, segment in self.selected_path:
            if i==-1:
                print(segment_names[idx])
                print('SKIP')
                print('--------------------------')
                idx+=1
                continue
        # Go on with common behaviour
            print(segment_names[idx])
            print(i, segment.relationships)
            print('--------------------------')
            idx+=1
    
    def get_segment_names(self):
        return [str(x) for x in self.meta_path.values()]

    def get_selected_path_relations(self):
        return [x[1].relationships for x in self.selected_path]  


class MetaSegment:
    def __init__(self, head, tail):
        self.head=head
        self.tail=tail
        self.shortest_paths=None
        self.selected_path=None
    
    def show_paths(self):
        print(str(self))
        for idx, record in enumerate(self.shortest_paths.records):
            print(str(idx), record.relationships, '\t\t\t',record.avg_npmi)

            if idx >= 10:
                break

    def __str__(self):
        return self.head + '-->' + self.tail

    def select_path(self, index):
        for idx, record in enumerate(self.shortest_paths.records):
            if idx == index:
                self.selected_path=record
                return idx, record

    def show_selected_path(self):
        print(str(self))
        print(self.selected_path)
        #print(str(self.selected_path[0]) + '\t' + self.selected_path[1].relationships )
            
