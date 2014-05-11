import copy
from clauses import Clause

class Equation:
  variableHashTable = dict()
  variableHashToDependencies = dict()
  equationExpressions = dict()
  
  def __init__(self, JSON):
    self.dependentVariable = JSON['equation']['dependent_variable']
    self.expression = JSON['equation']['expression']
    self.hashcode = self.calculateHash(self.dependentVariable)
    if self.hashcode in Equation.variableHashTable:
      Equation.remove(Equation.variableHashTable[self.hashcode])
    Equation.variableHashTable[self.hashcode] = self
    self.calculateDependencies()
  
  @classmethod
  def remove(clss, equation):
    del clss.variableHashToDependencies[equation.hashcode]
    del equation
  
  @staticmethod
  def calculateHash(obj):
    if isinstance(obj, (set, tuple, list)):
      return tuple([Equation.calculateHash(e) for e in obj])    
    elif not isinstance(obj, dict):
      return hash(obj)
    new_obj = copy.deepcopy(obj)
    for k, v in new_obj.items():
      new_obj[k] = Equation.calculateHash(v)
    return hash(tuple(frozenset(sorted(new_obj.items()))))
  
  def retrieveDependencies(self, JSON):
    hash = self.calculateHash(JSON)
    if hash in Equation.variableHashToDependencies:
      return Equation.variableHashToDependencies[hash]
    else:
      return list()
  
  def calculateDependencies(self):
    if not self.hashcode in Equation.variableHashToDependencies:
      Equation.variableHashToDependencies[self.hashcode] = list()
    for x in self.expression:
      if isinstance(x, dict):
        if 'concept' in x or 'component' in x:
          Equation.variableHashToDependencies[self.hashcode].append(x)
        else:
          raise Exception('calculateDependencies: Unknown equation structure')
  
  def independentClause(self):
    compoundClause = {'AND':[{'statement': self.dependentVariable}]}
    for variable in self.variableHashToDependencies[self.hashcode]:
      compoundClause['AND'].append({'statement': variable})
    clause = Clause(compoundClause, independent=True, isEquation=True)
    return clause
  
  def dependentClause(self):
    clause = Clause({'statement': {'equation': self.hashcode}}, independent=False, isEquation=True)
    return clause
  
  def solveAndAssertWithInterpreter(self, interpreter):
    dependencies = Equation.variableHashToDependencies[self.hashcode]
    for dependency in dependencies:
      if Equation.calculateHash(dependency) in Equation.variableHashTable:
        Equation.variableHashTable[Equation.calculateHash(dependency)].solveAndAssertWithInterpreter(interpreter)
    stringForEval = ""
    for term in self.expression:
      if isinstance(term, dict):
        if 'concept' in term or 'component' in term:
          stringForEval += str(interpreter.queryQuantitativeState(term))
      else:
        stringForEval += str(term)
    solution = eval(stringForEval)
    state = {'state': {'subject': self.dependentVariable, 'description': {'quantity': solution}}}
    interpreter.assertState(state)