import re
import networkx

import sys
sys.dont_write_bytecode = True
# Keeps directory clean by not compiling utilities to bytecode

import utilities

class Concept(object):
  graph = networkx.MultiDiGraph()
  
  def __init__(self, name):
    self.name = utilities.camelCase(name)
    self.potential = dict()
    self.potential['components'] = set()
    self.potential['actions'] = set()
    self.potential['states'] = set()
    self.undirected = dict()
    self.undirected['components'] = set()
    self.undirected['actions'] = set()
    self.states = set()
    Concept.graph.add_node(self)
  
  def component(self, component, target=None, negative=False):
    if re.match('^!', target): return self.component(component[1:], target, True)
    component = utilities.camelCase(component)
    self.potential['components'].add(component)
    if not negative:
      if not target: self.undirected['components'].add(component)
      if isinstance(target, Concept):
        Concept.graph.add_edge(self, target, key='has ' + component)
    else:
      if not target and component in self.undirected['components']: 
        self.undirected['components'].remove(component)
      if isinstance(target, Concept):
        Concept.graph.remove_edge(self, target, key='has ' + component)      
  
  def action(self, action, target=None, negative=False):
    if re.match('^!', action): return self.action(action[1:], target, True)
    action = utilities.camelCase(action)
    self.potential['actions'].add(action)
    if not negative:
      if not target: self.undirected['actions'].add(action)
      if isinstance(target, Concept):
        Concept.graph.add_edge(self, target, key=action)
    else:
      if not target and action in self.undirected['actions']:
        self.undirected['actions'].remove(action)
      if isinstance(target, Concept):
        Concept.graph.remove_edge(self, target, key=action)
        
  def state(self, state, negative=False):
    if re.match('^!', state): return self.state(state[1:], True)
    state = utilities.camelCase(state)
    if not negative:
      self.potential['states'].add(state)
      if state not in self.states: self.states.add(state)
    else:
      if state in self.states: self.states.remove(state)
  
  def clause(self, clause):
    self.clauses.add(clause)
  
  def listComponents(self, filter=None):
    pairs = Concept.graph.out_edges(self, keys=True)
    for pair in pairs:
      if re.match('^has ', pair[2]):
        print self.name + ' ' + pair[2] + ' ' + pair[1].name
        
  def listActions(self, filter=None):
    pairs = Concept.graph.out_edges(self, keys=True)
    for pair in pairs:
      if not re.match('^has ', pair[2]):
        print self.name + ' ' + pair[2] + ' ' + pair[1].name
  
  def listStates(self, filter=None):
    for state in self.states:
      print self.name + " is " + state
  
  def listClauses(self):
    for clause in self.clauses:
      print clause
  