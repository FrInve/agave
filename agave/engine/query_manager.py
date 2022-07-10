from agave.engine.engine import Stoner, Gatherer

class MichaelScott:
    def __init__(self, metadata, paper_cache, graph_db):
        self.stoner = Stoner(graph_db)
        self.gatherer = Gatherer(metadata, paper_cache)
        self.query = []


    def find_single_chain(self, entities):
        self.stoner.get_meta_path(entities)
    
    def show_single_chain_result(self):
        self.stoner.show_meta_paths()
    
    def select_path_single_chain(self, path_idxs):
        '''
        This indexes are the same shown in show_single_chain_result
        '''
        self.stoner.select_path(path_idxs)
        self.stoner.show_selected_path()

    def find_graphical_abstract(self, ga):
        for chain in ga.chains:
            self.stoner.get_meta_path(chain)
    
    def gather_papers(self):
        """
        DEPRECATED!
        """
        for segment in self.stoner.get_selected_path_relations():
            for relation in segment:
                if relation == segment[0] or relation == segment[-1]:
                    original = True
                else:
                    original = False
                self.gatherer.add_papers_from_bigram(relation, original, str(segment))
        self.gatherer.extract_papers()
    
    def _gather_papers(self):
        for record_tuple in self.stoner.selected_path:
            record = record_tuple[1]
            segment = record.relationships
            for relation in segment:
                if relation == segment[0] or relation == segment[-1]:
                    original = True
                else:
                    original = False
                self.gatherer.add_papers_from_bigram(relation, original, record.get_meta_path_name())
        self.gatherer.extract_papers()