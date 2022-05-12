import pandas as pd

class Gatherer:
    def __init__(self, metadata, cache):
        self.metadata = metadata
        self.cache = cache
        self.papers = pd.DataFrame(data=None, columns=['cord_uid', 'relation','original'])
    
    def add_papers_from_bigram(self, bigram, original):
        uids = self.cache.get_papers_by_bigram(bigram)
        for uid in uids:
            self.add_paper(uid, bigram, original)

    def add_paper(self, cord_uid, relation, original):
        new_row = pd.DataFrame(data={'cord_uid':cord_uid, 'relation':relation, 'original':original}, index=[0],columns=self.papers.columns)
        self.papers = pd.concat([self.papers, new_row], ignore_index=True)
        return new_row
# --------------------------------------------------------

class Stoner:
    def __init__(self, graph_db):
        self.graph_db = graph_db
        self.meta_path = {}
        self.selected_path = []
    
    def get_meta_path(self, chain):
        self.meta_path = {}
        for first, second in zip(chain, chain[1:]):
           ms = MetaSegment(first, second)
           ms.shortest_paths=self.graph_db.get_shortest_paths(first, second)
           self.meta_path[str(ms)] = ms
    
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
        for idx, segment in self.selected_path:
            print(segment_names[idx])
            print(idx, segment.relationships)
    
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
            print(str(idx), record.relationships, '\t\t\t',record.avg_pwmi)

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
            
