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