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
      temp = set()
      for branch in branches:
        if branch in self.context:
          temp.add(branch)
      branches = temp
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
      temp = set()
      for branch in branches:
        if branch in self.context:
          temp.add(branch)
      branches = temp
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
 
  def queryConcept(self, JSON):
    return self.context.queryNounPhrases(JSON['concept'])
  
  def queryComponent(self, JSON):
    return self.retrieveComponent(JSON['component']['stem'], JSON['component']['branch'], assertBranches=False)
  
  def queryState(self, JSON):
    potentialSubjects = self.queryConcept(JSON['state']['subject'])
    descriptionJSON = JSON['state']['description']
    if 'quantity' in descriptionJSON:
      targetDescriptor = str(descriptionJSON['quantity'])
      if descriptionJSON['units']:
        targetDescriptor += descriptionJSON['units']
    else:
      targetDescriptor = descriptionJSON['quality']    
    for potentialSubject in potentialSubjects:
      descriptors = self.context.stateGraph.succesors(potentialSubject)
      temp = list()
      for descriptor in descriptors:
        temp.extend(descriptor.parents())
      descriptors = temp
      if targetDescriptor in descriptors:
        yield potentialSubject
  
  def assertConcept(self, conceptJSON):
    return self.context.newNounPhrase(conceptJSON['concept'])
  
  def assertState(self, stateJSON):
    if 'concept' in stateJSON['state']['subject']:
      subject = self.queryConcept(stateJSON['state']['subject'])
    elif 'component' in stateJSON['state']['subject']:
      subject = self.queryComponent(stateJSON['state']['subject'])
    else:
      raise Exception('assertState: Unknown state structure')
    if not subject:
      if 'concept' in stateJSON['state']['subject']:
        subject = self.assertConcept(stateJSON['state']['subject'])
      elif 'component' in stateJSON['state']['subject']:
        subject = self.assertComponent(stateJSON['state']['subject'])
      else:
        raise Exception('assertState: Unknown state structure')
    if isinstance(subject, set):
      if len(subject) == 1:
        (subject,) = subject
      elif len(subject) > 1:
        raise Exception('assertState: Too many potential subjects')
    descriptionJSON = stateJSON['state']['description']
    if 'quantity' in descriptionJSON:
      description = str(descriptionJSON['quantity'])
      if descriptionJSON['units']:
        description += descriptionJSON['units']
    else:
      description = descriptionJSON['quality']  
    descriptor = self.context.newDescriptor(description)
    return self.context.setState(subject, descriptor)
  
  def assertComponent(self, componentJSON):
    (branches, stems) = self.retrieveComponent(componentJSON['component']['stem'], componentJSON['component']['branch'], returnLastStems=True, assertBranches=True)
    if not branches:
      temp = set()
      for stem in stems:    
        branch = self.context.newNounPhrase(None, 'unspecified')
        branch.classify(componentJSON['component']['branch'])
        self.context.setComponent(stem, componentJSON['component']['branch'], branch)
        temp.add(branch)
      branches = temp
    return branches
  
  def assertComponentAssignment(self, componentAssertionJSON):
    #TODO: implement merger with unspecified rather than just deleting them immediately
    (branches, stems) = self.retrieveComponent(componentAssertionJSON['component_assignment']['target']['component']['stem'], componentAssertionJSON['component_assignment']['target']['component']['branch'], returnLastStems=True, assertBranches=True)
    if branches:
      if isinstance(branches, set):
        for branch in branches:
          if branch.isA('unspecified'): self.context.remove(branch)
      else:
        if branches.isA('unspecified'): self.context.remove(branches)
    assignments = list()
    uninstantiatedAssignments = list()
    if isinstance(componentAssertionJSON['component_assignment']['assignment'], list):
      for concept in componentAssertionJSON['component_assignment']['assignment']:
          x = self.context.queryNounPhrases(concept['concept'])
          if x: 
            assignments.extend(x)
          else:
            uninstantiatedAssignments.append(concept['concept'])
    else:
      x = self.context.queryNounPhrases(componentAssertionJSON['component_assignment']['assignment']['concept'])
      if x: 
        assignments.extend(x)
      else:
        uninstantiatedAssignments.append(componentAssertionJSON['component_assignment']['assignment']['concept'])
    branchPhrase = componentAssertionJSON['component_assignment']['target']['component']['branch']
    for uninstantiatedAssignment in uninstantiatedAssignments:
      assignment = self.context.newNounPhrase(None, uninstantiatedAssignment)
      assignment.classify(branchPhrase)
      assignments.append(assignment)
    for assignment in assignments:
      for stem in stems:    
        self.context.setComponent(stem, branchPhrase, assignment)
  
  def assertTaxonomyAssignment(self, taxonomyAssignmentJSON):
    parents = list()
    children = list()
    def extractConcept(JSON):
      return JSON['concept']
    if isinstance(taxonomyAssignmentJSON['taxonomy_assignment']['parent'], list): 
      parents.extend(map(extractConcept, taxonomyAssignmentJSON['taxonomy_assignment']['parent']))
    else:
      parents.append(taxonomyAssignmentJSON['taxonomy_assignment']['parent']['concept'])
    if isinstance(taxonomyAssignmentJSON['taxonomy_assignment']['child'], list): 
      children.extend(map(extractConcept, taxonomyAssignmentJSON['taxonomy_assignment']['child']))
    else:
      children.append(taxonomyAssignmentJSON['taxonomy_assignment']['child']['concept'])
    c = Concept()
    for parent in parents:
      for child in children:
        c.classify(child, parent)
  
  def assertSynonymAssignment(self, synonymAssignmentJSON):
    synonyms = synonymAssignmentJSON['synonym_assignment']['concepts']
    Concept().equate(*synonyms)
    
  def assertAction(self, actionJSON):
    actor = None
    if 'component' in actionJSON['action']['actor']:
      potentialActors = self.queryComponent(actionJSON['action']['actor'])
      if potentialActors:
        if isinstance(potentialActors, set):
          if len(potentialActors) == 1:
            (actor,) = potentialActors
          else:
            raise Exception('assertAction: Too many suitable actors found')
        else:
          actor = potentialActors
      else:
        actor = self.assertComponent(actionJSON['action']['actor'])
        if isinstance(actor, set):
          if len(actor) == 1:
            (actor,) = actor
          else:
            raise Exception('assertAction: Too many suitable actors found')
    elif 'concept' in actionJSON['action']['actor']:
      potentialActors = self.queryConcept(actionJSON['action']['actor'])
      if potentialActors:
        if isinstance(potentialActors, set):
          if len(potentialActors) == 1:
            (actor,) = potentialActors
          else:
            raise Exception('assertAction: Too many suitable actors found')
        else:
          actor = potentialActors
      else:
        actor = self.assertConcept(actionJSON['action']['actor'])
        if isinstance(actor, set):
          if len(actor) == 1:
            (actor,) = actor
          else:
            raise Exception('assertAction: Too many suitable actors found')
    if not actor:
      raise Exception('assertAction: No suitable actors found')
    targets = []
    if actionJSON['action']['target']:
      if isinstance(actionJSON['action']['target'], list):
        for conceptJSON in actionJSON['action']['target']:
          moreTargets = self.queryConcept(conceptJSON)
          if not moreTargets:
            moreTargets = self.assertConcept(conceptJSON)
          if isinstance(moreTargets, set):
            targets.extend(moreTargets)
          else:
            targets.append(moreTargets)
      elif 'component' in actionJSON['action']['target']:
        moreTargets = self.queryComponent(actionJSON['action']['target'])
        if not moreTargets:
          moreTargets = self.assertComponent(actionJSON['action']['target'])
        if isinstance(moreTargets, set):
          targets.extend(moreTargets)
        else:
          targets.append(moreTargets)
      elif 'concept' in actionJSON['action']['target']:
        moreTargets = self.queryConcept(actionJSON['action']['target'])
        if not moreTargets:
          moreTargets = self.assertConcept(actionJSON['action']['target'])
        if isinstance(moreTargets, set):
          targets.extend(moreTargets)
        else:
          targets.append(moreTargets)
    else:
      act = self.context.newVerbPhrase(actionJSON['action']['act']['verb'])
      self.context.setAction(actor, act)
    if targets:
      for target in targets:
        act = self.context.newVerbPhrase(actionJSON['action']['act']['verb'])
        self.context.setAction(actor, act, target)
            
  def assertStatement(self, statementJSON):
    #TODO: implement arithmetic operation assertion
    if 'concept' in statementJSON['statement']:
      self.assertConcept(statementJSON['statement'])
    elif 'component' in statementJSON['statement']:
      self.assertComponent(statementJSON['statement'])
    elif 'component_assignment' in statementJSON['statement']:
      self.assertComponentAssignment(statementJSON['statement'])
    elif 'taxonomy_assignment' in statementJSON['statement']:
      self.assertTaxonomyAssignment(statementJSON['statement'])
    elif 'synonym_assignment' in  statementJSON['statement']:
      self.assertSynonymAssignment(statementJSON['statement'])
    elif 'action' in statementJSON['statement']:
      self.assertAction(statementJSON['statement'])
    elif 'state' in statementJSON['statement']:
      self.assertState(statementJSON['statement'])
          
  def interpret(self, JSON):
    if 'statement' in JSON:
      self.assertStatement(JSON)
      return None
    elif 'query' in JSON:
      results = list()
      if 'concept' in JSON['query']:
        results = self.queryConcept(JSON['query'])
      elif 'component' in JSON['query']:
        results = self.queryComponent(JSON['query'])
      return results
    
  
    