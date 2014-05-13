import re
import datetime
import os
import copy
from collections import deque
import networkx
from concepts import Concept
from phrases import NounPhrase, VerbPhrase, Descriptor
from interpreter import Interpreter
from clauses import Clause
import utilities

class Context:
  def __init__(self, name=None):
    if name:
      self.name = name
    else:
      now = datetime.datetime.now()
      self.name = 'Context from ' + now.strftime("%B %d %Y %I:%M%p")
    self.componentGraph = networkx.DiGraph()
    self.actionGraph = networkx.DiGraph()
    self.stateGraph = networkx.DiGraph()
    self.concepts = {'noun_phrases': set(), 'verb_phrases': set(), 'descriptors': set()}
    self.conceptHashTable = dict()
    self.potentialComponentGraph = networkx.MultiDiGraph()
    self.potentialActionGraph = networkx.MultiDiGraph()
    self.potentialStateGraph = networkx.MultiDiGraph()
    self.shortTermMemory = deque(maxlen=100)
    self.clauseToConceptSet = dict()
    self.clauseToPotentialEdges = dict()
    self.recentlyMentionedPhrases = set()
  
  def rename(self, newName):
    self.name = newName

  def incorporateConcept(self, concept, dontRemember=False):
    hash = os.urandom(5).encode('hex')
    self.conceptHashTable[hash] = concept
    if isinstance(self, Subcontext):
      self.supercontext.incorporateConcept(concept)
    if isinstance(concept, NounPhrase):
      self.componentGraph.add_node(concept)
      self.actionGraph.add_node(concept)
      self.stateGraph.add_node(concept)
      self.potentialComponentGraph.add_node(concept)
      self.potentialActionGraph.add_node(concept)
      self.potentialStateGraph.add_node(concept)
      self.concepts['noun_phrases'].add(concept)
      if not dontRemember:
        self.registerChange(concept)
    elif isinstance(concept, VerbPhrase):
      self.actionGraph.add_node(concept)
      self.stateGraph.add_node(concept)
      self.potentialActionGraph.add_node(concept)
      self.potentialStateGraph.add_node(concept)
      self.concepts['verb_phrases'].add(concept)
    elif isinstance(concept, Descriptor):
      self.stateGraph.add_node(concept)
      self.potentialStateGraph.add_node(concept)
      self.concepts['descriptors'].add(concept)
      
  def newNounPhrase(self, nounPhrase, initiatingClauseHash=None):
    concept = NounPhrase(nounPhrase)
    if initiatingClauseHash:
      self.incorporateConcept(concept, dontRemember=True)
    else:
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
          if not self.actionGraph.predecessors(act):
            self.remove(act)
      if concept in self.stateGraph:
        descriptions = self.stateGraph.successors(concept)
        for description in descriptions:
          if not self.stateGraph.predecessors(description):
            self.remove(description)
      if concept in self.potentialActionGraph:
        acts = self.potentialActionGraph.successors(concept)
        for act in acts:
          self.remove(act)
      if concept in self.potentialStateGraph:
        descriptions = self.potentialStateGraph.successors(concept)
        for description in descriptions:
          self.remove(description)
    if concept in self.actionGraph: self.actionGraph.remove_node(concept)
    if concept in self.stateGraph: self.stateGraph.remove_node(concept)
    if concept in self.componentGraph: self.componentGraph.remove_node(concept)
    if concept in self.potentialActionGraph: self.potentialActionGraph.remove_node(concept)
    if concept in self.potentialStateGraph: self.potentialStateGraph.remove_node(concept)
    if concept in self.potentialComponentGraph: self.potentialComponentGraph.remove_node(concept)
    if concept in self.concepts['noun_phrases']: self.concepts['noun_phrases'].remove(concept)
    if concept in self.concepts['verb_phrases']: self.concepts['verb_phrases'].remove(concept)
    if concept in self.concepts['descriptors']: self.concepts['descriptors'].remove(concept)
  
  def addPotentialEdge(self, graphName, node1, node2, weight, clauseHash, label=None):
    if graphName == 'potentialActionGraph':
      self.potentialActionGraph.add_edge(node1, node2, key=clauseHash, weight=weight)
    elif graphName == 'potentialStateGraph':
      self.potentialStateGraph.add_edge(node1, node2, key=clauseHash, weight=weight)
    elif graphName == 'potentialComponentGraph':
      self.potentialComponentGraph.add_edge(node1, node2, key=clauseHash, weight=weight, label=label)
    else:
      raise Exception('addPotentialEdge: Unknown graph name')
    if not clauseHash in self.clauseToPotentialEdges:
      self.clauseToPotentialEdges[clauseHash] = list()
    self.clauseToPotentialEdges[clauseHash].append((graphName, node1, node2, clauseHash))

  def ponderRecentMentions(self):
    recentlyExecutedDependentClauses = set()
    recentlyTestedIndependentClauses = set()
    interpreter = Interpreter(self)
    relevantPhrases = self.recentlyMentionedPhrases & set(Clause.relatedPhraseToClause.keys())
    self.recentlyMentionedPhrases = set()
    for phrase in relevantPhrases:
      matchingClauses = Clause.relatedPhraseToClause[phrase]
      for clause in matchingClauses:
        if clause in recentlyTestedIndependentClauses:
          continue
        else:
          recentlyTestedIndependentClauses.add(clause)
        results = interpreter.test(clause.JSON)
        graphs = {
          'potentialActionGraph': self.potentialActionGraph,
          'potentialComponentGraph': self.potentialComponentGraph,
          'potentialStateGraph': self.potentialStateGraph
        }
        if not clause.hashcode in self.clauseToPotentialEdges:
          self.clauseToPotentialEdges[clause.hashcode] = list()
        relatedPotentialEdges = self.clauseToPotentialEdges[clause.hashcode]
        if not results:
          for edgeRecord in relatedPotentialEdges:
            graphs[edgeRecord[0]].remove_edge(edgeRecord[1], edgeRecord[2], key=clause.hashcode)
          self.clauseToPotentialEdges[clause.hashcode] = list()
          self.clauseToConceptSet[clause.hashcode] = set()
          continue
        if not clause.hashcode in self.clauseToConceptSet:
          self.clauseToConceptSet[clause.hashcode] = set()
        oldSet = self.clauseToConceptSet[clause.hashcode]
        newSet = results
        self.clauseToConceptSet[clause.hashcode] = newSet.copy()
        if not clause.isEquation and oldSet == newSet:
          continue
        conceptsOfDeprecatedPotentiations = oldSet - newSet
        conceptsOfNewPotentiations = newSet - oldSet
        if clause.isEquation:
          conceptsOfNewPotentiations = newSet
        brainFreeze = copy.copy(self.shortTermMemory)
        self.shortTermMemory.extendleft(conceptsOfNewPotentiations)
        def edgeRecordIsDeprecated(edgeRecord):
          if edgeRecord[1] in conceptsOfDeprecatedPotentiations or edgeRecord[2] in conceptsOfDeprecatedPotentiations:
            graphs[edgeRecord[0]].remove_edge(edgeRecord[1], edgeRecord[2], key=clause.hashcode)
            return True
          else:
            return False 
        if clause.hashcode in self.clauseToPotentialEdges:       
          if conceptsOfDeprecatedPotentiations:
            self.clauseToPotentialEdges[clause.hashcode] = [x for x in relatedPotentialEdges if not edgeRecordIsDeprecated(x)]
        if conceptsOfNewPotentiations:
          subcontext = Subcontext(self, conceptsOfNewPotentiations)
          evidenceEdges = Clause.evidenceGraph.out_edges(clause.hashcode)
          ruleEdges = Clause.ruleGraph.out_edges(clause.hashcode)
          for evidenceEdge in evidenceEdges:
            dependentClause = Clause.hashtable[evidenceEdge[1]]
            JSON = interpreter.solveQueries(copy.deepcopy(dependentClause.JSON))
            if dependentClause in recentlyExecutedDependentClauses:
              continue
            else:
              recentlyExecutedDependentClauses.add(dependentClause)
              interpreter.setContext(subcontext)
              interpreter.assertStatement(JSON, clause.hashcode)
              interpreter.setContext(self)
          for ruleEdge in ruleEdges:
            dependentClause = Clause.hashtable[ruleEdge[1]]
            JSON = interpreter.solveQueries(copy.deepcopy(dependentClause.JSON))
            if dependentClause in recentlyExecutedDependentClauses:
              continue
            else:
              recentlyExecutedDependentClauses.add(dependentClause)
              interpreter.assertStatement(JSON)
        self.shortTermMemory = brainFreeze  
                
  def registerChange(self, concept):
    self.shortTermMemory.appendleft(concept)
    lineage = concept.ancestors().copy()
    self.recentlyMentionedPhrases |= set(concept.synonyms())
    self.recentlyMentionedPhrases |= set(concept.ancestors())
    
  def setAction(self, actor, act, target=None, initiatingClauseHash=None):
    #TODO: if actor has same one or more of the same acts and any have targets there shouldn't be any successorless acts
    if initiatingClauseHash:
      if not target:
        self.addPotentialEdge('potentialActionGraph', actor, act, 1, initiatingClauseHash)
      else:
        if target.name == '!':
          potentialMatchingActs = self.actionGraph.successors(actor)
          potentialMatchingActs.extend(self.potentialActionGraph.successors(actor))
          for potentialMatchingAct in potentialMatchingActs:
            if potentialMatchingAct.isA(act.name):
              self.unsetAction(actor, potentialMatchingAct, None, initiatingClauseHash)
          self.remove(act)
          self.remove(target)
          return    
        elif re.match('^!', target.name):
          affirmativeTarget = target.name[1:]
          potentialMatchingActs = self.actionGraph.successors(actor)
          potentialMatchingActs.extend(self.potentialActionGraph.successors(actor))
          temp = set()
          for potentialMatchingAct in potentialMatchingActs:
            if potentialMatchingAct.isA(act.name):
              temp.add(potentialMatchingAct)
          potentialMatchingActs = temp
          for potentialMatchingAct in potentialMatchingActs:
            potentiallyMatchingTargets = self.actionGraph.successors(potentialMatchingAct)
            potentiallyMatchingTargets.extend(self.potentialActionGraph.successors(potentialMatchingAct))
            for potentiallyMatchingTarget in potentiallyMatchingTargets:
              if potentiallyMatchingTarget.isA(affirmativeTarget):
                self.unsetAction(actor, potentialMatchingAct, potentiallyMatchingTarget, initiatingClauseHash)
          self.remove(act)
          self.remove(target)
          return          
        else:
          self.addPotentialEdge('potentialActionGraph', act, target, 1, initiatingClauseHash)
          self.addPotentialEdge('potentialActionGraph', actor, act, 1, initiatingClauseHash)
    else:
      if not target:
        self.actionGraph.add_edge(actor, act)
        self.registerChange(actor)
      else:
        if target.name == '!':
          potentialMatchingActs = self.actionGraph.successors(actor)
          for potentialMatchingAct in potentialMatchingActs:
            if potentialMatchingAct.isA(act.name):
              self.remove(potentialMatchingAct)
          self.registerChange(actor)
          self.remove(act)
          self.remove(target)
          return
        elif re.match('^!', target.name):
          affirmativeTarget = target.name[1:]
          potentialMatchingActs = self.actionGraph.successors(actor)
          temp = set()
          for potentialMatchingAct in potentialMatchingActs:
            if potentialMatchingAct.isA(act.name):
              temp.add(potentialMatchingAct)
          potentialMatchingActs = temp
          for potentialMatchingAct in potentialMatchingActs:
            potentiallyMatchingTargets = self.actionGraph.successors(potentialMatchingAct)
            for potentiallyMatchingTarget in potentiallyMatchingTargets:
              if potentiallyMatchingTarget.isA(affirmativeTarget):
                self.unsetAction(actor, potentialMatchingAct, potentiallyMatchingTarget, initiatingClauseHash)
          self.registerChange(actor)
          self.remove(act)
          self.remove(target)
          return
        else:
          if self.actionGraph.successors(actor) and self.actionGraph.predecessors(target):
            sharedActs = set(self.actionGraph.successors(actor)).intersection(set(self.actionGraph.predecessors(target)))
            for sharedAct in sharedActs:
              if sharedAct.isA(act.name): 
                self.unsetAction(actor, sharedAct, target, initiatingClauseHash)
              elif act.isA(sharedAct.name):
                return False
          self.actionGraph.add_edge(act, target)
          self.actionGraph.add_edge(actor, act)
          self.registerChange(actor)
          self.registerChange(target)
          
  def unsetAction(self, actor, act, target=None, initiatingClauseHash=None):
    if initiatingClauseHash:
      if target and target.name != '!':
        self.addPotentialEdge('potentialActionGraph', actor, act, -1, initiatingClauseHash)
        self.addPotentialEdge('potentialActionGraph', act, target, -1, initiatingClauseHash)
      else:
        targets = list()
        self.addPotentialEdge('potentialActionGraph', actor, act, -1, initiatingClauseHash)
        if act in self.actionGraph:
          targets = self.actionGraph.successors(act)
        if act in self.potentialActionGraph:
          targets.extend(self.potentialActionGraph.successors(act))
        for target in targets:
          self.addPotentialEdge('potentialActionGraph', act, target, -1, initiatingClauseHash)
    else:
      if target and target.name != '!':
        self.actionGraph.remove_edge(act, target)
        self.registerChange(target)
      if len(self.actionGraph.out_edges(act)) == 0:
          self.remove(act)
      self.registerChange(actor)
  
  def setComponent(self, parent, label, child=None, initiatingClauseHash=None):
    if initiatingClauseHash:
      if child:
        self.addPotentialEdge('potentialComponentGraph', parent, child, 1, initiatingClauseHash, label=label)
      else:
        child = self.newNounPhrase(label, initiatingClauseHash)
        self.addPotentialEdge('potentialComponentGraph', parent, child, 1, initiatingClauseHash, label=label)
    else:
      if child:
        self.componentGraph.add_edge(parent, child, label=label)
      else:
        child = self.newNounPhrase(label, initiatingClauseHash)
        self.componentGraph.add_edge(parent, child, label=label)
      self.registerChange(parent)
      self.registerChange(child)
      
  def unsetComponent(self, parent, label, child, initiatingClauseHash=None):
    if initiatingClauseHash:
      self.addPotentialEdge('potentialComponentGraph', parent, child, -1, initiatingClauseHash, label=label)
    else:
      self.componentGraph.remove_edge(parent, child)
      self.registerChange(parent)
      self.registerChange(child)
  
  def setState(self, subject, descriptor, initiatingClauseHash=None):
    if initiatingClauseHash:
      if re.match('^!', descriptor.name):
        affirmativeDescriptor = descriptor.name[1:]
        if affirmativeDescriptor != '':
          potentialMatches = self.stateGraph.successors(subject)
          potentialMatches.extend(self.potentialStateGraph.successors(subject))
          for potentialMatch in potentialMatches:
            if potentialMatch.isA(affirmativeDescriptor):
              self.unsetState(subject, potentialMatch, initiatingClauseHash)
        self.remove(descriptor)
      else:
        self.addPotentialEdge('potentialStateGraph', subject, descriptor, 1, initiatingClauseHash)
    else:
      if re.match('^!', descriptor.name):
        affirmativeDescriptor = descriptor.name[1:]
        if affirmativeDescriptor != '':
          potentialMatches = self.stateGraph.successors(subject)
          for potentialMatch in potentialMatches:
            if potentialMatch.isA(affirmativeDescriptor):
              self.unsetState(subject, potentialMatch, initiatingClauseHash)
        self.remove(descriptor)
      elif descriptor.isQuantity:
        descriptors = self.stateGraph.successors(subject)
        quantitativeStates = [x for x in descriptors if x.isQuantity]
        for quantitativeState in quantitativeStates:
          self.remove(quantitativeState)
        self.stateGraph.add_edge(subject, descriptor)
      else:
        self.stateGraph.add_edge(subject, descriptor)
      self.registerChange(subject)

  def unsetState(self, subject, state, initiatingClauseHash=None):
    if initiatingClauseHash:
      self.addPotentialEdge('potentialStateGraph', subject, state, -1, initiatingClauseHash)
    else:
      self.remove(state)
      self.registerChange(subject)
    
  def mergeConcepts(self, concept1, concept2, initiatingClauseHash=None):
    names = (concept1.name, concept2.name)
    if isinstance(concept1, NounPhrase) and isinstance(concept2, NounPhrase):
      mergedConcept = self.newNounPhrase(names[1], initiatingClauseHash) if re.match('^unspecified', names[0]) else self.newNounPhrase(names[0], initiatingClauseHash)
    elif isinstance(concept1, VerbPhrase) and isinstance(concept2, VerbPhrase):
      mergedConcept = self.newVerbPhrase(names[1]) if re.match('^unspecified', names[0]) else self.newVerbPhrase(names[0])
    elif isinstance(concept1, Descriptor) and isinstance(concept2, Descriptor):
      mergedConcept = self.newDescriptor(names[1]) if re.match('^unspecified', names[0]) else self.newDescriptor(names[0])
    else:
      raise Exception('mergeConcepts: Unmatching phrase types')
    if not re.match('^unspecified', names[0]) and not re.match('^unspecified', names[1]):
      concept1.equate(concept2.name)
    for parent in concept1.parents():
      mergedConcept.classify(parent)
    for parent in concept2.parents():
      mergedConcept.classify(parent)
    graphs = [self.actionGraph, self.componentGraph, self.stateGraph]
    potentialGraphs = [self.potentialActionGraph, self.potentialComponentGraph, self.potentialStateGraph]
    concepts = [concept1, concept2]
    for concept in concepts:
      for graph in graphs:
        if concept in graph:
          in_edges = graph.in_edges(concept, data=True)
          out_edges = graph.out_edges(concept, data=True)
          for edge in in_edges:
            graph.add_edge(edge[0], mergedConcept, attr_dict=edge[2])
          for edge in out_edges:
            graph.add_edge(mergedConcept, edge[1], attr_dict=edge[2])
      for graph in potentialGraphs:
        if concept in graph:
          in_edges = graph.in_edges(concept, keys=True, data=True)
          out_edges = graph.out_edges(concept, keys=True, data=True)
          for edge in in_edges:
            graph.add_edge(edge[0], mergedConcept, key=edge[2], attr_dict=edge[3])
          for edge in out_edges:
            graph.add_edge(mergedConcept, edge[1], key=edge[2], attr_dict=edge[3])
    if initiatingClauseHash:
      def rewriteRecord(edgeRecord):
        graphType = edgeRecord[0]
        graphs = {'potentialComponentGraph': self.potentialComponentGraph}
        sourceEdge = edgeRecord[1] if edgeRecord[1] != concept1 and edgeRecord[1] != concept2 else mergedConcept
        destEdge = edgeRecord[2] if edgeRecord[2] != concept1 and edgeRecord[2] != concept2 else mergedConcept
        clause = edgeRecord[3]
        return ((graphType, sourceEdge, destEdge, clause))
      potentialEdgeRecords = self.clauseToPotentialEdges[initiatingClauseHash]
      self.clauseToPotentialEdges[initiatingClauseHash] = map(rewriteRecord, potentialEdgeRecords)
    self.remove(concept1)
    self.remove(concept2)
    if initiatingClauseHash:
      self.supercontext.remove(concept1)
      self.supercontext.remove(concept2)
    if not initiatingClauseHash:
      self.registerChange(mergedConcept)
    return mergedConcept 
 
  def queryNounPhrases(self, type):
    if 'query' in type:
      interpreter = Interpreter(self)
      return set(interpreter.query(type))
    response = set()
    if re.match('.*\^', type.strip()):
      query = type[:-1]
      all = self.queryNounPhrases(query)
      concept = self.findLastReferenced(all)
      response.add(concept)
      return response
    if re.match('^!', type):
      concept = self.newNounPhrase(type)
      response.add(concept)
      return response
    if re.match('.*\*$', type.strip()):
      type = type[:-1]
      concept = self.newNounPhrase(type)
      response.add(concept)
      return response
    type = utilities.sanitize(type)
    exactMatch = self.queryExact(type, phraseType='NounPhrase')
    if exactMatch: response.add(exactMatch)
    for concept in self.concepts['noun_phrases']:
      if concept.isA(type):
        response.add(concept)
    if not response and isinstance(self, Subcontext):
      return self.supercontext.queryNounPhrases(type)
    else:
      return response
        
  def queryVerbPhrases(self, type):
    response = set()
    type = utilities.sanitize(type)
    exactMatch = self.queryExact(type, phraseType='VerbPhrase')
    if exactMatch: response.add(exactMatch)
    for concept in self.concepts['verb_phrases']:
      if concept.isA(type):
        response.add(concept)
    return response        
  
  def queryDescriptors(self, type):
    response = set()
    type = utilities.sanitize(type)
    exactMatch = self.queryExact(type, phraseType='Descriptor')
    if exactMatch: response.add(exactMatch)
    for concept in self.concepts['descriptor']:
      if concept.isA(type):
        response.add(concept)
    return response
  
  def queryExact(self, name, phraseType=None):
    resultByHashQuery = self.queryHash(name)
    if resultByHashQuery: return resultByHashQuery
    if not name: return None
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
  
