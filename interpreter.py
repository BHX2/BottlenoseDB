from concepts import Concept

class Interpreter:
  def __init__(self, context):
    self.context = context
  
  def retrieveComponent(self, stemJSON, branchPhrase, returnLastStems=False, assertBranches=True):
    if 'stem' in stemJSON:
      stems = self.retrieveComponent(stemJSON['stem'], stemJSON['branch'], False, assertBranches)
      if not isinstance(stems, set): 
        temp = set()
        temp.add(stems)
        stems = temp
      edges = self.context.componentGraph.out_edges(stems, data=True)
      branches = set()
      for edge in edges:
        if edge[2]['label'] == branchPhrase or edge[1].name == branchPhrase or edge[1].isA(branchPhrase):
          branches.add(edge[1])
      if len(branches) == 0:
        branches = None
      elif len(branches) == 1:
        (branch,) = branches
        branches = branch
      if returnLastStems:
        return (branches, stems)
      else:
        return branches
    else:
      if 'concept' not in stemJSON: raise Exception('retrieveComponent: Unknown tree structure')
      candidateStems = self.context.queryNounPhrases(stemJSON['concept'])
      temp = set()
      for candidateStem in candidateStems:
        edges = self.context.componentGraph.out_edges(candidateStem, data=True)
        for edge in edges:
          if edge[2]['label'] == branchPhrase or edge[1].name == branchPhrase or edge[1].isA(branchPhrase):
            temp.add(edge[0])
      candidateStems = temp
      if len(candidateStems) == 0:
        if assertBranches:
          stem = self.context.newNounPhrase(stemJSON['concept'])
        else:
          if returnLastStems:
            return (None, None)
          else:
            return None
      elif len(candidateStems) > 1:
        raise Exception('retrieveComponent: Too many matching stems')
      else:
        (stem,) = candidateStems
      edges = self.context.componentGraph.out_edges(stem, data=True)
      branches = set()
      for edge in edges:
        if edge[2]['label'] == branchPhrase or edge[1].name == branchPhrase or edge[1].isA(branchPhrase):
          branches.add(edge[1])
      if len(branches) == 0:
        if assertBranches:
          branch = self.context.newNounPhrase(None, 'unspecified')
          branch.classify(branchPhrase)
          self.context.setComponent(stem, branchPhrase, branch)
        else:
          if returnLastStems:
            stems = list()
            stems.append(stem)
            return (None, stems)
          else:
            return None
        branches.add(branch)
      if returnLastStems:
        stems = list()
        stems.append(stem)
        return (branches, stems)
      else:
        return branches
            
  def assertConcept(self, conceptPhrase):
    self.context.newNounPhrase(conceptPhrase)
  
  def assertComponent(self, componentJSON):
    (branches, stems) = self.retrieveComponent(componentJSON['stem'], componentJSON['branch'], returnLastStems=True, assertBranches=True)
    if not branches:
      for stem in stems:    
        branch = self.context.newNounPhrase(None, 'unspecified')
        branch.classify(componentJSON['branch'])
        self.context.setComponent(stem, componentJSON['branch'], branch)
  
  def assertComponentAssignment(self, componentAssertionJSON):
    (branches, stems) = self.retrieveComponent(componentAssertionJSON['target']['component']['stem'], componentAssertionJSON['target']['component']['branch'], returnLastStems=True, assertBranches=True)
    if branches:
      if isinstance(branches, set):
        for branch in branches:
          if branch.isA('unspecified'): self.context.remove(branch)
      else:
        if branches.isA('unspecified'): self.context.remove(branches)
    assignments = list()
    uninstantiatedAssignments = list()
    if isinstance(componentAssertionJSON['assignment'], list):
      for concept in componentAssertionJSON['assignment']:
          x = self.context.queryNounPhrases(concept['concept'])
          if x: 
            assignments.extend(x)
          else:
            uninstantiatedAssignments.append(concept['concept'])
    else:
      x = self.context.queryNounPhrases(componentAssertionJSON['assignment']['concept'])
      if x: 
        assignments.extend(x)
      else:
        uninstantiatedAssignments.append(componentAssertionJSON['assignment']['concept'])
    branchPhrase = componentAssertionJSON['target']['component']['branch']
    for uninstantiatedAssignment in uninstantiatedAssignments:
      assignment = self.context.newNounPhrase(None, uninstantiatedAssignment)
      assignment.classify(branchPhrase)
      assignments.append(assignment)
    print assignments
    for assignment in assignments:
      for stem in stems:    
        self.context.setComponent(stem, branchPhrase, assignment)
  
  def assertTaxonomyAssignment(self, taxonomyAssignmentJSON):
    parents = list()
    children = list()
    def extractConcept(JSON):
      return JSON['concept']
    if isinstance(taxonomyAssignmentJSON['parent'], list): 
      parents.extend(map(extractConcept, taxonomyAssignmentJSON['parent']))
    else:
      parents.append(taxonomyAssignmentJSON['parent']['concept'])
    if isinstance(taxonomyAssignmentJSON['child'], list): 
      children.extend(map(extractConcept, taxonomyAssignmentJSON['child']))
    else:
      children.append(taxonomyAssignmentJSON['child']['concept'])
    c = Concept()
    for parent in parents:
      for child in children:
        c.classify(child, parent)
  
  def assertSynonymAssignment(self, synonymAssignmentJSON):
    synonyms = synonymAssignmentJSON['concepts']
    Concept().equate(*synonyms)
        
  def assertStatement(self, statement):
    #TODO: implement arithmetic operation assertion
    if 'concept' in statement:
      self.assertConcept(statement['concept'])
    elif 'component' in statement:
      self.assertComponent(statement['component'])
    elif 'component_assignment' in statement:
      self.assertComponentAssignment(statement['component_assignment'])
    elif 'taxonomy_assignment' in statement:
      self.assertTaxonomyAssignment(statement['taxonomy_assignment'])
    elif 'synonym_assignment' in  statement:
      self.assertSynonymAssignment(statement['synonym_assignment'])
  
  def queryConcept(self, JSON):
    return self.context.queryNounPhrases(JSON['concept'])
  
  def queryComponent(self, JSON):
    return self.retrieveComponent(JSON['component']['stem'], JSON['component']['branch'], assertBranches=False)
          
  def interpret(self, JSON):
    if 'statement' in JSON:
      self.assertStatement(JSON['statement'])
      return None
    elif 'query' in JSON:
      results = list()
      if 'concept' in JSON['query']:
        results = self.queryConcept(JSON['query'])
      elif 'component' in JSON['query']:
        results = self.queryComponent(JSON['query'])
      return results
    
  
    