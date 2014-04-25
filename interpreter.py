from clint.textui import puts, colored, indent

class Interpreter:
  def __init__(self, context):
    self.context = context
  
  def retrieveComponent(self, stemJSON, branchPhrase, makeIfNonexistent=False):
    if 'stem' in stemJSON:
      stems = self.retrieveComponent(stemJSON['stem'], stemJSON['branch'], makeIfNonexistent)
      if not isinstance(stems, set): 
        temp = set()
        temp.add(stems)
        stems = temp
      edges = self.context.stateGraph.out_edges(stems, data=True)
      branches = set()
      for edge in edges:
        if edge[2]['label'] == branchPhrase or edge[1].name == branchPhrase:
          branches.add(edge[1])
      if len(branches) == 0:
        if makeIfNonexistent:
          for stem in stems:
            branch = self.context.newNounPhrase(None, branchPhrase)
            self.context.setComponent(stem, branchPhrase, branch)
            branches.add(branch)
        else:
          raise Exception('retrieveComponent: Branch not found')
      if len(branches) == 0:
        return None
      elif len(branches) == 1:
        (branch,) = branches
        return branch
      else:
        return branches
    else:
      if 'concept' not in stemJSON: raise Exception('retrieveComponent: Unknown tree structure')
      candidateStems = self.context.queryNounPhrases(stemJSON['concept'])
      for candidateStem in candidateStems:
        edges = self.context.stateGraph.out_edges(candidateStem, data=True)
        for edge in edges:
          if edge[2]['label'] != branchPhrase and edge[1].name != branchPhrase:
            candidateStems.remove(edge[1])
      if len(candidateStems) == 0:
        if makeIfNonexistent:
          stem = self.context.newNounPhrase(stemJSON['concept'])
        else:
          raise Exception('retrieveComponent: Stem not found')
      elif len(candidateStems) > 1:
        raise Exception('retrieveComponent: Too many matching stems')
      else:
        (stem,) = candidateStems
      edges = self.context.stateGraph.out_edges(stem, data=True)
      branches = set()
      for edge in edges:
        if edge[2]['label'] == branchPhrase or edge[1].name == branchPhrase:
          branches.add(edge[1])
      if len(branches) == 0:
        if makeIfNonexistent:
          branch = self.context.newNounPhrase(None, branchPhrase)
          self.context.setComponent(stem, branchPhrase, branch)
          branches.add(branch)
        else:
          raise Exception('retrieveComponent: No matching branch found')
      return branches
            
  def assertConcept(self, conceptPhrase):
    self.context.newNounPhrase(conceptPhrase)
  
  def assertComponent(self, componentJSON):
    self.retrieveComponent(componentJSON['stem'], componentJSON['branch'], makeIfNonexistent=True)
  
  def assertStatement(self, statement):
    if 'concept' in statement:
      self.assertConcept(statement['concept'])
    elif 'component' in statement:
      self.assertComponent(statement['component'])
  
  def query(self, conceptPhrase):
    results = self.context.queryNounPhrases(conceptPhrase)
    if results:
      for result in results:
        puts(colored.green(result.name))
        for edge in self.context.componentGraph.out_edges(result, data=True):
          with indent(2):
            puts(colored.yellow(edge[0].name) + ' (has ' + edge[2]['label'] + ') --> ' + edge[1].name)
        for edge in self.context.componentGraph.in_edges(result, data=True):
          with indent(2):
            puts(edge[0].name + ' (has ' + edge[2]['label'] + ') --> ' + colored.yellow(edge[1].name))
        for actor_act in self.context.actionGraph.edges(result):
          with indent(2):
            puts(actor_act[0].name + ' ' + actor_act[1].name)
          for act_target in context.actionGraph.edges(actor_act[1]):
            with indent(8):
              puts(actor_act[0].name + ' (' + act_target[0].name + ') --> ' + act_target[1].name)
      
        
    else:
      print 'No matching concepts found.'
  
  def interpret(self, JSON):
    if 'statement' in JSON:
      self.assertStatement(JSON['statement'])
    elif 'query' in JSON:
      if 'concept' in JSON['query']:
        self.query(JSON['query']['concept'])
  
          
    
  
    