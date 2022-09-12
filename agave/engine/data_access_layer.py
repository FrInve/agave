from neo4j import GraphDatabase
import pandas as pd
from sqlalchemy import create_engine, insert, Column, MetaData, Table, String
import json


class CooccurrencyGraph:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        self.driver.close()

    def test_connection(self) -> None:
        with self.driver.session() as session:
            try:
                result = session.read_transaction(self._test_connection)
                print("Connected to graph db")
            except Exception:
                print("Not connected to Neo4J! \nCheck authentication and connection")

    @staticmethod
    def _test_connection(tx):
        result = tx.run("MATCH () RETURN 1 LIMIT 1")
        return result

    def get_shortest_paths(self, head: str, tail: str, npmi_thr:float):
        with self.driver.session() as session:
            result = session.read_transaction(self._get_shortest_paths, head, tail, npmi_thr)
            return result

    @staticmethod
    def _get_shortest_paths(tx, head: str, tail: str, npmi_thr: float=0):
        #        query = (
        #            "MATCH p=allshortestpaths((a)-[*]-(b))"
        #            " WHERE a.entity=$head AND b.entity=$tail"
        #            " UNWIND p AS path"
        #            " UNWIND relationships(path) AS rela"
        #            " WITH path AS path,"
        #            "      avg(rela.frequency) AS average_relationship_frequency,"
        #            "      collect(rela.name) AS relas"
        #            " WHERE average_relationship_frequency > 1"
        #            " RETURN path, average_relationship_frequency, relas"
        #            " ORDER BY average_relationship_frequency DESC"
        #        )
        query = (
            "MATCH p=allshortestpaths((a)-[*]-(b))"
            " WHERE a.name=$head AND b.name=$tail"
            " UNWIND p AS path"
            " UNWIND relationships(path) AS rela"
            " WITH path AS path,"
            "      avg(rela.npmi) AS average_relationship_npmi,"
            "      collect(rela.name) AS relas"
            " WHERE average_relationship_npmi > $npmi_thr"
            " RETURN path, average_relationship_npmi, relas"
            " ORDER BY average_relationship_npmi DESC"
        )
        result = tx.run(query, head=head, tail=tail, npmi_thr=npmi_thr)
        out = ShortestPathsResult(result)
        return out

    def resolve_name(self, _name: str):
        with self.driver.session() as session:
            result = session.read_transaction(self._resolve_name, _name)
            return result

    @staticmethod
    def _resolve_name(tx, _name: str):
        query = (
            "MATCH (a) WHERE a.name =~ '.*(?i)%s.*' RETURN a.name, a.umls_id, a.frequency"
            % _name
        )
        result = tx.run(query, name=_name)
        result = [
            {
                "name": record["a.name"],
                "umls_id": record["a.umls_id"],
                "frequency": record["a.frequency"],
            }
            for record in list(result)
        ]
        return result


class ShortestPathsResult:
    def __init__(self, result):
        self.graph = result.graph()
        self.records = []
        for record in list(result):
            self.records.append(ShortestPathsRecord(record))


class ShortestPathsRecord:
    def __init__(self, record):
        self.path = record["path"]
        self.avg_npmi = record["average_relationship_npmi"]
        self.relationships = record["relas"]

    def __repr__(self) -> str:
        return str(self.path)

    def get_meta_path_name(self) -> str:
        return (
            str(self.path.start_node["name"]) + "-->" + str(self.path.end_node["name"])
        )


# -----------------------------------------------------
class PaperCache:
    def __init__(self, db_string):
        self.engine = create_engine(db_string)
        try:
            with self.engine.connect() as con:
                con.execute("SELECT * FROM bigram_paper LIMIT 1").fetchall()
                print("Connected to paper cache")
        except Exception:
            print("I can't connect to paper cache")
            raise

    def get_papers_by_bigram(self, bigram: str):
        query = """
        SELECT papers
        FROM bigram_paper
        WHERE bigram = '%s'
        """ % str(
            bigram
        )
        try:
            with self.engine.connect() as con:
                result = con.execute(query).fetchall()
                return json.loads(result[0][0])
        except Exception:
            return []

    def get_papers_by_bigrams(self, bigrams: list[str]) -> dict:
        result = {}
        for bigram in bigrams:
            result[bigram] = self.get_papers_by_bigram(bigram)
        return result


# ------------------------------------------------------


class Metadata:
    def __init__(self, db_string, sample=False):
        self.engine = create_engine(db_string)
        try:
            with self.engine.connect() as con:
                con.execute("SELECT cord_uid FROM metadata LIMIT 1").fetchall()
                print("Connected to metadata table")
        except Exception:
            print("I can't connect to metadata table")
            raise

    def get_paper(self, cord_uid):
        query = """
        SELECT *
        FROM metadata
        WHERE cord_uid = '%s'
        """ % str(
            cord_uid
        )
        try:
            result = pd.read_sql(query, self.engine)
            return result.iloc[0].to_dict()
        except Exception:
            print("Paper not found")
            return

    def get_papers(self, cord_uids):
        if len(cord_uids) == 0: # Check if input list is empty
            query = "SELECT * FROM metadata LIMIT 1"
            try:
                result = pd.read_sql(query, self.engine)
            except Exception as e:
                print(e)
                result = None
            return result[0:0]

        with self.engine.connect() as connection:
            # Create tmp table for cord_uids of papers from method parameter
            META_DATA = MetaData(bind=connection)

            cord_uids_tmp_table = Table("cord_uid_tmp", META_DATA,
            Column("cord_uid", String(30), primary_key=True),
            prefixes=['OR REPLACE TEMPORARY'],
            )

            META_DATA.create_all(connection)

            with connection.begin():
                insert_uids = connection.execute(
                    insert(cord_uids_tmp_table),
                    [{'cord_uid':cord_uid} for cord_uid in cord_uids]
                )
        
            # Left join the tmp table with the metadata table
            query = """SELECT metadata.cord_uid,
            metadata.doi,
            metadata.title,
            metadata.authors,
            metadata.abstract,
            metadata.publish_time,
            metadata.journal
            FROM cord_uid_tmp
            LEFT JOIN metadata ON cord_uid_tmp.cord_uid = metadata.cord_uid"""
            try:
                result = pd.read_sql(query, connection)
                #result = result.T.to_dict().values()
            except Exception as e:
                print(e)
                result = None
        return result
