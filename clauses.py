import copy

class Clause:
  def __init__(self, cogScriptJSON):
    self.cogScriptJSON = cogScriptJSON
    self.hashcode = self.calculateHash(cogScriptJSON)
    self.calculateDependencies()
  
  def calculateHash(self, obj):
    if isinstance(obj, (set, tuple, list)):
      return tuple([self.calculateHash(e) for e in obj])    
    elif not isinstance(obj, dict):
      return hash(obj)
    new_obj = copy.deepcopy(obj)
    for k, v in new_obj.items():
      new_obj[k] = self.calculateHash(v)
    return hash(tuple(frozenset(sorted(new_obj.items()))))
    
  def calculateDependencies(self):
    print 'TODO: write recursive dependency calculating function'