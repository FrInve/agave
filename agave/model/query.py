from dataclasses import dataclass, field
from typing import List
import networkx as nx

@dataclass
class UnaryPredicate:
    name: str

@dataclass(eq=True, frozen=True)
class Entity:
    name: str = field(compare=True)
    label: str = field(compare=False)
    predicates : List[UnaryPredicate] = field(compare=False,default_factory=list)

class Cooccurrence:
    def __init__(self, entity_1, entity_2):
        self.first_entity = entity_1 if entity_1.name < entity_2.name else entity_2
        self.second_entity = entity_2 if entity_2.name > entity_1.name else entity_1
        self.relation_type = "cooccurrence"

    def get_id(self):
        return str(self.first_entity.name)+'<->'+str(self.second_entity.name)

@dataclass
class Chain:
    relations: List[ Cooccurrence ] = field(default_factory=list)
    entities: List[Entity] = field(default_factory=list)

@dataclass
class ContainmentBox:
    chains: List[Entity] = field(default_factory=list)

class GraphicalAbstract:

    def __init__(self):
        self.__graph = nx.Graph()
        self.__relations = {}
        self.__containment_boxes = []

    def add_entity(self, entity):
        self.__graph.add_node(entity)

    def add_relation(self, entity_1, entity_2, relation_str):
        relation = Cooccurrence(entity_1, entity_2)
        self.__relations[relation.get_id()] = relation_str
        self.__graph.add_edge(relation.first_entity, relation.second_entity)

    def list_relations(self):
        return self.__relations.items()
