import neo4j
import logging
from neo4j import GraphDatabase
import pickledb
import pandas as pd
import sqlite3

class CooccurrencyGraph:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def test_connection(self):
        with self.driver.session() as session:
            try:
                result = session.read_transaction(self._test_connection)
                print("Connection established")
            except Exception:
                print("Not connected to Neo4J! \nCheck authentication and connection")

    @staticmethod
    def _test_connection(tx):
        result = tx.run("MATCH () RETURN 1 LIMIT 1")
        return result

    def get_shortest_paths(self, head, tail):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._get_shortest_paths, head, tail)
            return result

    @staticmethod
    def _get_shortest_paths(tx, head, tail):
        query = (
            "MATCH p=allshortestpaths((a)-[*]-(b))"
            " WHERE a.entity=$head AND b.entity=$tail"
            " UNWIND p AS path"
            " UNWIND relationships(path) AS rela"
            " WITH path AS path,"
            "      avg(rela.frequency) AS average_relationship_frequency,"
            "      collect(rela.name) AS relas"
            " WHERE average_relationship_frequency > 1"
            " RETURN path, average_relationship_frequency, relas"
            " ORDER BY average_relationship_frequency DESC"
        )
        result = tx.run(query, head=head, tail=tail)
        out = ShortestPathsResult(result)
        return out


class ShortestPathsResult:
    def __init__(self, result):
        self.graph = result.graph()
        self.records = []
        for record in list(result):
            self.records.append(ShortestPathsRecord(record))

class ShortestPathsRecord:
    def __init__(self, record):
        self.path = record['path']
        self.avg_pwmi = record['average_relationship_frequency']
        self.relationships = record['relas']
    
    def __repr__(self):
        return str(self.path)
    
    def get_meta_path_name(self):
        return str(self.path.start_node['entity'])+'-->'+str(self.path.end_node['entity'])

# -----------------------------------------------------
class PaperCache:
    def __init__(self, path_entity, path_bigram):
        self.by_entity = pickledb.load(path_entity, False)
        self.by_bigram = pickledb.load(path_bigram, False)
    
    def get_papers_by_bigram(self, bigram):
        return self.by_bigram.get(bigram)
    
    def get_papers_by_bigrams(self, bigrams):
        result = {}
        for bigram in bigrams:
            result[bigram] = self.get_papers_by_bigram(bigram)
        return result



# ------------------------------------------------------

class Metadata:
    def __init__(self, metadata_csv_path, sample=False):
        if sample:
            self.df = pd.read_csv(metadata_csv_path, nrows=10000)
        else:
            self.df = pd.read_csv(metadata_csv_path)
        self.df['publish_time'] = pd.to_datetime(self.df['publish_time'])
        self.df = self.df.set_index('cord_uid')

    def get_paper(self, cord_uid):
        try:
            result = self.df.loc[cord_uid].to_dict()
            result['cord_uid'] = cord_uid
            return result
        except KeyError:
            return
    
    def get_papers(self, cord_uids):
        result = [self.get_paper(cord_uid) for cord_uid in cord_uids]
        return [elem for elem in result if elem is not None]