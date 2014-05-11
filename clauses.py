import copy
import networkx

class Clause:
  relatedPhraseToClause = dict()
  hashtable = dict()
  evidenceGraph = networkx.DiGraph()
  ruleGraph = networkx.DiGraph()
  
  def __init__(self, JSON, independent=False):
    self.JSON = JSON
    self.hashcode = self.calculateHash(JSON)
    Clause.hashtable[self.hashcode] = self
    if independent:
      self.calculateRelatedPhrases(JSON, self)
      self.evidenceGraph.add_node(self.hashcode)
      self.ruleGraph.add_node(self.hashcode)
 
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
  def calculateRelatedPhrases(JSON, originalClause):
    if isinstance(JSON, dict):
      if 'concept' in JSON:
        if not JSON['concept'] in Clause.relatedPhraseToClause:
          Clause.relatedPhraseToClause[JSON['concept']] = set()
        Clause.relatedPhraseToClause[JSON['concept']].add(originalClause)
      else:
        for key in JSON:
          Clause.calculateRelatedPhrases(JSON[key], originalClause)
    elif isinstance(JSON, list):
      for element in JSON:
        Clause.calculateRelatedPhrases(element, originalClause)
        
  def potentiates(self, dependentClause):
    self.evidenceGraph.add_edge(self.hashcode, dependentClause.hashcode)
    
  def mandates(self, dependentClause):
    self.ruleGraph.add_edge(self.hashcode, dependentClause.hashcode)
    
    