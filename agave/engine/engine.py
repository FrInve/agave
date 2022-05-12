import pandas as pd

class Gatherer:
    def __init__(self, metadata, cache):
        self.metadata = metadata
        self.cache = cache
        self.papers = pd.DataFrame(data=None, columns=['cord_uid', 'relation','original'])
    
    def add_paper(self, cord_uid, relation, original):
        new_row = pd.DataFrame(data=[cord_uid, relation, original], columns=self.paper.columns)
        self.papers = pd.concat(self.papers, new_row)
        return new_row
    
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
    
    def select_path(indexes):
        self.selected_path = indexes
        for position, segment in enumerate(self.meta_path.values()):
            segment.select_path(indexes[position])
    
    def show_selected_path():
        return



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
            
