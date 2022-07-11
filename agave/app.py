from agave.engine.data_access_layer import CooccurrencyGraph, PaperCache, Metadata
from agave.engine.query_manager import MichaelScott as Manager
from agave.conf import CONFIG
from agave.model.query import GraphicalAbstract
class Agave:
    def __init__(self, conf_dict=CONFIG, chains=[]):
        self.conf = conf_dict
        self.graphical_abstract = GraphicalAbstract(chains)
        print(self.conf)
    
    def _connect_graph_db(self):
        self.graph_db = CooccurrencyGraph(self.conf['graph_db_uri'],
                                        self.conf['graph_db_user'],
                                        self.conf['graph_db_password'])
        self.graph_db.test_connection()
    
    def _connect_database(self):
        self.metadata = Metadata(self.conf['database_string'])
        self.paper_cache = PaperCache(self.conf['database_string'])
    
    def initialize(self):
        self._connect_graph_db()
        self._connect_database()
        self.manager = Manager(self.metadata, self.paper_cache, self.graph_db)
    
    def find_name(self,name):
        res = self.manager.stoner.graph_db.resolve_name(name)
        print(res)
        return res
    
    def find_graphical_abstract(self):
        self.manager.find_graphical_abstract(self.graphical_abstract)
    
    def show_found_paths(self):
        self.manager.show_found_paths()
    
    def select_path(self, selected_idxs):
        self.manager.select_path(selected_idxs)
    
    def autoselect_path(self):
        indexes_len = len(self.manager.stoner.get_segment_names())
        self.manager.select_path([0]*indexes_len)

