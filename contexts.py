import re
import datetime
import os
from collections import deque
import networkx
from concepts import Concept
from phrases import NounPhrase, VerbPhrase, Descriptor
from interpreter import Interpreter
import utilities

class Context:
  def __init__(self, name=None, universal=False):
    if name:
      self.name = name
    else:
      if universal:
        self.name = "Universal Context"
      else:
        now = datetime.datetime.now()
        self.name = 'Context from ' + str(now.month) + '/' + str(now.day) + '/' + str(now.year) + ' at ' + str(now.hour) + ':' + str(now.minute)
    self.isUniversal = universal
    self.componentGraph = networkx.DiGraph()
    self.actionGraph = networkx.DiGraph()
    self.stateGraph = networkx.DiGraph()
    self.concepts = {'noun_phrases': set(), 'verb_phrases': set(), 'descriptors': set()}
    self.conceptHashTable = dict()
    self.prototypes = dict()
    self.potentialTaxonomy = dict()
    self.potentialComponentGraph = networkx.DiGraph()
    self.potentialActionGraph = networkx.DiGraph()
    self.potentialStateGraph = networkx.DiGraph()
    self.shortTermMemory = deque(maxlen=50)
  
  def rename(self, newName):
    self.name = newName

  def incorporateConcept(self, concept, prototype=False):
    hash = os.urandom(5).encode('hex')
    self.conceptHashTable[hash] = concept
    if prototype:
      self.prototypes[concept.name] = hash
    if isinstance(concept, NounPhrase):
      self.componentGraph.add_node(concept)
      self.actionGraph.add_node(concept)
      self.stateGraph.add_node(concept)
      self.concepts['noun_phrases'].add(concept)
      self.shortTermMemory.appendleft(concept)
    elif isinstance(concept, VerbPhrase):
      self.actionGraph.add_node(concept)
      self.stateGraph.add_node(concept)
      self.concepts['verb_phrases'].add(concept)
    elif isinstance(concept, Descriptor):
      self.stateGraph.add_node(concept)
      self.concepts['descriptors'].add(concept)
      
  def newNounPhrase(self, nounPhrase):
    concept = NounPhrase(nounPhrase)
    self.incorporateConcept(concept)
    return concept
  
  def newVerbPhrase(self, verbPhrase):
    concept = VerbPhrase(verbPhrase)
    self.incorporateConcept(concept)
    return concept
  
  def newDescriptor(self, descriptor):
    concept = Descriptor(descriptor)
    self.incorporateConcept(concept)
    return concept
  
  def remove(self, concept):
    for hash in self.conceptHashTable:
      if concept is self.conceptHashTable[hash]:
        del self.conceptHashTable[hash]
        break
    if isinstance(concept, NounPhrase):
      if concept in self.shortTermMemory:
        self.shortTermMemory.remove(concept)
      if concept in self.actionGraph:
        acts = self.actionGraph.successors(concept)
        for act in acts:
          self.remove(act)
      if concept in self.stateGraph:
        descriptions = self.stateGraph.successors(concept)
        for description in descriptions:
          self.remove(description)
    if concept in self.actionGraph: self.actionGraph.remove_node(concept)
    if concept in self.stateGraph: self.stateGraph.remove_node(concept)
    if concept in self.componentGraph: self.componentGraph.remove_node(concept)
    if concept in self.concepts['noun_phrases']: self.concepts['noun_phrases'].remove(concept)
    if concept in self.concepts['verb_phrases']: self.concepts['verb_phrases'].remove(concept)
    if concept in self.concepts['descriptors']: self.concepts['descriptors'].remove(concept)
  
  def setAction(self, actor, act, target=None):
    #TODO: if actor has same one or more of the same acts and any have targets there shouldn't be any successorless acts
    if not target:
      self.actionGraph.add_edge(actor, act)
      self.shortTermMemory.appendleft(actor)
    else:
      if target.name == '!':
        potentialMatchingActs = self.actionGraph.successors(actor)
        for potentialMatchingAct in potentialMatchingActs:
          if act.name in potentialMatchingAct.synonyms() or potentialMatchingAct.isA(act.name):
            self.remove(potentialMatchingAct)
        self.shortTermMemory.appendleft(actor)
        self.remove(act)
        self.remove(target)
        return
      elif re.match('^!', target.name):
        affirmativeTarget = target.name[1:]
        potentialMatchingActs = self.actionGraph.successors(actor)
        temp = set()
        for potentialMatchingAct in potentialMatchingActs:
          if act.name in potentialMatchingAct.synonyms() or potentialMatchingAct.isA(act.name):
            temp.add(potentialMatchingAct)
        potentialMatchingActs = temp
        for potentialMatchingAct in potentialMatchingActs:
          potentiallyMatchingTargets = self.actionGraph.successors(potentialMatchingAct)
          for potentiallyMatchingTarget in potentiallyMatchingTargets:
            if affirmativeTarget in potentiallyMatchingTarget.synonyms() or potentiallyMatchingTarget.isA(affirmativeTarget):
              self.remove(potentialMatchingAct)
        self.shortTermMemory.appendleft(actor)
        self.remove(act)
        self.remove(target)
        return
      else:
        if self.actionGraph.successors(actor) and self.actionGraph.predecessors(target):
          sharedActs = set(self.actionGraph.successors(actor)).intersection(set(self.actionGraph.predecessors(target)))
          for sharedAct in sharedActs:
            if act.parents().intersection(sharedAct.parents()): 
              self.remove(act)
              return False
        self.actionGraph.add_edge(act, target)
        self.actionGraph.add_edge(actor, act)
        self.shortTermMemory.appendleft(actor)
        self.shortTermMemory.appendleft(target)
        
  def unsetAction(self, actor, act, target=None):
    if target:
      self.actionGraph.remove_edge(act, target)
      self.shortTermMemory.appendleft(target)
    if len(self.actionGraph.out_edges(act)) == 0:
        self.actionGraph.remove_edge(actor, act)
        self.concepts['verb_phrases'].remove(act)
        self.stateGraph.remove_node(act)
        self.actionGraph.remove_node(act)
    self.shortTermMemory.appendleft(actor)
  
  def setComponent(self, parent, label, child=None):
    if child:
      self.componentGraph.add_edge(parent, child, label=label)
    else:
      child = self.newNounPhrase(label)
      self.componentGraph.add_edge(parent, child, label=label)
    self.shortTermMemory.appendleft(parent)
    self.shortTermMemory.appendleft(child)
      
  def unsetComponent(self, parent, child):
    self.componentGraph.remove_edge(parent, child)
    self.shortTermMemory.appendleft(parent)
    self.shortTermMemory.appendleft(child)
  
  def setState(self, subject, descriptor):
    if re.match('^!', descriptor.name):
      affirmativeDescriptor = descriptor.name[1:]
      if affirmativeDescriptor != '':
        potentialMatches = self.stateGraph.successors(subject)
        for potentialMatch in potentialMatches:
          if affirmativeDescriptor in potentialMatch.synonyms() or potentialMatch.isA(affirmativeDescriptor):
            self.unsetState(subject, potentialMatch)
      self.remove(descriptor)
    else:
      self.stateGraph.add_edge(subject, descriptor)
    self.shortTermMemory.appendleft(subject)

  def unsetState(self, subject, state):
    self.stateGraph.remove_edge(subject, state)
    self.concepts['descriptors'].remove(state)
    self.stateGraph.remove_node(state)
    self.remove(state)
    self.shortTermMemory.appendleft(subject)
    
  def mergeConcepts(self, concept1, concept2):
    names = (concept1.name, concept2.name)
    if isinstance(concept1, NounPhrase) and isinstance(concept2, NounPhrase):
      mergedConcept = self.newNounPhrase(names[1]) if re.match('^unspecified', names[0]) else self.newNounPhrase(names[0])
    elif isinstance(concept1, VerbPhrase) and isinstance(concept2, VerbPhrase):
      mergedConcept = self.newVerbPhrase(names[1]) if re.match('^unspecified', names[0]) else self.newVerbPhrase(names[0])
    elif isinstance(concept1, Descriptor) and isinstance(concept2, Descriptor):
      mergedConcept = self.newDescriptor(names[1]) if re.match('^unspecified', names[0]) else self.newDescriptor(names[0])
    else:
      raise Exception('mergeConcepts: Unmatching phrase types')
    if self.isUniversal:
      for hash in self.conceptHashTable:
        if mergedConcept is self.conceptHashTable[hash]:
          if concept1.name in self.prototypes: self.prototypes[concept1.name] = hash 
          if concept2.name in self.prototypes: self.prototypes[concept2.name] = hash 
          break
    if not re.match('^unspecified', names[0]) and not re.match('^unspecified', names[1]):
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
            graph.add_edge(mergedConcept, edge[1], edge[2])
    self.remove(concept1)
    self.remove(concept2)
    self.shortTermMemory.appendleft(mergedConcept)
    return mergedConcept

  def queryPrototype(self, name, phraseType):
    synonyms = Concept().synonyms(name)
    for synonym in synonyms:
      if synonym in self.prototypes:
        hash = self.prototypes[synonym]
        if hash in self.conceptHashTable:
          concept = self.conceptHashTable[hash]
          if concept: return concept
    if phraseType == 'NounPhrase':
      concept = NounPhrase(name)
    elif phraseType == 'VerbPhrase':
      concept = VerbPhrase(name)
    elif phraseType == 'Descriptor':
      concept = Descriptor(name)
    else:
      raise Exception('queryPrototype: Unknown phrase type')
    self.incorporateConcept(concept, prototype=True)
    return concept    
 
  def queryNounPhrases(self, type):
    if 'query' in type:
      interpreter = Interpreter(self)
      return set(interpreter.query(type))
    response = set()
    if re.match('.*\*$', type.strip()):
      type = type[:-1]
      concept = NounPhrase(type)
      self.incorporateConcept(concept)
      response.add(concept)
      return response
    type = utilities.camelCase(type)
    exactMatch = self.queryExact(type, phraseType='NounPhrase')
    if exactMatch: response.add(exactMatch)
    for concept in self.concepts['noun_phrases']:
      if concept.isA(type):
        response.add(concept)
    return response
        
  def queryVerbPhrases(self, type):
    response = set()
    type = utilities.camelCase(type)
    exactMatch = self.queryExact(type, phraseType='VerbPhrase')
    if exactMatch: response.add(exactMatch)
    for concept in self.concepts['verb_phrases']:
      if concept.isA(type):
        response.add(concept)
    return response        
  
  def queryDescriptors(self, type):
    response = set()
    type = utilities.camelCase(type)
    exactMatch = self.queryExact(type, phraseType='Descriptor')
    if exactMatch: response.add(exactMatch)
    for concept in self.concepts['descriptor']:
      if concept.isA(type):
        response.add(concept)
    return response
  
  def queryExact(self, name, phraseType=None):
    resultByHashQuery = self.queryHash(name)
    if resultByHashQuery: return resultByHashQuery
    nameSynonyms = Concept().synonyms(utilities.camelCase(name))
    if not phraseType or phraseType == 'NounPhrase':
      for concept in self.concepts['noun_phrases']:
        if concept.name in nameSynonyms:
          return concept
    if not phraseType or phraseType == 'VerbPhrase':
      for concept in self.concepts['verb_phrases']:
        if concept.name in nameSynonyms:
          return concept
    if not phraseType or phraseType == 'Descriptor':
      for concept in self.concepts['descriptors']:
        if concept.name in nameSynonyms:
          return concept
    return None
  
  def queryHash(self, hash):
    if hash in self.conceptHashTable:
      return self.conceptHashTable[hash]
    else:
      return None
  
  def findLastReferenced(self, concepts):
    if isinstance(concepts, set):
      for reference in self.shortTermMemory:
        if reference in concepts:
          return reference
      raise Exception('findLastReferenced: No appropriate recent references')
    else:
      raise Exception('findLastReferenced: Expected set of concepts')
  
  def __contains__(self, concept):
    if concept in self.concepts['noun_phrases']:
      return True
    elif concept in self.concepts['verb_phrases']:
      return True
    elif concept in self.concepts['descriptors']:
      return True
    else:
      return False
  
      
    