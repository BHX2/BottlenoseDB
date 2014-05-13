import re
from concepts import Concept
from clauses import Clause
from equations import Equation
import utilities

class Interpreter:
  def __init__(self, context):
    self.context = context
    
  def setContext(self, context):
    self.context = context
  
  def retrieveComponent(self, stemJSON, branchPhrase, branchFilter=None, assertBranches=True, initiatingClauseHash=None, originalJSON=None, depth=0):
    if 'stem' in stemJSON:
      if depth == 0:
        stems = self.retrieveComponent(stemJSON['stem'], stemJSON['branch'], None, assertBranches, initiatingClauseHash, stemJSON, depth=depth+1)
      else:
        stems = self.retrieveComponent(stemJSON['stem'], stemJSON['branch'], None, assertBranches, initiatingClauseHash, originalJSON, depth=depth+1)
    else:
      if 'concept' not in stemJSON: 
        raise Exception('retrieveComponent: Unknown tree structure')
      if not originalJSON:
        originalJSON = stemJSON
      if 'concept' in originalJSON:
        stems = self.queryConcept(originalJSON)
      else:
        stems = self.retrieveRoots(originalJSON) 
      stems = set([x for x in stems if x in self.context]) 
      roots = stems
    
    if assertBranches:
      if len(stems) == 0:
          stem = self.assertConcept(stemJSON, initiatingClauseHash)
      elif len(stems) == 1:
        (stem,) = stems
      else:
        stem = self.context.findLastReferenced(stems)
        #raise Exception('retrieveComponent: Too many matching stems')
      stems = {stem}
    else:
      if len(stems) == 0:
        return set()
      
    edges = self.context.componentGraph.out_edges(stems, data=True)
    branches = set()
    for edge in edges:
      if edge[2]['label'] == branchPhrase:
        if branchFilter:
          if edge[1].isA(branchFilter):
            branches.add(edge[1])
        else:
          branches.add(edge[1])
    if len(branches) == 0:
      if assertBranches:
        branch = self.context.newNounPhrase(branchPhrase)
        if self.context.__class__.__name__ == 'Subcontext':
          self.context.supercontext.incorporateConcept(branch)
        self.context.setComponent(stem, branchPhrase, branch, initiatingClauseHash=initiatingClauseHash)
        #branch.classify(utilities.sanitize(branchPhrase).split()[-1])
        branches.add(branch)
    return branches
 
  def generateLabelChain(self, JSON):
    chain = list()
    if 'concept' in JSON:
      chain.append(JSON['concept'])
    else:
      chain.extend(self.generateLabelChain(JSON['stem']))
      chain.append(JSON['branch'])
    return chain
 
  def retrieveRoots(self, chain, rootsAndCurrentBranches=None, filter=None):
    if isinstance(chain, dict):
      if 'component' in chain:
        chain = chain['component']
      chain = self.generateLabelChain(chain)
    elif not isinstance(chain, list):
      raise Exception('retrieveRoots: Unexpected parameter')
    if not filter or isinstance(filter, dict):
      filterFromConcept = None
    else:
      filterFromConcept = filter
    if not rootsAndCurrentBranches:
      roots = self.context.queryNounPhrases(chain.pop(0))
      rootsAndCurrentBranches = list()
      for root in roots:
        rootsAndCurrentBranches.append((root, root))    
    branchPhrase = chain.pop(0)
    if len(chain) == 0 and filter:
      if isinstance(filter, dict):
        filterFromConcept = filter['concept']
      else:
        filterFromConcept = filter
    rootsAndNextBranches = list()
    for rootBranchTuple in rootsAndCurrentBranches:
      if rootBranchTuple[1] in self.context.componentGraph:
        nextEdges = self.context.componentGraph.out_edges(rootBranchTuple[1], data=True)
        nextBranches = list()
        for edge in nextEdges:
          if edge[2]['label'] == branchPhrase:
            if filterFromConcept:
              if edge[1].isA(filterFromConcept) or edge[1] is self.context.queryHash(filterFromConcept):
                nextBranches.append(edge[1])
            else:
              nextBranches.append(edge[1])
      if len(nextBranches) > 0:
        rootsAndNextBranches.append((rootBranchTuple[0], nextBranches))
    if not rootsAndNextBranches: 
      return []
    if len(chain) == 0:
      return map(lambda x: x[0], rootsAndNextBranches)
    elif len(chain) == 1:
      if isinstance(filter, dict):
        return self.retrieveRoots(chain, rootsAndNextBranches, filter=filter['concept'])
      else:
        return self.retrieveRoots(chain, rootsAndNextBranches, filter)
    else:
      return self.retrieveRoots(chain, rootsAndNextBranches)
      
  def queryConcept(self, JSON):
    return self.context.queryNounPhrases(JSON['concept'])
  
  def queryComponent(self, JSON):
    return self.retrieveComponent(JSON['component']['stem'], JSON['component']['branch'], branchFilter=None, assertBranches=False)
  
  def queryComponentAssignment(self, JSON):
    return self.retrieveComponent(JSON['component_assignment']['target']['component']['stem'], JSON['component_assignment']['target']['component']['branch'], branchFilter=JSON['component_assignment']['assignment']['concept'], assertBranches=False)
    
  def queryState(self, JSON):
    response = set()
    if 'quality' in JSON['state']['description']:
      if re.match('^!', JSON['state']['description']['quality']):
        raise Exception('Negatives can not be used as filtering criteria.')
    if 'concept' in JSON['state']['subject']:
      potentialSubjects = self.queryConcept(JSON['state']['subject'])
    elif 'component' in JSON['state']['subject']:
      potentialSubjects = self.queryComponent(JSON['state']['subject'])
    else:
      raise Exception('queryState: Unknown state structure')
    descriptionJSON = JSON['state']['description']
    if 'quantity' in descriptionJSON:
      targetDescriptor = descriptionJSON['quantity']
      if potentialSubjects:
        for potentialSubject in potentialSubjects:
          descriptors = self.context.stateGraph.successors(potentialSubject)
          for descriptor in descriptors:
            if descriptor.isQuantity:
              if descriptor.quantity == descriptionJSON['quantity']:
                response.add(potentialSubject)
    else:
      targetDescriptor = descriptionJSON['quality']
      if potentialSubjects:
        for potentialSubject in potentialSubjects:
          descriptors = self.context.stateGraph.successors(potentialSubject)
          for descriptor in descriptors:
            if descriptor == targetDescriptor or descriptor.isA(targetDescriptor):
              response.add(potentialSubject)
    return response
  
  def queryQuantitativeState(self, JSON, returnVariable=False):
    if 'concept' in JSON:
      potentialVariables = self.queryConcept(JSON)
    elif 'component' in JSON:
      potentialVariables = self.queryComponent(JSON)
    else:
      raise Exception('queryQuantity: Only concept and components can be variables')
    if len(potentialVariables) == 1:
      (variable,) = potentialVariables
    else:
      variable = self.context.findLastReferenced(potentialVariables)
      #raise Exception('queryQuantitativeState: Too many potential variables')
    descriptors = self.context.stateGraph.successors(variable)
    quantitativeStates = [x for x in descriptors if x.isQuantity]
    quantities = map(lambda x: x.quantity, quantitativeStates)
    if len(quantities) > 1:
      average = sum(quantities) / float(len(quantities))
    elif len(quantities) == 1:
      average = quantities[0]
    else:
      average = None
    if returnVariable:
      return (average, variable)
    else:
      return average
  
  def queryAction(self, actionJSON, returnActor=True, returnTarget=False):
    if actionJSON['action']['target']:
      if 'concept' in actionJSON['action']['target']:
        if re.match('^!', actionJSON['action']['target']['concept']):
          raise Exception('Negatives can not be used as filtering criteria.')
      elif isinstance(actionJSON['action']['target'], list):
        for target in actionJSON['action']['target']:
          if re.match('^!', target['concept']):
            raise Exception('Negatives can not be used as filtering criteria.')
    if not returnActor and not returnTarget: return set()
    if not actionJSON['action']['actor']:
      potentialActors = set()
      potentialActs = self.context.queryVerbPhrases(actionJSON['action']['act']['verb'])
    else:
      if 'concept' in actionJSON['action']['actor']:
        potentialActors = self.queryConcept(actionJSON['action']['actor'])
      elif 'component' in actionJSON['action']['actor']:
        potentialActors = self.queryComponent(actionJSON['action']['actor'])
      else:
        raise Exception('queryAction: Unknown action structure')
      if not potentialActors:
        return set()
      temp = set()
      temp2 = set()
      for potentialActor in potentialActors:
        acts = self.context.actionGraph.successors(potentialActor)
        for act in acts:
          if act.isA(actionJSON['action']['act']['verb']):
            if potentialActor in self.context:
              temp.add(potentialActor)
              temp2.add(act)
      potentialActors = temp
      potentialActs = temp2
      if not actionJSON['action']['target']:
        if returnActor:
          return potentialActors
        else:
          return set()
    temp3 = set()
    temp4 = set()
    for potentialAct in potentialActs:
      potentialTargets = self.context.actionGraph.successors(potentialAct)
      for potentialTarget in potentialTargets:
        if potentialTarget not in self.context: continue
        if isinstance(actionJSON['action']['target'], list):
          for target in actionJSON['action']['target']:
            if potentialTarget.isA(actionJSON['action']['target']['concept']):
              temp3.add(potentialTarget)
              temp4.add(potentialAct)
              break
        elif 'concept' in actionJSON['action']['target']:
          if potentialTarget.isA(actionJSON['action']['target']['concept']):
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
  
  def queryComparison(self, JSON):
    (variable, item1) = self.queryQuantitativeState(JSON['comparison']['variable'], returnVariable=True)
    item2 = None
    if 'quantity' in JSON['comparison']['measure']:
      measure = float(JSON['comparison']['measure']['quantity'])
    else:
      (measure, item2) = self.queryQuantitativeState(JSON['comparison']['measure'], returnVariable=True)
    if variable == None or measure == None: 
      return set()
    response = {item1}
    if item2: 
      response.add(item2)
    sign = JSON['comparison']['sign']
    if sign == '==':
      if variable == measure:
        return response
      else:
        return set()
    elif sign == '!=':
      if variable != measure:
        return response
      else:
        return set()
    elif sign == '>':
      if variable > measure:
        return response
      else:
        return set()      
    elif sign == '>=':
      if variable >= measure:
        return response
      else:
        return set()      
    elif sign == '<':
      if variable < measure:
        return response
      else:
        return set()      
    elif sign == '<=':
      if variable <= measure:
        return response
      else:
        return set()      
    else:
      raise Exception('queryComparison: Unknown comparison operator')
  
  def assertConcept(self, conceptJSON, initiatingClauseHash=None):
    results = self.queryConcept(conceptJSON)
    if not results:
      concept = self.context.newNounPhrase(conceptJSON['concept'], initiatingClauseHash)
    elif isinstance(results, set):
      if len(results) == 1:
        (concept,) = results
      else:
        concept = self.context.findLastReferenced(results)
    else:
      concept = results
    return concept
  
  def assertState(self, stateJSON, initiatingClauseHash=None):
    if 'concept' in stateJSON['state']['subject']:
      subject = self.queryConcept(stateJSON['state']['subject'])
    elif 'component' in stateJSON['state']['subject']:
      subject = self.queryComponent(stateJSON['state']['subject'])
    else:
      raise Exception('assertState: Unknown state structure')
    if not subject:
      if 'concept' in stateJSON['state']['subject']:
        subject = self.assertConcept(stateJSON['state']['subject'], initiatingClauseHash)
      elif 'component' in stateJSON['state']['subject']:
        subject = self.assertComponent(stateJSON['state']['subject'], initiatingClauseHash)
      else:
        raise Exception('assertState: Unknown state structure')
    if isinstance(subject, set):
      if len(subject) == 1:
        (subject,) = subject
      elif len(subject) > 1:
        subject = self.context.findLastReferenced(subject)
        #raise Exception('assertState: Too many potential subjects')
    descriptionJSON = stateJSON['state']['description']
    if 'quantity' in descriptionJSON:
      description = str(descriptionJSON['quantity'])
    else:
      description = descriptionJSON['quality']  
    descriptor = self.context.newDescriptor(description)
    self.context.setState(subject, descriptor, initiatingClauseHash)
  
  def assertComponent(self, componentJSON, initiatingClauseHash=None):
    components = self.retrieveComponent(componentJSON['component']['stem'], componentJSON['component']['branch'], assertBranches=True, initiatingClauseHash=initiatingClauseHash)
    if len(components) == 1:
      (component,) = components
    else:
      component = self.findLastReferenced(components)
    return component
  
  def removeComponentAssignment(self, stem, branchPhrase, branches, affirmativeConcept=None, initiatingClauseHash=None):
    if not branches: 
      branches = set()
    elif isinstance(branches, list):
      branches = set(branches)
    elif not isinstance(branches, set):
      branches = {branches}
    if stem in self.context.potentialComponentGraph:
        branches |= set(self.context.potentialComponentGraph.successors(stem))
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
          if branch.isA(affirmativeConcept):         
            matchingBranches.add(branch)
      else:
        if branches.isA(affirmativeConcept):   
          matchingBranches = {branches}
    potentialEdges = self.context.componentGraph.out_edges(stem, data=True)
    if stem in self.context.potentialComponentGraph:
      potentialEdges.extend(self.context.potentialComponentGraph.out_edges(stem, data=True))
    for potentialEdge in potentialEdges:
      if potentialEdge[1] in matchingBranches and potentialEdge[2]['label'] == branchPhrase:
        self.context.unsetComponent(potentialEdge[0], branchPhrase, potentialEdge[1], initiatingClauseHash)
        
  def assertComponentAssignment(self, componentAssignmentJSON, initiatingClauseHash=None):
    if 'stem' in componentAssignmentJSON['component_assignment']['target']['component']['stem']:
      stems = self.retrieveComponent(componentAssignmentJSON['component_assignment']['target']['component']['stem']['stem'], componentAssignmentJSON['component_assignment']['target']['component']['stem']['branch'], assertBranches=True, initiatingClauseHash=initiatingClauseHash)
      if isinstance(stems, set):
        stem = self.context.findLastReferenced(stems)
        #raise Exception('assertComponentAssignment: Too many potential stems')
      else:
        stem = stems
    elif 'concept' in componentAssignmentJSON['component_assignment']['target']['component']['stem']:
      stem = {self.assertConcept(componentAssignmentJSON['component_assignment']['target']['component']['stem'], initiatingClauseHash)}
    else:
      raise Exception('assertComponentAssignment: Unknown component structure')
    branchPhrase = componentAssignmentJSON['component_assignment']['target']['component']['branch']
    branches = self.retrieveComponent(componentAssignmentJSON['component_assignment']['target']['component']['stem'], componentAssignmentJSON['component_assignment']['target']['component']['branch'], assertBranches=True, initiatingClauseHash=initiatingClauseHash)    
    def checkIfNegativeAssignment(concept):
      if re.match('^!', concept['concept']):
        affirmativeConcept = concept['concept'][1:]
        self.removeComponentAssignment(stem, branchPhrase, branches, affirmativeConcept, initiatingClauseHash)
        return True
      else:
        return False    
    if checkIfNegativeAssignment(componentAssignmentJSON['component_assignment']['assignment']): return
    if branches and not initiatingClauseHash:
      if isinstance(branches, set):
        for branch in branches:
          if branch.name != branchPhrase:
            self.removeComponentAssignment(stem, branchPhrase, branch, initiatingClauseHash)
      else:
        if branches.name != branchPhrase:
          self.removeComponentAssignment(stem, branchPhrase, branches, initiatingClauseHash)
    componentAdditionJSON = {'component_addition': {'target': componentAssignmentJSON['component_assignment']['target'], 'addition': componentAssignmentJSON['component_assignment']['assignment']}}
    self.assertComponentAddition(componentAdditionJSON, initiatingClauseHash)
    
  def assertComponentAddition(self, componentAdditionJSON, initiatingClauseHash=None):
    if 'stem' in componentAdditionJSON['component_addition']['target']['component']['stem']:
      stems = self.retrieveComponent(componentAdditionJSON['component_addition']['target']['component']['stem']['stem'], componentAdditionJSON['component_addition']['target']['component']['stem']['branch'], assertBranches=True, initiatingClauseHash=initiatingClauseHash)
      if isinstance(stems, set):
        stem = self.context.findLastReferenced(stems)
        #raise Exception('assertComponentAssignment: Too many potential stems')
      else:
        stem = stems
    elif 'concept' in componentAdditionJSON['component_addition']['target']['component']['stem']:
      stem = self.assertConcept(componentAdditionJSON['component_addition']['target']['component']['stem'], initiatingClauseHash)
    else:
      raise Exception('assertComponentAddition: Unknown component structure')
    branchPhrase = utilities.camelCase(componentAdditionJSON['component_addition']['target']['component']['branch'])
    branches = self.retrieveComponent(componentAdditionJSON['component_addition']['target']['component']['stem'], componentAdditionJSON['component_addition']['target']['component']['branch'], assertBranches=True, initiatingClauseHash=initiatingClauseHash) 
    def checkIfNegativeAssignment(concept):
      if re.match('^!', concept['concept']):
        affirmativeConcept = concept['concept'][1:]
        self.removeComponentAssignment(stem, branchPhrase, branches, affirmativeConcept, initiatingClauseHash)
        return True
      else:
        return False    
    if isinstance(componentAdditionJSON['component_addition']['addition'], list):
      componentAdditionJSON['component_addition']['addition'][:] = [x for x in componentAdditionJSON['component_addition']['addition'] if not checkIfNegativeAssignment(x)]
    else:
      if checkIfNegativeAssignment(componentAdditionJSON['component_addition']['addition']): return
    unspecifiedBranches = []   
    if branches:
      if isinstance(branches, set):
        for branch in branches:
          if branch.name == branchPhrase: unspecifiedBranches.append(branch)
      else:
        if branch.name == branchPhrase: unspecifiedBranches.append(branches)
    assignments = list()
    uninstantiatedAssignments = list()
    if isinstance(componentAdditionJSON['component_addition']['addition'], list):
      for concept in componentAdditionJSON['component_addition']['addition']:
        x = self.context.queryNounPhrases(concept['concept'])
        if x: 
          assignments.extend(x)
        else:
          uninstantiatedAssignments.append(concept['concept'])
    else:
      x = self.context.queryNounPhrases(componentAdditionJSON['component_addition']['addition']['concept'])
      if x: 
        assignments.extend(x)
      else:
        uninstantiatedAssignments.append(componentAdditionJSON['component_addition']['addition']['concept'])
    for uninstantiatedAssignment in uninstantiatedAssignments:
      assignment = self.context.newNounPhrase(uninstantiatedAssignment, initiatingClauseHash)
      #assignment.classify(utilities.sanitize(branchPhrase).split()[-1])
      assignments.append(assignment)
    for assignment in assignments:
      if len(unspecifiedBranches) > 0:
        unspecifiedBranch = unspecifiedBranches.pop()
        unspecifiedBranch.name = 'unspecified' + unspecifiedBranch.name[0].upper() + unspecifiedBranch.name[1:]
        self.context.mergeConcepts(assignment, unspecifiedBranch, initiatingClauseHash)
      else:
        self.context.setComponent(stem, branchPhrase, assignment, initiatingClauseHash)
  
  def assertComponentSubtraction(self, componentSubtractionJSON, initiatingClauseHash):
    newComponentAdditionJSON = {'component_addition': {'target': componentSubtractionJSON['component_subtraction']['target'], 'addition': None}}
    if isinstance(componentSubtractionJSON['component_subtraction']['unassignment'], list):
      newComponentAdditionJSON['component_addition']['addition'] = list()
      for unassignment in componentSubtractionJSON['component_subtraction']['unassignment']:
        if re.match('^!', unassignment['concept']):
          newComponentAdditionJSON['component_addition']['addition'].append({'concept': unassignment['concept'][1:]})
        else:
          newComponentAdditionJSON['component_addition']['addition'].append({'concept': '!' + unassignment['concept']})
    else:
      unassignment = componentSubtractionJSON['component_subtraction']['unassignment']['concept']
      if re.match('^!', unassignment):
        newComponentAdditionJSON['component_addition']['addition'] = {'concept': unassignment[1:]}
      else:
        newComponentAdditionJSON['component_addition']['addition'] = {'concept': '!' + unassignment}
    self.assertComponentAddition(newComponentAdditionJSON, initiatingClauseHash)
  
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
    if isinstance(taxonomyAssignmentJSON['taxonomy_assignment']['child'], list): 
      children.extend(map(extractConcept, taxonomyAssignmentJSON['taxonomy_assignment']['child']))
    else:
      children.append(taxonomyAssignmentJSON['taxonomy_assignment']['child']['concept'])
    self.context.recentlyMentionedPhrases |= set(parents)
    self.context.recentlyMentionedPhrases |= set(children)
    c = Concept()
    for parent in parents:
      for child in children:
        c.classify(child, parent)
    for child in children:
      examples = self.context.queryNounPhrases(child)
      if not examples:
        self.context.newNounPhrase(child)
  
  def assertSynonymAssignment(self, synonymAssignmentJSON):
    synonyms = synonymAssignmentJSON['synonym_assignment']['concepts']
    self.context.recentlyMentionedPhrases |= set(synonyms)
    Concept().equate(*synonyms)
    
  def assertAction(self, actionJSON, initiatingClauseHash=None):
    actor = None
    if 'component' in actionJSON['action']['actor']:
      potentialActors = self.queryComponent(actionJSON['action']['actor'])
      if potentialActors:
        if isinstance(potentialActors, set):
          if len(potentialActors) == 1:
            (actor,) = potentialActors
          else:
            actor = self.context.findLastReferenced(potentialActors)
            #raise Exception('assertAction: Too many suitable actors found')
        else:
          actor = potentialActors
      else:
        actor = self.assertComponent(actionJSON['action']['actor'], initiatingClauseHash)
    elif 'concept' in actionJSON['action']['actor']:
      potentialActors = self.queryConcept(actionJSON['action']['actor'])
      if potentialActors:
        if isinstance(potentialActors, set):
          if len(potentialActors) == 1:
            (actor,) = potentialActors
          else:
            actor = self.context.findLastReferenced(potentialActors)
            #raise Exception('assertAction: Too many suitable actors found')
        else:
          actor = potentialActors
      else:
        actor = self.assertConcept(actionJSON['action']['actor'], initiatingClauseHash)
    if not actor:
      raise Exception('assertAction: No suitable actors found')
    targets = []
    if actionJSON['action']['target']:
      if isinstance(actionJSON['action']['target'], list):
        for conceptJSON in actionJSON['action']['target']:
          moreTargets = self.queryConcept(conceptJSON)
          if not moreTargets:
            target.append(self.assertConcept(conceptJSON, initiatingClauseHash))
          else:
            targets.extend(moreTargets)
      elif 'component' in actionJSON['action']['target']:
        moreTargets = self.queryComponent(actionJSON['action']['target'])
        if not moreTargets:
          targets.append(self.assertComponent(actionJSON['action']['target'], initiatingClauseHash))
        else:
          targets.extend(moreTargets)
      elif 'concept' in actionJSON['action']['target']:
        targets.append(self.assertConcept(actionJSON['action']['target'], initiatingClauseHash))
    else:
      act = self.context.newVerbPhrase(actionJSON['action']['act']['verb'])
      self.context.setAction(actor, act, None, initiatingClauseHash)
    if targets:
      for target in targets:
        act = self.context.newVerbPhrase(actionJSON['action']['act']['verb'])     
        self.context.setAction(actor, act, target, initiatingClauseHash)

  def assertArithmeticOperation(self, arithmeticOperationJSON, initiatingClauseHash=None):
    if initiatingClauseHash:
      raise Exception('assertArithmeticOperation: Arithmetic cannot be potentiated via evidence')
    value = self.queryQuantitativeState(arithmeticOperationJSON['arithmetic_operation']['variable'])
    if value == None:
      value = 0
    newValue = eval(str(value) + arithmeticOperationJSON['arithmetic_operation']['operator'] + arithmeticOperationJSON['arithmetic_operation']['quantity'])
    state = {'state': {'subject': arithmeticOperationJSON['arithmetic_operation']['variable'], 'description': {'quantity': newValue}}}
    self.assertState(state)

  def resolveKnownReferences(self, JSON):
    if isinstance(JSON, list):
      temp = list()
      for x in JSON:
        addition = self.resolveKnownReferences(x)
        if isinstance(addition, list):
          temp.extend(addition)
        else:
          temp.append(addition)
      return temp
    if not isinstance(JSON, dict): 
      return JSON
    elif 'concept' in JSON and re.match('.*\^', JSON['concept'].strip()):
      (concept,) = self.context.queryNounPhrases(JSON['concept'])
      for hashcode in self.context.conceptHashTable:
        if concept is self.context.conceptHashTable[hashcode]:
          return {'concept': str(hashcode)}
    else:
      for key in JSON.keys():
        JSON[key] = self.resolveKnownReferences(JSON[key])
      return JSON  
  
  def solveQueries(self, JSON):
    if isinstance(JSON, list):
      temp = list()
      for x in JSON:
        addition = self.solveQueries(x)
        if isinstance(addition, list):
          temp.extend(addition)
        else:
          temp.append(addition)
      return temp
    if not isinstance(JSON, dict): 
      return JSON
    elif 'concept' in JSON and 'query' in JSON['concept']:
      response = self.query(self.resolveKnownReferences(JSON['concept']))
      if not response: 
        return []
      elif isinstance(response, list) or isinstance(response, set):
        JSON = list()
        for concept in response:
          JSON.append({'concept': concept.name})
          # Using name insteaad of hash at least for now
          '''
          for hashcode in self.context.conceptHashTable:
            if concept is self.context.conceptHashTable[hashcode]:
              JSON.append({'concept': concept.name})
              break
          '''
        return JSON
      else:
        raise Exception('assertStatement: Unknown query response')
    else:
      for key in JSON.keys():
        if key == 'subject' or key == 'actor' or key == 'assignment':
          x = self.solveQueries(JSON[key])
          if isinstance(x, list):
            JSON[key] = x[0]
          else:
            JSON[key] = x
        else:
          JSON[key] = self.solveQueries(JSON[key])
      return JSON
        
  def assertStatement(self, statementJSON, initiatingClauseHash=None):
    if 'AND' in statementJSON or 'OR' in statementJSON:
      for clause in statementJSON.values()[0]:
        self.assertStatement(clause, initiatingClauseHash)
      return
    elif 'NOT' in statementJSON:
      negativeStatement = self.negateStatement(statementJSON.values()[0])
      self.assertStatement(negativeStatement, initiatingClauseHash)
    if 'equation' in statementJSON['statement']:
      equation = Equation.variableHashTable[statementJSON['statement']['equation']]
      equation.solveAndAssertWithInterpreter(self)
      return
    if 'concept' in statementJSON['statement'] and not initiatingClauseHash:
      if re.match('^!', statementJSON['statement']['concept']):
        affirmativeConcept = statementJSON['statement']['concept'][1:]
        if not affirmativeConcept:
          return
        matches = self.context.queryNounPhrases(affirmativeConcept)
        if matches:
          if len(matches) == 1:
            (match,) = matches
            self.context.remove(match)
          if len(matches) > 1:
            match = self.context.findLastReferenced(matches)
            self.context.remove(match)
            #raise Exception('assertConcept: Too many matching concepts')
      else:
        self.assertConcept(statementJSON['statement'], initiatingClauseHash)
    elif 'component' in statementJSON['statement']:
      self.assertComponent(statementJSON['statement'], initiatingClauseHash)
    elif 'component_assignment' in statementJSON['statement']:
      self.assertComponentAssignment(statementJSON['statement'], initiatingClauseHash)
    elif 'component_addition' in statementJSON['statement']:
      self.assertComponentAddition(statementJSON['statement'], initiatingClauseHash)
    elif 'component_subtraction' in statementJSON['statement']:
      self.assertComponentSubtraction(statementJSON['statement'], initiatingClauseHash)
    elif 'taxonomy_assignment' in statementJSON['statement']:
      self.assertTaxonomyAssignment(statementJSON['statement'])
    elif 'synonym_assignment' in  statementJSON['statement']:
      self.assertSynonymAssignment(statementJSON['statement'])
    elif 'action' in statementJSON['statement']:
      self.assertAction(statementJSON['statement'], initiatingClauseHash)
    elif 'state' in statementJSON['statement']:
      self.assertState(statementJSON['statement'], initiatingClauseHash)
    elif 'arithmetic_operation' in statementJSON['statement']:
      self.assertArithmeticOperation(statementJSON['statement'], initiatingClauseHash)
  
  def extractRootsFromQueryResults(self, componentJSON, results, chain=None):
    if not results:
      return []
    if chain == None:
      chain = self.generateLabelChain(componentJSON['component'])
    relationship = chain.pop()
    if len(chain) == 0:
      return results
    else:
      edges = self.context.componentGraph.in_edges(results, data=True)
      nextResults = list()
      for edge in edges:
        if edge[2]['label'] == relationship:
          nextResults.append(edge[0])
      return self.extractRootsFromQueryResults(componentJSON, nextResults, chain)
    
  def query(self, queryJSON):
    results = list()
    subjectJSON = queryJSON['query']['subject']
    if not subjectJSON:
      raise Exception('query: Query must contain subject')
    clauseJSON = queryJSON['query']['clause']
    if not 'concept' in subjectJSON:
      raise Exception('query: Subject must be a simple concept')
    if not clauseJSON:
      return self.queryConcept(subjectJSON)
    if 'concept' in clauseJSON:
      results = self.queryConcept(clauseJSON)
    elif 'component' in clauseJSON:
      if clauseJSON['component']['branch'] == subjectJSON['concept']:
        results = self.queryComponent(clauseJSON)
        subjectJSON = {'concept' : 'thing'}
      else:
        results = self.retrieveRoots(clauseJSON)
    elif 'state' in clauseJSON:
      results = self.queryState(clauseJSON)
      if 'component' in clauseJSON['state']['subject'] and self.generateLabelChain(clauseJSON['state']['subject']['component'])[0] == subjectJSON['concept']:
        if results:
          results = self.extractRootsFromQueryResults(clauseJSON['state']['subject'], results)
    elif 'action' in clauseJSON:
      if clauseJSON['action']['target'] == subjectJSON:
        results = self.queryAction(clauseJSON, returnActor=False, returnTarget=True)
      elif 'component' in clauseJSON['action']['target'] and self.generateLabelChain(clauseJSON['action']['target']['component'])[0] == subjectJSON['concept']:
        results = self.queryAction(clauseJSON, returnActor=False, returnTarget=True)
        if results:
          results = self.extractRootsFromQueryResults(clauseJSON['action']['target'], results)
      elif clauseJSON['action']['actor'] == subjectJSON:
        results = self.queryAction(clauseJSON, returnActor=True, returnTarget=False)
      elif 'component' in clauseJSON['action']['actor'] and self.generateLabelChain(clauseJSON['action']['actor']['component'])[0] == subjectJSON['concept']:
        results = self.queryAction(clauseJSON, returnActor=True, returnTarget=False)
        if results:
          results = self.extractRootsFromQueryResults(clauseJSON['action']['actor'], results)
      else:
        results = self.queryAction(clauseJSON, returnActor=True, returnTarget=True)
    elif 'component_assignment' in clauseJSON:
      if clauseJSON['component_assignment']['target']['component']['branch'] == subjectJSON['concept'] or clauseJSON['component_assignment']['assignment'] == subjectJSON:
        results = self.queryComponentAssignment(clauseJSON)
        subjectJSON = {'concept' : 'thing'}
      else:
        results = self.retrieveRoots(clauseJSON['component_assignment']['target'], filter=clauseJSON['component_assignment']['assignment'])
    elif 'comparison' in clauseJSON:
      results = self.queryComparison(clauseJSON)
    if not results: results = list()
    results = [x for x in results if x.isA(subjectJSON['concept'])]
    return results

  def test(self, JSON):
    results = set()
    if not 'statement' in JSON:
      if 'comparison' in JSON:
        results |= self.queryComparison(JSON)
      elif 'AND' in JSON:
        for subclause in JSON['AND']:
          moreResults = self.test(subclause)
          if isinstance(moreResults, set):
            results |= moreResults
          elif moreResults == False:
            return False
      elif 'OR' in JSON:
        anyTrue = False
        for subclause in JSON['OR']:
          moreResults = self.test(subclause)
          if isinstance(moreResults, set):
            results |= moreResults
            anyTrue = True
          elif moreResults == True:
            anyTrue = True
        if not anyTrue: return False
      elif 'NOT' in JSON:
        if not self.test(JSON['NOT'][0]): return True
    else:
      clauseJSON = JSON['statement']
      if 'state' in clauseJSON:
        results |= self.queryState(clauseJSON)
      elif 'action' in clauseJSON:
        results |= self.queryAction(clauseJSON, returnActor=True, returnTarget=True)
      elif 'component_assignment' in clauseJSON:
        branches = self.queryComponentAssignment(clauseJSON)
        if branches:
          results |= branches
          roots = self.retrieveRoots(clauseJSON['component_assignment']['target'], filter=clauseJSON['component_assignment']['assignment'])
          if roots: 
            results |= set(roots)
      elif 'component' in clauseJSON:
        branches = self.queryComponent(clauseJSON)
        if branches:
          results |= branches
          roots = self.retrieveRoots(clauseJSON)
          if roots: 
            results |= set(roots)
      elif 'concept' in clauseJSON:
        results |= self.queryConcept(clauseJSON)
      elif 'query' in clauseJSON:
        results |= self.query(clauseJSON)
      else:
        raise Exception('test: Unknown clause structure')
    if not results:
      return False
    else:
      return results

  def negateStatement(self, JSON):
    if isinstance(JSON, list):
      temp = list()
      for x in JSON:
        addition = self.negateStatement(x)
        if isinstance(addition, list):
          temp.extend(addition)
        else:
          temp.append(addition)
      return temp
    if not isinstance(JSON, dict): 
      return JSON
    if 'concept' in JSON:
      if re.match('^!', JSON['concept']):
        JSON['concept'] = JSON['concept'][1:]
      else:
        JSON['concept'] = '!' + JSON['concept']
      return JSON
    if 'quality' in JSON:
      if re.match('^!', JSON['quality']):
        JSON['quality'] = JSON['quality'][1:]
      else:
        JSON['quality'] = '!' + JSON['quality']
      return JSON
    elif 'target' in JSON and JSON['target'] == None:
      JSON['target'] = {'concept': '!'}
      return JSON
    else:
      stopKeys = {'component', 'subject', 'actor', 'query', 'arithmetic_operation', 'comparison', 'taxonomy_assignment', 'synonym_assignment'}
      for key in JSON.keys():
        if not key in stopKeys:
          JSON[key] = self.negateStatement(JSON[key])
      return JSON
  
  def processEvidence(self, evidenceJSON):
    independentClause = Clause(evidenceJSON['evidence']['independent_clause'], independent=True)
    if evidenceJSON['evidence']['type'] == 'supporting':
      dependentClause = Clause(evidenceJSON['evidence']['dependent_clause'], independent=False)
    elif evidenceJSON['evidence']['type'] == 'opposing':
      dependentClause = Clause(self.negateStatement(evidenceJSON['evidence']['dependent_clause']), independent=False)
    else:
      raise Exception('processEvidence: Unknown evidence structure')
    independentClause.potentiates(dependentClause)
    
  def processRule(self, ruleJSON):
    independentClause = Clause(ruleJSON['rule']['independent_clause'], independent=True)
    dependentClause = Clause(ruleJSON['rule']['dependent_clause'], independent=False)
    independentClause.mandates(dependentClause)
    
  def processEquation(self, equationJSON):
    equation = Equation(equationJSON)
    independentClause = equation.independentClause()
    dependentClause = equation.dependentClause()
    independentClause.mandates(dependentClause)
  
  def interpret(self, JSON):
    if JSON.keys() == ['statement'] and \
       JSON['statement'].keys() == ['concept'] and \
       isinstance(JSON['statement']['concept'], dict) and\
       JSON['statement']['concept'].keys() == ['query']:
        return self.query(JSON['statement']['concept'])
    elif 'statement' in JSON:
      JSON = self.solveQueries(JSON)
      self.assertStatement(JSON)
      return None
    elif 'equation' in JSON:
      self.processEquation(JSON)
      return None
    elif 'belief' in JSON:
      if 'evidence' in JSON['belief']:
        self.processEvidence(JSON['belief'])
      elif 'rule' in JSON['belief']:
        self.processRule(JSON['belief'])
      return None
      
    
  
    