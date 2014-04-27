import re
import networkx
from concepts import Concept
from phrases import NounPhrase, VerbPhrase, Descriptor
import utilities

class Context:
  def __init__(self):
    self.clauseTable = dict()
    self.componentGraph = networkx.DiGraph()
    self.actionGraph = networkx.DiGraph()
    self.stateGraph = networkx.DiGraph()
    self._concepts = {'noun_phrases': set(), 'verb_phrases': set(), 'descriptors': set()}
  
  def checkClause(self, clause):
    if clause in self.clauseTable:
      return self.clauseTable[clause]
    else:
      return False
  
  def incorporateConcept(self, concept):
    if isinstance(concept, NounPhrase):
      self.componentGraph.add_node(concept)
      self.actionGraph.add_node(concept)
      self.stateGraph.add_node(concept)
      self._concepts['noun_phrases'].add(concept)
    elif isinstance(concept, VerbPhrase):
      self.actionGraph.add_node(concept)
      self.stateGraph.add_node(concept)
      self._concepts['verb_phrases'].add(concept)
    elif isinstance(concept, Descriptor):
      self.stateGraph.add_node(concept)
      self._concepts['descriptors'].add(concept)

  def newNounPhrase(self, nounPhrase, type=None):
    for concept in self._concepts['noun_phrases']:
      if concept.name == nounPhrase: return concept
    if type:
      concept = NounPhrase(nounPhrase, type)
    else:
      concept = NounPhrase(nounPhrase)
    self.incorporateConcept(concept)
    return concept
  
  def newVerbPhrase(self, verbPhrase):
    concept = VerbPhrase(None, verbPhrase)
    self.incorporateConcept(concept)
    return concept
  
  def newDescriptor(self, descriptor):
    concept = Descriptor(None, descriptor)
    self.incorporateConcept(concept)
    return concept
  
  def remove(self, concept):
    concept.taxonomy.remove(utilities.sanitize(concept.name))
    if concept in self.actionGraph: self.actionGraph.remove_node(concept)
    if concept in self.stateGraph: self.stateGraph.remove_node(concept)
    if concept in self.componentGraph: self.componentGraph.remove_node(concept)
    if concept in self._concepts['noun_phrases']: self._concepts['noun_phrases'].remove(concept)
    if concept in self._concepts['verb_phrases']: self._concepts['verb_phrases'].remove(concept)
    if concept in self._concepts['descriptors']: self._concepts['descriptors'].remove(concept)
  
  def setAction(self, actor, act, target=None):
    if self.actionGraph.successors(actor) and self.actionGraph.predecessors(target):
      sharedActs = set(self.actionGraph.successors(actor)).intersection(set(self.actionGraph.predecessors(target)))
      for sharedAct in sharedActs:
        if act.parents().intersection(sharedAct.parents()): 
          self.remove(act)
          return False
    self.actionGraph.add_edge(actor, act)
    if target:
      self.actionGraph.add_edge(act, target)
    
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
    self.stateGraph.add_edge(subject, descriptor)

  def unsetState(self, subject, state):
    state.stateGraph.remove_edge(subject, state)
    self._concepts['descriptors'].remove(state)
    self.stateGraph.remove_node(state)
    
  def mergeConcepts(self, concept1, concept2):
    names = (concept1.name, concept2.name)
    if isinstance(concept1, NounPhrase) and isinstance(concept2, NounPhrase):
      mergedConcept = self.newNounPhrase(names[1]) if re.match('.+_.+', names[0]) else self.newNounPhrase(names[0])
    elif isinstance(concept1, VerbPhrase) and isinstance(concept2, VerbPhrase):
      mergedConcept = self.newVerbPhrase(names[1]) if re.match('.+_.+', names[0]) else self.newVerbPhrase(names[0])
    elif isinstance(concept1, Descriptor) and isinstance(concept2, Descriptor):
      mergedConcept = self.newDescriptor(names[1]) if re.match('.+_.+', names[0]) else self.newDescriptor(names[0])
    else:
      raise Exception('mergeConcepts: Unmatching phrase types')
    concept1.equate(concept2.name)
    for parent in concept1.parents():
      mergedConcept.classify(parent)
    for parent in concept2.parents():
      mergedConcept.classify(parent)
    graphs = [self.actionGraph, self.componentGraph, self.stateGraph]
    concepts = [concept1, concept2]
    for concept in concepts:
      for graph in graphs:
        if concept in graph:
          in_edges = graph.in_edges(concept, data=True)
          out_edges = graph.out_edges(concept, data=True)
          for edge in in_edges:
            graph.add_edge(edge[0], mergedConcept, edge[2])
          for edge in out_edges:
            graph.add_edge(mergeConcept, edge[1], edge[2])
    self.remove(concept1)
    self.remove(concept2)
    return mergedConcept
          
  def queryNounPhrases(self, type):
    type = utilities.camelCase(type)
    exactMatch = self.queryExact(type, phraseType='NounPhrase')
    if exactMatch: return {exactMatch}
    response = set()
    for concept in self._concepts['noun_phrases']:
      if concept.isA(type):
        response.add(concept)
    return response
        
  def queryVerbPhrases(self, type):
    type = utilities.camelCase(type)
    exactMatch = self.queryExact(type, phraseType='VerbPhrase')
    if exactMatch: return {exactMatch}
    response = set()
    for concept in self._concepts['verb_phrases']:
      if concept.isA(type):
        response.add(concept)
    return response        
  
  def queryDescriptors(self, type):
    type = utilities.camelCase(type)
    exactMatch = self.queryExact(type, phraseType='Descriptor')
    if exactMatch: return {exactMatch}
    response = set()
    for concept in self._concepts['descriptor']:
      if concept.isA(type):
        response.add(concept)
    return response
  
  def queryExact(self, name, phraseType=None):
    nameSynonyms = Concept().synonyms(name)
    if not phraseType or phraseType == 'NounPhrase':
      for concept in self._concepts['noun_phrases']:
        if concept.name in nameSynonyms:
          return concept
    if not phraseType or phraseType == 'VerbPhrase':
      for concept in self._concepts['verb_phrases']:
        if concept.name in nameSynonyms:
          return concept
    if not phraseType or phraseType == 'Descriptor':
      for concept in self._concepts['descriptors']:
        if concept.name in nameSynonyms:
          return concept
    return None
        
  def __contains__(self, concept):
    if concept in self._concepts['noun_phrases']:
      return True
    elif concept in self._concepts['verb_phrases']:
      return True
    elif concept in self._concepts['descriptors']:
      return True
    else:
      return False
  
      
    