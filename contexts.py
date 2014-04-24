import networkx
from phrases import NounPhrase, VerbPhrase, Descriptor

class Context:
  def __init__(self):
    self.clauseTable = dict()
    self.componentGraph = networkx.DiGraph()
    self.actionGraph = networkx.DiGraph()
    self.stateGraph = networkx.Graph()
    self._concepts = {'noun_phrases': set(), 'verb_phrases': set(), 'descriptors': set()}
  
  def checkClause(self, clause):
    if clause in self.clauseTable:
      return self.clauseTable[clause]
    else:
      return False

  def newNounPhrase(self, nounPhrase):
    concept = NounPhrase(nounPhrase)
    self.componentGraph.add_node(concept)
    self.actionGraph.add_node(concept)
    self.stateGraph.add_node(concept)
    self._concepts['noun_phrases'].add(concept)
  
  def newVerbPhrase(self, verbPhrase):
    concept = VerbPhrase(verbPhrase)
    self.actionGraph.add_node(concept)
    self.stateGraph.add_node(concept)
    self._concepts['verb_phrases'].add(concept)
  
  def newDescriptor(self, descriptor):
    concept = Descriptor(descriptor)
    self.stateGraph.add_node(descriptor)
    self._concepts['descriptor'].add(concept)
  
  def setAction(self, actor, act, target):
    self.actionGraph.add_edge(actor, act)
    self.actionGraph.add_edge(act, target)
    if self.relationshipGraph.get_edge_
    self.relationshipGraph.add_edge(actor, target)
    
  def unsetAction(self, actor, act, target=None):
    if target:
      self.actionGraph.remove_edge(act, target)
    if len(self.actionGraph.out_edges(act)) == 0:
        self.actionGraph.remove_edge(actor, act)
        self._concepts['verb_phrases'].remove(act)
        self.stateGraph.remove_node(act)
        self.actionGraph.remove_node(act)
  
  def setComponent(self, parent, label, child=None):
    if child:
      self.componentGraph.add_edge(parent, child, label=label)
    else:
      child = self.newNounPhrase(label)
      self.componentGraph.add_edge(parent, child, label=label)
      
  def unsetComponent(self, parent, child):
    self.componentGraph.remove_edge(parent, child)
  
  def setState(self, subject, descriptor):
    state = self.newDescriptor(descriptor)
    self.stateGraph.add_edge(subject, state)

  def unsetState(self, subject, state):
    state.stateGraph.remove_edge(subject, state)
    self._concepts['descriptors'].remove(state)
    self.stateGraph.remove_node(state)
    
  def mergeConcepts(self, concept1, concept2):
    #TODO: write this merge method
    if isinstance(concept1, NounPhrase) and isinstance(concept2, NounPhrase):
    elif isinstance(concept1, VerbPhrase) and isinstance(concept2, VerbPhrase):
    elif isinstance(concept1, Descriptor) and isinstance(concept2, Descriptor):
  
  def queryNounPhrases(self, type):
    response = list()
    for concept in self._concepts['noun_phrases']:
      if concept.name == type or concept.paternityTest(type):
        response.append(concept)
        
  def queryVerbPhrases(self, type):
    response = list()
    for concept in self._concepts['verb_phrases']:
      if concept.name == type or concept.paternityTest(type):
        response.append(concept)    
  
  def queryDescriptor(self, type):
    response = list()
    for concept in self._concepts['descriptor']:
      if concept.name == type or concept.paternityTest(type):
        response.append(concept)
  
  
      
    