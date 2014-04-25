class Interpreter:
  def __init__(self, context):
    self.context = context
  
  def retrieveComponent(self, stem, branch):
    candidateStems = set()
    if 'stem' in stem:
      candidateStems = self.retrieveComponent(stem['stem'], stem['branch'])
    else:
      if 'concept' not in stem: 
        raise Exception('retrieveComponent: Unknown tree structure')
        return False
      possibleStems = self.context.queryNounPhrases(stem['concept'])
      candidatePairs = set()
      for possibleStem in possibleStems:
        edges = self.context.componentGraph.out_edges(possibleStem, data=True)
        for edge in edges:
          if edge[2]['label'] == branch or edge[1].name == branch:
            candidatePairs.add((possibleStem, edge[1]))
      if len(candidatePairs) == 0:
        raise Exception('retrieveComponent: No candidate stem-branch pairs found')
        return False
      else:
        for pair in candidatePairs:
          candidateStems.add(pair[1])
        return candidateStems
    newCandidateStems = set()
    for candidateStem in candidateStems:
      edges = self.context.componentGraph.out_edges(candidateStem, data=True)
      for edge in edges:
        if edge[2]['label'] == branch or edge[1].anem == branch:
          newCandidateStems.add(candidateStem)
    if len(candidateStems) == 0:
      raise Exception('retrieveComponent: Not enough candidate stems')
    elif len(candidateStems) > 1:
      raise Exception('retrieveComponent: Too many candidate stems')
    else:
      return candidateStems[0]
  
  def assertConcept(self, concept):
    self.context.newNounPhrase(concept, concept)
  
  def assertArithmeticOperation(self, arithmetic_operation):
    #TODO: Write arithmetic operation assertion method
    print "to be implemented..."
  
  def assertStatement(self, statement):
    if 'arithmetic_operation' in statement:
      self.assertArithmeticOperation(statement['arithmetic_operation'])
    elif 'concept' in statement:
      self.assertConcept(statement['concept'])
  
  def queryConcept(self, concept):
    results = self.context.queryNounPhrases(concept)
    if results:
      for result in results:
        print result
    else:
      print 'No matching concepts found.'
  
  def interpret(self, JSON):
    if 'statement' in JSON:
      self.assertStatement(JSON['statement'])
    elif 'query' in JSON:
      if 'concept' in JSON['query']:
        self.queryConcept(JSON['query']['concept'])
  
          
    
  
    