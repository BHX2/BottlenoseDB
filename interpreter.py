import re
from concepts import Concept
from pattern.en import singularize

class Interpreter:
  def __init__(self, context):
    self.context = context
    
  def setContext(self, context):
    self.context = context
  
  def retrieveComponent(self, stemJSON, branchPhrase, returnLastStems=False, assertBranches=True):
    branchPhrase = str(singularize(branchPhrase))
    if 'stem' in stemJSON:
      stems = self.retrieveComponent(stemJSON['stem'], stemJSON['branch'], False, assertBranches)
      if not isinstance(stems, set): 
        temp = set()
        temp.add(stems)
        stems = temp
      edges = self.context.componentGraph.out_edges(stems, data=True)
      branches = set()
      for edge in edges:
        if edge[2]['label'] == branchPhrase or branchPhrase in edge[1].synonyms() or edge[1].isA(branchPhrase):
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
      if self.context.isUniversal:
        candidateStems = {self.context.queryPrototype(stemJSON['concept'], phraseType='NounPhrase')}
      else:
        candidateStems = self.context.queryNounPhrases(stemJSON['concept'])
      temp = set()
      for candidateStem in candidateStems:
        edges = self.context.componentGraph.out_edges(candidateStem, data=True)
        for edge in edges:
          if edge[2]['label'] == branchPhrase or branchPhrase in edge[1].synonyms() or edge[1].isA(branchPhrase):
            temp.add(edge[0])
      candidateStems = temp
      if len(candidateStems) == 0:
        if assertBranches:
          if self.context.isUniversal:
            stem = self.context.queryPrototype(stemJSON['concept'], phraseType='NounPhrase')
          else:
            stems = self.context.queryNounPhrases(stemJSON['concept'])
            if len(stems) == 0:
              stem = self.context.newNounPhrase(stemJSON['concept'])
            elif len(stems) == 1:
              (stem,) = stems
            else:
              raise Exception('retrieveComponent: Too many matching stems')
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
        if edge[2]['label'] == branchPhrase or branchPhrase in edge[1].synonyms() or edge[1].isA(branchPhrase):
          branches.add(edge[1])
      temp = set()
      for branch in branches:
        if branch in self.context:
          temp.add(branch)
      branches = temp
      if len(branches) == 0:
        if assertBranches:
          branch = self.context.newNounPhrase('unspecified ' + branchPhrase)
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
    response = self.retrieveComponent(JSON['component']['stem'], JSON['component']['branch'], assertBranches=False)
    if not response:
      return []
    else:
      return response
  
  def queryState(self, JSON):
    if 'quality' in JSON['state']['description']:
      if re.match('^!', JSON['state']['description']['quality']):
        raise Exception('Negatives can not be used as filtering criteria.')
    if 'concept' in JSON['state']['subject']:
      if self.context.isUniversal:
        potentialSubjects = {self.context.queryPrototype(JSON['state']['subject']['concept'], phraseType='NounPhrase')}
      else:
        potentialSubjects = self.queryConcept(JSON['state']['subject'])
    elif 'component' in JSON['state']['subject']:
      potentialSubjects = self.queryComponent(JSON['state']['subject'])
    else:
      raise Exception('queryState: Unknown state structure')
    descriptionJSON = JSON['state']['description']
    if 'quantity' in descriptionJSON:
      targetDescriptor = str(descriptionJSON['quantity'])
      if descriptionJSON['units']:
        targetDescriptor += descriptionJSON['units']
    else:
      targetDescriptor = descriptionJSON['quality']
    response = set()
    if potentialSubjects:
      for potentialSubject in potentialSubjects:
        descriptors = self.context.stateGraph.successors(potentialSubject)
        temp = list()
        for descriptor in descriptors:
          temp.extend(descriptor.ancestors())
        descriptors = temp
        if targetDescriptor in descriptors:
          response.add(potentialSubject)
    return response
  
  def queryAction(self, actionJSON, returnActor=True, returnTarget=False):
    if actionJSON['action']['target']:
      if 'concept' in actionJSON['action']['target']:
        if re.match('^!', actionJSON['action']['target']['concept']):
          raise Exception('Negatives can not be used as filtering criteria.')
      elif isinstance(actionJSON['action']['target'], list):
        for target in actionJSON['action']['target']:
          if re.match('^!', target['concept']):
            raise Exception('Negatives can not be used as filtering criteria.')
    if not returnActor and not returnTarget: return {}
    if 'concept' in actionJSON['action']['actor']:
      if self.context.isUniversal:
        potentialActors = {self.context.queryPrototype(actionJSON['action']['actor']['concept'], phraseType='NounPhrase')}
      else:
        potentialActors = self.queryConcept(actionJSON['action']['actor'])
    elif 'component' in actionJSON['action']['actor']:
      potentialActors = self.queryComponent(actionJSON['action']['actor'])
    else:
      raise Exception('queryAction: Unknown action structure')
    if not potentialActors:
      return {}
    temp = set()
    temp2 = set()
    for potentialActor in potentialActors:
      acts = self.context.actionGraph.successors(potentialActor)
      for act in acts:
        if actionJSON['action']['act']['verb'] in act.synonyms() or act.isA(actionJSON['action']['act']['verb']):
          if potentialActor in self.context:
            temp.add(potentialActor)
            temp2.add(act)
    potentialActors = temp
    potentialActs = temp2
    if not actionJSON['action']['target']:
      if returnActor:
        return potentialActors
      else:
        return {}
    temp3 = set()
    temp4 = set()
    for potentialAct in potentialActs:
      potentialTargets = self.context.actionGraph.successors(potentialAct)
      for potentialTarget in potentialTargets:
        if potentialTarget not in self.context: continue
        if isinstance(actionJSON['action']['target'], list):
          for target in actionJSON['action']['target']:
            if actionJSON['action']['target']['concept'] in potentialTarget.synonyms() or potentialTarget.isA(actionJSON['action']['target']['concept']):
              temp3.add(potentialTarget)
              temp4.add(potentialAct)
              break
        elif 'concept' in actionJSON['action']['target']:
          if actionJSON['action']['target']['concept'] in potentialTarget.synonyms() or potentialTarget.isA(actionJSON['action']['target']['concept']):
            temp3.add(potentialTarget)
            temp4.add(potentialAct)
        elif 'component' in actionJSON['action']['target']:
          if potentialTarget in self.queryComponent(actionJSON['action']['target']):
            temp3.add(potentialTarget)
            temp4.add(potentialAct)
        else:
          raise Exception('queryAction: Unknown action structure')
    targets = temp3
    if returnTarget and not returnActor:
      return targets
    acts = temp4
    roles = set()
    for act in acts:
      roles |= set(self.context.actionGraph.predecessors(act))
    actors = potentialActors.intersection(roles)
    if returnActor and returnTarget:
      return actors | targets
    elif returnTarget:
      return targets
    elif returnActor:
      return actors
    
  def assertConcept(self, conceptJSON):
      if self.context.isUniversal:
        return self.context.queryPrototype(conceptJSON['concept'], phraseType='NounPhrase')
      else:
        return self.context.newNounPhrase(conceptJSON['concept'])
  
  def assertState(self, stateJSON):
    if 'concept' in stateJSON['state']['subject']:
      if self.context.isUniversal:
        subject = {self.context.queryPrototype(stateJSON['state']['subject']['concept'], phraseType='NounPhrase')}
      else:
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
        branch = self.context.newNounPhrase('unspecified ' + componentJSON['component']['branch'])
        branch.classify(componentJSON['component']['branch'])
        self.context.setComponent(stem, componentJSON['component']['branch'], branch)
        temp.add(branch)
      branches = temp
    return branches
  
  def removeComponentAssignment(self, stems, branchPhrase, branches, affirmativeConcept=None):
    branchPhrase = str(singularize(branchPhrase))
    if not branches: return 
    matchingBranches = set()
    if not affirmativeConcept:
      if isinstance(branches, set):
        for branch in branches:
          matchingBranches.add(branch)
      else:
        matchingBranches = {branches}
    else:
      if isinstance(branches, set):
        for branch in branches:
          if affirmativeConcept in branch.synonyms() or branch.isA(affirmativeConcept):         
            matchingBranches.add(branch)
      else:
        if affirmativeConcept in branches.synonyms() or branches.isA(affirmativeConcept):   
          matchingBranches = {branches}
    potentialEdges = self.context.componentGraph.out_edges(stems, data=True)
    temp = list()
    for potentialEdge in potentialEdges:
      if potentialEdge[1] in matchingBranches and potentialEdge[2]['label'] == branchPhrase:
        self.context.componentGraph.remove_edge(potentialEdge[0], potentialEdge[1])
        
  def assertComponentAssignment(self, componentAssignmentJSON):
    (branches, stems) = self.retrieveComponent(componentAssignmentJSON['component_assignment']['target']['component']['stem'], componentAssignmentJSON['component_assignment']['target']['component']['branch'], returnLastStems=True, assertBranches=True)
    branchPhrase = componentAssignmentJSON['component_assignment']['target']['component']['branch']
    branchPhrase = str(singularize(branchPhrase))
    def checkIfNegativeAssignment(concept):
      if re.match('^!', concept['concept']):
        affirmativeConcept = concept['concept'][1:]
        self.removeComponentAssignment(stems, branchPhrase, branches, affirmativeConcept)
        return True
      else:
        return False    
    if checkIfNegativeAssignment(componentAssignmentJSON['component_assignment']['assignment']): return
    if branches:
      if isinstance(branches, set):
        for branch in branches:
          self.removeComponentAssignment(stems, branchPhrase, branch)
      else:
        self.removeComponentAssignment(stems, branchPhrase, branches)
    if self.context.isUniversal:
      assignment = {self.context.queryPrototype(componentAssignmentJSON['component_assignment']['assignment']['concept'], phraseType='NounPhrase')}
    else:
      assignment = self.context.queryNounPhrases(componentAssignmentJSON['component_assignment']['assignment']['concept'])
    if not assignment:
      assignment = self.context.newNounPhrase(componentAssignmentJSON['component_assignment']['assignment']['concept'])
    if isinstance(assignment, set):
      if len(assignment) == 1:
        (assignment,) = assignment
      elif len(assignment) > 1:
        raise Exception('assertComponentAssignment: Too many potential assignments')
    for stem in stems:    
      self.context.setComponent(stem, branchPhrase, assignment)
    
  def assertComponentAddition(self, componentAdditionJSON):
    (branches, stems) = self.retrieveComponent(componentAdditionJSON['component_addition']['target']['component']['stem'], componentAdditionJSON['component_addition']['target']['component']['branch'], returnLastStems=True, assertBranches=True)
    def checkIfNegativeAssignment(concept):
      if re.match('^!', concept['concept']):
        affirmativeConcept = concept['concept'][1:]
        branchPhrase = componentAdditionJSON['component_addition']['target']['component']['branch']
        branchPhrase = str(singularize(branchPhrase))
        self.removeComponentAssignment(stems, branchPhrase, branches, affirmativeConcept)
        return True
      else:
        return False
    if isinstance(componentAdditionJSON['component_addition']['assignment'], list):
      componentAdditionJSON['component_addition']['assignment'][:] = [x for x in componentAdditionJSON['component_addition']['assignment'] if not checkIfNegativeAssignment(x)]
    else:
      if checkIfNegativeAssignment(componentAdditionJSON['component_addition']['assignment']): return
    unspecifiedBranches = []
    if branches:
      if isinstance(branches, set):
        for branch in branches:
          if re.match('^unspecified', branch.name): unspecifiedBranches.append(branch)
      else:
        if re.match('^unspecified', branches.name): unspecifiedBranches.append(branches)
    assignments = list()
    uninstantiatedAssignments = list()
    if isinstance(componentAdditionJSON['component_addition']['assignment'], list):
      for concept in componentAdditionJSON['component_addition']['assignment']:
          if self.context.isUniversal:
            x = {self.context.queryPrototype(concept['concept'], phraseType='NounPhrase')}
          else:
            x = self.context.queryNounPhrases(concept['concept'])
          if x: 
            assignments.extend(x)
          else:
            uninstantiatedAssignments.append(concept['concept'])
    else:
      if self.context.isUniversal:
        x = {self.context.queryPrototype(componentAdditionJSON['component_addition']['assignment']['concept'], phraseType='NounPhrase')}
      else:
        x = self.context.queryNounPhrases(componentAdditionJSON['component_addition']['assignment']['concept'])
      if x: 
        assignments.extend(x)
      else:
        uninstantiatedAssignments.append(componentAdditionJSON['component_addition']['assignment']['concept'])
    branchPhrase = componentAdditionJSON['component_addition']['target']['component']['branch']
    branchPhrase = str(singularize(branchPhrase))
    for uninstantiatedAssignment in uninstantiatedAssignments:
      if self.context.isUniversal:
        assignment = self.context.queryPrototype(uninstantiatedAssignment, phraseType='NounPhrase')
      else:
        assignment = self.context.newNounPhrase(uninstantiatedAssignment)
      assignment.classify(branchPhrase)
      assignments.append(assignment)
    for assignment in assignments:
      if len(unspecifiedBranches) > 0:
        self.context.mergeConcepts(assignment, unspecifiedBranches.pop())
      else:
        for stem in stems:    
          self.context.setComponent(stem, branchPhrase, assignment)
  
  def potentiateComponentTaxonomy(self, componentJSON, parentJSON):
    print 'potentiateComponentTaxonomy: Yet to be implemented method'
  
  def assertTaxonomyAssignment(self, taxonomyAssignmentJSON):
    parents = list()
    children = list()
    def extractConcept(JSON):
      return JSON['concept']
    if 'component' in taxonomyAssignmentJSON['taxonomy_assignment']['parent']:
      raise Exception('assertTaxonomyAssignment: Cannot use /= to assert taxonomy of a component')
    elif isinstance(taxonomyAssignmentJSON['taxonomy_assignment']['parent'], list): 
      parents.extend(map(extractConcept, taxonomyAssignmentJSON['taxonomy_assignment']['parent']))
    else:
      parents.append(taxonomyAssignmentJSON['taxonomy_assignment']['parent']['concept'])
    if 'component' in taxonomyAssignmentJSON['taxonomy_assignment']['child']:
      self.potentiateComponentTaxonomy(taxonomyAssignmentJSON['taxonomy_assignment']['child'], taxonomyAssignmentJSON['taxonomy_assignment']['parent'])
      return
    elif isinstance(taxonomyAssignmentJSON['taxonomy_assignment']['child'], list): 
      children.extend(map(extractConcept, taxonomyAssignmentJSON['taxonomy_assignment']['child']))
    else:
      children.append(taxonomyAssignmentJSON['taxonomy_assignment']['child']['concept'])
    c = Concept()
    for parent in parents:
      for child in children:
        c.classify(child, parent)
    for child in children:
      examples = self.context.queryNounPhrases(child)
      if not examples:
        if self.context.isUniversal:
          self.context.queryPrototype(child, phraseType='NounPhrase')
        else:
          self.context.newNounPhrase(child)
  
  def assertSynonymAssignment(self, synonymAssignmentJSON):
    synonyms = synonymAssignmentJSON['synonym_assignment']['concepts']
    prototypes = []
    if self.context.isUniversal:
      for synonym in synonyms:
        if synonym in self.context.prototypes:
          prototypes.append(synonym)
    if prototypes:
      primaryPrototype = self.context.queryPrototype(synonyms[0], phraseType='NounPhrase')
      for prototype in prototypes:
        if not primaryPrototype is prototype:
          self.context.mergeConcepts(self.context.queryPrototype(prototype, phraseType='NounPhrase'), primaryPrototype)
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
      if self.context.isUniversal:
        potentialActors = self.context.queryPrototype(actionJSON['action']['actor']['concept'], phraseType='NounPhrase')
      else:
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
          if self.context.isUniversal:
            moreTargets = self.context.queryPrototype(conceptJSON['concept'], phraseType='NounPhrase')
          else:
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
        if self.context.isUniversal:
          moreTargets = self.context.queryPrototype(actionJSON['action']['target']['concept'], phraseType='NounPhrase')
        else:
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
    #TODO: implement variable assignment
    if 'concept' in statementJSON['statement']:
      if re.match('^!', statementJSON['statement']['concept']):
        affirmativeConcept = statementJSON['statement']['concept'][1:]
        if not affirmativeConcept:
          return self.context.newNounPhrase('!')
        if self.context.isUniversal:
          match = self.context.queryPrototype(affirmativeConcept, phraseType='NounPhrase')
          if match:
            self.context.remove(match)
        else:
          matches = self.context.queryNounPhrases(affirmativeConcept)
          if matches:
            if len(matches) == 1:
              (match,) = matches
              self.context.remove(match)
            if len(matches) > 1:
              raise Exception('assertConcept: Too many matching concepts')
      else:
        self.assertConcept(statementJSON['statement'])
    elif 'component' in statementJSON['statement']:
      self.assertComponent(statementJSON['statement'])
    elif 'component_assignment' in statementJSON['statement']:
      self.assertComponentAssignment(statementJSON['statement'])
    elif 'component_addition' in statementJSON['statement']:
      self.assertComponentAddition(statementJSON['statement'])
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
      elif 'state' in JSON['query']:
        results = self.queryState(JSON['query'])
      elif 'action' in JSON['query']:
        results = self.queryAction(JSON['query'], returnActor=True)
      return results
    
  
    