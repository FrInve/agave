from typing import Type
import pandas as pd

class Gatherer:
    def __init__(self, metadata, cache):
        self.metadata = metadata
        self.cache = cache
        #self.papers = {}
        self.papers = PapersRegistry()
        self.extracted_papers = pd.DataFrame(data=None, columns=['cord_uid','title','abstract','doi','authors','journal','publish_time','occurrences','explained_relations'])
    
    def add_papers_from_bigram(self, bigram: str, original: bool, meta_relation: str, npmi: float):
        uids = self.cache.get_papers_by_bigram(bigram)
        self.papers.add(uids, bigram, original, meta_relation, npmi)
    
    def extract_papers(self):
        self.extracted_papers = pd.DataFrame(data=None, columns=self.extracted_papers.columns)
        self.papers.count_uids()
        papers = self.metadata.get_papers(list(self.papers.counted_uids.index))
#        papers['occurrences'] = papers.cord_uid.apply(lambda x: self.papers.counted_uids[x])
        papers['explained_relations'] = papers.cord_uid.apply(lambda x: self.papers.get_relations(x))
        papers['weighted_occurrencies'] = papers.cord_uid.apply(lambda x: self.papers.get_weighted_occurrencies(x))
        papers['npmi_sum'] = papers.cord_uid.apply(lambda x: self.papers.get_npmi_sum(x))
        self.extracted_papers = papers.sort_values(by=['weighted_occurrencies','citedby_count','publish_time'], ascending=False)


class PapersRegistry:
    def __init__(self):
        self.meta_relations = {} # Structure: meta_relations[meta_relation][bigram]['uids'][uid] -> True
        self.counted_uids = pd.Series(dtype='string').value_counts()
        self.paper_bigrams = {}
    
    def add(self, uids: list[str], bigram: str, original: bool, meta_relation: str, npmi: float):
        try:
            self.meta_relations[meta_relation]
        except KeyError:
            self.meta_relations[meta_relation] = {bigram:{}, '_bigrams_count':0}
        finally: 
            self.meta_relations[meta_relation][bigram] = {'npmi':npmi, 'original':original, 'uids':{uid:True for uid in uids}}
            self.meta_relations[meta_relation]['_bigrams_count'] += 1

        for uid in uids:
            try:
                self.paper_bigrams[uid]
            except KeyError:
                self.paper_bigrams[uid] = {}
            try:
                self.paper_bigrams[uid][bigram]
            except KeyError:
                self.paper_bigrams[uid][bigram] = True
    
    def get_uids(self, bigram: str, meta_relation: str) -> list[str]:
        try:
            return self.meta_relations[meta_relation][bigram]['uids'].keys()
        except KeyError:
            return []
    
    def get_all_uids(self):
        """DEPRECATED"""
        result = []
        for m in self.meta_relations.keys():
            for b in self.meta_relations[m].keys():
                if b == '_bigrams_count':
                    continue
                result += list(self.meta_relations[m][b]['uids'].keys())
        return result
    
    def count_uids(self):
        """DEPRECATED"""
        self.counted_uids = pd.Series(self.get_all_uids()).value_counts()
    
    def get_relations(self, paper):
        return list(self.paper_bigrams[paper].keys())
    
    def get_weighted_occurrencies(self, paper):
        weighted_occurrencies = 0
        for meta_relation in self.meta_relations.keys():
            for bigram in self.meta_relations[meta_relation].keys():
                if bigram == '_bigrams_count':
                    continue
                try:
                    self.meta_relations[meta_relation][bigram]['uids'][paper]
                except KeyError:
                    continue
                weighted_occurrencies += 1/self.meta_relations[meta_relation]['_bigrams_count']
        return weighted_occurrencies
    
    def get_npmi_sum(self, paper):
        npmi_sum = 0
        for meta_relation in self.meta_relations.keys():
            for bigram in self.meta_relations[meta_relation].keys():
                if bigram == '_bigrams_count':
                    continue
                try:
                    self.meta_relations[meta_relation][bigram]['uids'][paper]
                except KeyError:
                    continue
                npmi_sum += self.meta_relations[meta_relation][bigram]['npmi']
        return npmi_sum 


        

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
            #Check if index is -1, skip this metasegment
            if indexes[position] is -1:
                continue
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
            
