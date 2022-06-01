from agave.query import *

def test_graphical_abstract_init():
    g = GraphicalAbstract()
    assert not hasattr(g, '__graph')
    assert g._GraphicalAbstract__graph != None

def test_add_entity():
    g = GraphicalAbstract()
    e = Entity('first', 'label0')
    g.add_entity(e)
    assert list(g._GraphicalAbstract__graph.nodes)[0] is e

def test_add_relation():
    g = GraphicalAbstract()
    e = Entity('first', 'label0')
    e0 = Entity('second', 'label1')
    g.add_entity(e)
    g.add_entity(e0)
    g.add_relation(e, e0, 'cooccurrence')
    assert list(g._GraphicalAbstract__graph.edges)[0] == (e, e0)
    assert g._GraphicalAbstract__relations['first<->second'] == 'cooccurrence'

def test_list_relations():
    g = GraphicalAbstract()
    e = Entity('first', 'label0')
    e0 = Entity('second', 'label1')
    g.add_entity(e)
    g.add_entity(e0)
    g.add_relation(e, e0, 'cooccurrence')
    print(g.list_relations())
    print("HEYHEYHEY")
    assert g.list_relations()
