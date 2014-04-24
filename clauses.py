import copy

#TODO: test soundness of dependency calculator with several Cogscript JSONs

class Clause:
  dependencies = dict()
  hashtable = dict()
  
  def __init__(self, cogscriptJSON):
    self.cogscriptJSON = cogscriptJSON
    self.hashcode = self.calculateHash(cogscriptJSON)
    self.truth = False
    self.threshold = None
    self.likelihood = 0
    Clause.dependencies[self.hashcode] = self.calculateDependencies(self.cogscriptJSON)
    Clause.hashtable[self.hashcode] = self
 
  @staticmethod
  def calculateHash(obj):
    if isinstance(obj, (set, tuple, list)):
      return tuple([Clause.calculateHash(e) for e in obj])    
    elif not isinstance(obj, dict):
      return hash(obj)
    new_obj = copy.deepcopy(obj)
    for k, v in new_obj.items():
      new_obj[k] = Clause.calculateHash(v)
    return hash(tuple(frozenset(sorted(new_obj.items()))))
  
  @staticmethod
  def checkForClause(cogscriptJSON):
    hashcode = Clause.calculateHash(cogscriptJSON)
    if hashcode in Clause.dependencies:
      return hashcode
    else:
      return False
  
  @staticmethod
  def makeClauseIfNonexistent(cogscriptJSON):
    clause = Clause.checkForClause(cogscriptJSON) 
    if clause:
      return clause
    else:
      return Clause(cogscriptJSON).hashcode
  
  @staticmethod
  def calculateDependencies(cogscriptJSON):
    dependencies = set()  
    # likely list of concepts or statements
    if isinstance(cogscriptJSON, list):
      for child in cogscriptJSON:
        dependencies.add(Clause.makeClauseIfNonexistent(child))
      return dependencies
    # convenience rename of parameter
    clause = cogscriptJSON
    # ginormous if-then-else tree
    if 'concept' in clause:
      return None
    elif 'comparison' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['comparison']['variable']))
      dependencies.add(Clause.makeClauseIfNonexistent(clause['comparison']['measure']))
    elif 'AND' in clause or 'OR' in clause or 'XOR' in clause or 'NOT' in clause:
      for subclause in clause.values():
        dependencies.add(Clause.makeClauseIfNonexistent(subclause))
    elif 'statement' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['statement']))
    elif 'arithmetic_operation' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['arithmetic_operation']['variable']))
    elif 'quantitative_change' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['quantitative_change'].values()[0]))
    elif 'taxonomy_assertion' in clause:
      if clause['taxonomy_assertion']['type'] == 'type_includes':
        dependencies.add(Clause.makeClauseIfNonexistent(clause['taxonomy_assertion']['parent']))
      elif clause['taxonomy_assertion']['type'] == 'is_a':
        dependencies.add(Clause.makeClauseIfNonexistent(clause['taxonomy_assertion']['child']))
    elif 'synonym_assertion' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['synonym_assertion']['subject']))
    elif 'state' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['state']['subject']))
    elif 'action' in clause:
      if 'actor' in clause['action'] and 'act' in clause['action']:
        dependencies.add(Clause.makeClauseIfNonexistent({'actor-act': {'actor': clause['action']['actor'], 'act': clause['action']['act']}}))
      if 'act' in clause['action'] and 'target' in clause['action']:
        dependencies.add(Clause.makeClauseIfNonexistent({'act-target': {'act': clause['action']['act'], 'target': clause['action']['target']}}))
      if 'actor' in clause['action'] and 'target' in clause['action']:
        dependencies.add(Clause.makeClauseIfNonexistent({'actor-target': {'actor': clause['action']['actor'], 'target': clause['action']['target']}}))
    elif 'actor-act' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['actor-act']['actor']))
      dependencies.add(Clause.makeClauseIfNonexistent(clause['actor-act']['act']))
    elif 'act-target' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['act-target']['act']))
      dependencies.add(Clause.makeClauseIfNonexistent(clause['act-target']['target']))    
    elif 'actor-target' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['actor-target']['actor']))
      dependencies.add(Clause.makeClauseIfNonexistent(clause['actor-target']['target']))
    elif 'component_assertion' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['component_assertion']['target']))
      dependencies.add(Clause.makeClauseIfNonexistent(clause['component_assertion']['assignment']))
    elif 'component' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['component']))
    elif 'stem' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['stem']))
      if 'branch' in clause:
        dependencies.add(Clause.makeClauseIfNonexistent(clause['branch']))
    # return back results
    if len(dependencies) > 0:
      return dependencies
    else:
      return None