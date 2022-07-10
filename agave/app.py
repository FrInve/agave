from agave.engine.data_access_layer import CooccurrencyGraph, PaperCache, Metadata
from agave.engine.query_manager import MichaelScott as Manager
from agave.conf import CONFIG

class Agave:
    def __init__(self):
        self.conf = CONFIG
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
