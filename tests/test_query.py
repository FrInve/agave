from agave.query import *

def test_create_graphical_abstract():
    g = GraphicalAbstract()
    assert len(g.chains) == 0
    assert len(g.boxes) == 0

def test_add_chain():
    g = GraphicalAbstract()
    g.add_chain()
    assert len(g.chains) == 1

def test_add_entities():
    g = GraphicalAbstract()
    e0 = Entity("First", "LABEL1")
    e1 = Entity("Second", "LABEL2")
    g.add_entity(e0)
    g.add_entity(e1)
    assert g.entities[0].name == "First"
    assert g.entities[1].name == "Second"

def test_add_relation():
    g = GraphicalAbstract()
    e0 = Entity("First", "LABEL1")
    e1 = Entity("Second", "LABEL2")
    g.add_entity(e0)
    g.add_entity(e1)
    g.add_relation(e0, e1, Cooccurrence)
    assert len(g.relations) == 1
    assert g.relations[0].object_1 is e0
    assert g.relations[0].object_2 is e1

def test_build_chains():
    g = GraphicalAbstract()
    e0 = Entity("First", "LABEL1")
    e1 = Entity("Second", "LABEL2")
    e2 = Entity("Third", "LABEL3")
    g.add_entity(e0)
    g.add_entity(e1)
    g.add_entity(e2)
    g.add_relation(e0, e1, Cooccurrence)
    g.add_relation(e1, e2, Cooccurrence)
    g.build_chains(e0)
    assert len(g.chains) == 1
    assert g.chains[0].start is e0
    assert g.chains[0].end is e1

    
    