class Subcontext(Context):
  def __init__(self, supercontext, concepts=None):
    self.supercontext = supercontext
    self.componentGraph = self.supercontext.componentGraph
    self.actionGraph = self.supercontext.actionGraph
    self.stateGraph = self.supercontext.stateGraph
    self.concepts = {'noun_phrases': set(), 'verb_phrases': set(), 'descriptors': set()}
    self.conceptHashTable = self.supercontext.conceptHashTable
    self.potentialComponentGraph = self.supercontext.potentialComponentGraph
    self.potentialActionGraph = self.supercontext.potentialActionGraph
    self.potentialStateGraph = self.supercontext.potentialStateGraph
    self.shortTermMemory = self.supercontext.shortTermMemory
    self.clauseToConceptSet = self.supercontext.clauseToConceptSet
    self.clauseToPotentialEdges = self.supercontext.clauseToPotentialEdges
    self.recentlyMentionedPhrases = self.supercontext.recentlyMentionedPhrases
    if concepts:
      for concept in concepts:
        self.add(concept)
    
  def add(self, concept):
    if concept not in self:
      if isinstance(concept, NounPhrase):
        self.concepts['noun_phrases'].add(concept)
      elif isinstance(concept, VerbPhrase):
        self.concepts['verb_phrases'].add(concept)
      elif isinstance(concept, Descriptor):
        self.concepts['descriptors'].add(concept)