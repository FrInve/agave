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
    relations: List[ Cooccurrence ] = field(default_factory=list)
    entities: List[Entity] = field(default_factory=list)

@dataclass
class ContainmentBox:
    chains: List[ Chain ] = field(default_factory=list)

@dataclass
class GraphicalAbstract:
    chains: List[ Chain ] = field(default_factory=list)
    boxes: List[ ContainmentBox ] = field(default_factory=list)
    entities: List[Entity] = field(default_factory=list)
    relations: List[Cooccurrence] = field(default_factory=list)

    def add_entity(self, entity):
        self.entities.append(entity)
    
    def add_relation(self, entity_1, entity_2, relation_class):
        self.relations.append(Cooccurrence(entity_1, entity_2))

    def add_chain(self):
        self.chains.append(Chain())
    
    def add_box(self):
        self.boxes.append(ContainmentBox)