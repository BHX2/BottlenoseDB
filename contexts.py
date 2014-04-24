import networkx

class Context:
  def __init__(self):
    aself.clauseTable = dict()
    self.componentGraph = networkx.DiGraph()
    self.actionGraph = networkx.DiGraph()
    self.relationshipGraph = networkx.Graph()
    self.stateGraph = networkx.Graph()
  
  def checkClause(self, clause):
    if clause in self.clauseTable:
      return self.clauseTable[clause]
    else:
      return False
