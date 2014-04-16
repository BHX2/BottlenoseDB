class Concept(object):
  def __init__(self, name, graph=None):
    self.components = set()
    self.actions = set()
    self.states = set()
    self.clauses = set()
    self.graphs = [graph] if graph else []
  
  def addComponent(component, target=None):
    self.components.add(component)
  
  def addAction(action, target=None):
    self.actions.add(action)
  
  def addState(state):
    self.states.add(state)
  
  def addClause(clause):
    self.clauses.add(clause)
  
  def components():
    return self.components
    
  def actions():
    return self.actions
  
  def states():
    return self.states
  
  def clauses():
    return self.clauses