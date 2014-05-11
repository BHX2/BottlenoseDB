#!usr/bin/python2.7 -tt

import sys
sys.dont_write_bytecode = True
# Keeps directory clean by not compiling local files to bytecode

from concepts import Concept
from contexts import Context
from translator import grammar, Translator
from interpreter import Interpreter
import utilities

class Bottlenose:
  def __init__(self, bootstrapVocabulary=False):
    Concept(bootstrapVocabulary)
    self._contexts = [Context()]
    self._context = self._contexts[0]
    self._translator = Translator()
    self._interpreter = Interpreter(self._context)
    
  def tell(self, input):
    JSON = self._translator.visit(grammar.parse(input))
    results = self._interpreter.interpret(JSON)
    self._context.ponderRecentMentions()
    if isinstance(results, set) or isinstance(results, list):
      objects = list()
      for result in results:
        objects.append(BottlenoseObject(result, self._context))
      return objects
    elif not results:
      return None
    else:
      return [BottlenoseObject(results, self._context)]
  
  def context(self):
    return self._context
    
  def listContexts(self):
    return self._contexts
    
  def setContext(self, index):
    if index >= 0 and index < len(self._contexts):
      self._context = self._contexts[index]
      self._interpreter.setContext(self._contexts[index])
      
class BottlenoseObject:
  def __init__(self, concept, context):
    self.name = concept.name
    self.hashcode = None
    for hash in context.conceptHashTable:
      if context.conceptHashTable[hash] is concept:
        self.hashcode = hash
    self.synonyms = concept.synonyms().copy()
    self.parents = concept.parents()
    self.ancestors = concept.ancestors()
    self.descendants = concept.descendants()
    if utilities.camelCase(concept.name) in self.synonyms: self.synonyms.remove(utilities.camelCase(concept.name))
    self.states = list()
    descriptors = context.stateGraph.successors(concept)
    for descriptor in descriptors:
      self.states.append((descriptor.name, 100))
    potentialDescriptorEdges = context.potentialStateGraph.out_edges(concept, data=True) if concept in context.potentialStateGraph else []
    for potentialDescriptorEdge in potentialDescriptorEdges:
      self.states.append((potentialDescriptorEdge[1].name, int(potentialDescriptorEdge[2]['weight'])))
    def combineStates(stateTuples):
      evidence = dict()
      for stateTuple in stateTuples:
        if not stateTuple[0] in evidence:
          evidence[stateTuple[0]] = int(stateTuple[1])
        else:
          if evidence[stateTuple[0]] < 100:
            evidence[stateTuple[0]] = evidence[stateTuple[0]] + int(stateTuple[1])
          else:
            evidence[stateTuple[0]] = 100
      states = list()  
      for state in evidence:
        states.append((state, evidence[state]))
      return states
    self.states = combineStates(self.states)
    self.components = list()
    for componentEdge in context.componentGraph.out_edges(concept, data=True):
      self.components.append((componentEdge[2]['label'], componentEdge[1].name, 100))
    potentialComponentEdges = context.potentialComponentGraph.out_edges(concept, data=True) if concept in context.potentialComponentGraph else []
    for potentialComponentEdge in potentialComponentEdges:
      self.components.append((potentialComponentEdge[2]['label'], potentialComponentEdge[1].name, potentialComponentEdge[2]['weight']))  
    def combineComponents(componentTuples):
      evidence = dict()
      for componentTuple in componentTuples:
        if not componentTuple[0] in evidence:
          evidence[componentTuple[0]] = dict()
        if not componentTuple[1] in evidence[componentTuple[0]]:
          evidence[componentTuple[0]][componentTuple[1]] = int(componentTuple[2])
        else:
          if evidence[componentTuple[0]][componentTuple[1]] < 100:
            evidence[componentTuple[0]][componentTuple[1]] = evidence[componentTuple[0]][componentTuple[1]] + int(componentTuple[2])
          else:
            evidence[componentTuple[0]][componentTuple[1]] = 100
      components = list()  
      for branchPhrase in evidence:
        for component in evidence[branchPhrase]:
          components.append((branchPhrase, component, evidence[branchPhrase][component]))
      return components
    self.components = combineComponents(self.components)
    self.componentOf = list()
    for componentEdge in context.componentGraph.in_edges(concept, data=True):
      self.componentOf.append((componentEdge[2]['label'], componentEdge[0].name, 100))
    potentialComponentOfEdges = context.potentialComponentGraph.in_edges(concept, data=True) if concept in context.potentialComponentGraph else []
    for potentialComponentOfEdge in potentialComponentOfEdges:
      self.componentOf.append((potentialComponentOfEdge[2]['label'], potentialComponentOfEdge[0].name, potentialComponentOfEdge[2]['weight']))
    self.componentOf = combineComponents(self.componentOf)
    self.actions = list()
    acts = set(context.actionGraph.neighbors(concept))
    for actor_act in context.actionGraph.out_edges(concept):
      for act_target in context.actionGraph.out_edges(actor_act[1]):
        self.actions.append((act_target[0].name, act_target[1].name, 100))
        acts.remove(act_target[0])
    potentialActs = set(context.potentialActionGraph.neighbors(concept))
    for potential_actor_act in context.potentialActionGraph.out_edges(concept):
      for potential_act_target in context.potentialActionGraph.out_edges(potential_actor_act[1]):
        self.actions.append((potential_act_target[0].name, potential_act_target[1].name, 100))
        potentialActs.remove(potential_act_target[0])
    def combineActions(actionTuples):
      evidence = dict()
      for actionTuple in actionTuples:
        if not actionTuple[0] in evidence:
          evidence[actionTuple[0]] = dict()
        if not actionTuple[1] in evidence[actionTuple[0]]:
          evidence[actionTuple[0]][actionTuple[1]] = int(actionTuple[2])
        else:
          if evidence[actionTuple[0]][actionTuple[1]] < 100:
            evidence[actionTuple[0]][actionTuple[1]] = evidence[actionTuple[0]][actionTuple[1]] + int(actionTuple[2])
          else:
            evidence[actionTuple[0]][actionTuple[1]] = 100
      actions = list()  
      for act in evidence:
        for target in evidence[act]:
          actions.append((act, target, evidence[act][target]))
      return actions
    for act in acts:
      self.actions.append((act.name, 'None', 100))
    self.actions = combineActions(self.actions)
    self.actedOnBy = list()
    for act_target in context.actionGraph.in_edges(concept):
      for actor_act in context.actionGraph.in_edges(act_target[0]):
        self.actedOnBy.append((act_target[0].name, actor_act[0].name, 100))
    for potential_act_target in context.potentialActionGraph.in_edges(concept):
      for potential_actor_act in context.potentialActionGraph.in_edges(potential_act_target[0]):
        self.actedOnBy.append((potential_act_target[0].name, potential_actor_act[0].name, 100))
    self.actedOnBy = combineActions(self.actedOnBy)