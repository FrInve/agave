from dataclasses import dataclass, field
from typing import List

@dataclass
class UnaryPredicate:
    name: str

@dataclass
class Entity:
    name: str
    label: str
    predicates : List[UnaryPredicate] = field(default_factory=list)

@dataclass
class Cooccurrence:
    object_1: Entity
    object_2: Entity

@dataclass
class Chain:
    head: object = None 
    relations: List[ Cooccurrence ] = field(default_factory=list)

    def add_head(self, entity):
        if len(self.relations) == 0:
            self.head = entity
    
    def get_tail(self):
        if len(self.relations) == 0:
            return self.head
        else:
            return self.relations[-1].object_2
    
    def add_node(self, entity, relation_class):
        tail = self.get_tail()
        self.relations.append(relation_class(tail, entity))

@dataclass
class ContainmentBox:
    chains: List[ Chain ]

@dataclass
class GraphicalAbstract:
    chains: List[ Chain ]
    boxes: List[ ContainmentBox ]