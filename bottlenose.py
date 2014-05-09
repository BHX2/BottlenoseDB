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
    self._universalContext = Context(universal=True)
    self._contexts = [self._universalContext, Context()]
    self._context = self._contexts[1]
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
    self.isPrototype = True if self.hashcode in context.prototypes.values() else False
    self.synonyms = concept.synonyms().copy()
    self.parents = concept.parents()
    self.ancestors = concept.ancestors()
    self.descendants = concept.descendants()
    if utilities.camelCase(concept.name) in self.synonyms: self.synonyms.remove(utilities.camelCase(concept.name))
    self.states = list()
    descriptors = context.stateGraph.successors(concept)
    for descriptor in descriptors:
      self.states.append(descriptor.name)
    self.components = list()
    for componentEdge in context.componentGraph.out_edges(concept, data=True):
      self.components.append((componentEdge[2]['label'], componentEdge[1].name, 1))
    self.componentOf = list()
    for componentEdge in context.componentGraph.in_edges(concept, data=True):
      self.componentOf.append((componentEdge[2]['label'], componentEdge[0].name, 1))
    self.actions = list()
    acts = set(context.actionGraph.neighbors(concept))
    for actor_act in context.actionGraph.out_edges(concept):
      for act_target in context.actionGraph.out_edges(actor_act[1]):
        self.actions.append((act_target[0].name, act_target[1].name, 1))
        acts.remove(act_target[0])
    for act in acts:
      self.actions.append((act.name, None, 1))
    self.actedOnBy = list()
    for act_target in context.actionGraph.in_edges(concept):
      for actor_act in context.actionGraph.in_edges(act_target[0]):
        self.actedOnBy.append((act_target[0].name, actor_act[0].name, 1))