from agave.engine.engine import Stoner, Gatherer

class MichaelScott:
    def __init__(self, metadata, paper_cache, graph_db):
        self.stoner = Stoner(graph_db)
        self.gatherer = Gatherer(metadata, paper_cache)
        self.query = []


    def find_single_chain(self, entities,npmi_thr:float=0):
        self.stoner.get_meta_path(entities, npmi_thr)
    
    def show_single_chain_result(self):
        self.stoner.show_meta_paths()
    
    def select_path(self, path_idxs):
        '''
        This indexes are the same shown in show_single_chain_result
        '''
        self.stoner.select_path(path_idxs)
        self.stoner.show_selected_path()

    def find_graphical_abstract(self, ga, npmi_thr: float=0):
        for chain in ga.chains:
            self.stoner.get_meta_path(chain,npmi_thr)
    
    def show_found_paths(self):
        self.stoner.show_meta_paths()
    
    def _gather_papers(self):
        for record_tuple in self.stoner.selected_path:
            if record_tuple[0] == -1: #Check if path is missing
                continue
            record = record_tuple[1]
            segment = record.relationships
            for relation in segment:
                if relation == segment[0] or relation == segment[-1]:
                    original = True
                else:
                    original = False
                self.gatherer.add_papers_from_bigram(relation, original, record.get_meta_path_name(), record.avg_npmi)
        self.gatherer.extract_papers()