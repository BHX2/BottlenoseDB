import copy

class Clause:
  dependencies = dict()
  hashtable = dict()
  
  def __init__(self, JSON):
    self.JSON = JSON
    self.hashcode = self.calculateHash(JSON)
    self.threshold = None
    Clause.dependencies[self.hashcode] = self.calculateDependencies(self.JSON)
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
  def checkForClause(JSON):
    hashcode = Clause.calculateHash(JSON)
    if hashcode in Clause.dependencies:
      return hashcode
    else:
      return False
  
  @staticmethod
  def makeClauseIfNonexistent(JSON):
    clause = Clause.checkForClause(JSON) 
    if clause:
      return clause
    else:
      return Clause(JSON).hashcode
  
  @staticmethod
  def calculateDependencies(JSON):
    dependencies = set()  
    if isinstance(JSON, list):
      for child in JSON:
        dependencies.add(Clause.makeClauseIfNonexistent(child))
      return dependencies
    clause = JSON
    if 'concept' in clause:
      if 'query' in clause:
        dependencies.add(Clause.makeClauseIfNonexistent(clause['concept']['query'])
      else:
        return None
    elif 'comparison' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['comparison']['variable']))
      if 'component' in clause['comparison']['measure'] or 'concept' in clause['comparison']['measure']
      dependencies.add(Clause.makeClauseIfNonexistent(clause['comparison']['measure']))
    elif 'AND' in clause:
      for subclause in clause.values():
        dependencies.add(Clause.makeClauseIfNonexistent(subclause))
    elif 'OR' in clause or 'XOR' in clause:
      for subclause in clause.values():
        dependencies.add(Clause.makeClauseIfNonexistent(subclause))
    elif 'NOT' in clause:
      return None
    elif 'statement' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['statement']))
    elif 'arithmetic_operation' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['arithmetic_operation']['variable']))
    elif 'taxonomy_assignment' in clause:
      if clause['taxonomy_assignment']['type'] == 'is_a':
        dependencies.add(Clause.makeClauseIfNonexistent(clause['taxonomy_assignment']['child']))
      else:
        raise Exception('calculateDependencies: /= should not be used within clauses')
    elif 'synonym_assignment' in clause:
      raise Exception('calculateDependencies: Synonym assignments should not be used within clauses')
    elif 'state' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['state']['subject']))
      dependencies.add(Clause.makeClauseIfNonexistent(clause['state']['description']))
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
    elif 'component_assignment' in clause or 'component_addition' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['component_assignment']['target']))
      dependencies.add(Clause.makeClauseIfNonexistent(clause['component_assignment']['assignment']))
    elif 'component' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['component']))
    elif 'stem' in clause:
      dependencies.add(Clause.makeClauseIfNonexistent(clause['stem']))
      if 'branch' in clause:
        dependencies.add(Clause.makeClauseIfNonexistent(clause['branch']))
    if len(dependencies) > 0:
      return dependencies
    else:
      return None