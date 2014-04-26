from clint.textui import puts, colored, indent

import sys
sys.dont_write_bytecode = True
from concepts import Concept

class Interpreter:
  def __init__(self, context):
    self.context = context
  
  def retrieveComponent(self, stemJSON, branchPhrase, returnLastStems=False):
    if 'stem' in stemJSON:
      stems = self.retrieveComponent(stemJSON['stem'], stemJSON['branch'])
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
      for candidateStem in candidateStems:
        edges = self.context.componentGraph.out_edges(candidateStem, data=True)
        for edge in edges:
          if edge[2]['label'] != branchPhrase and edge[1].name != branchPhrase and not edge[1].isA(branchPhrase):
            candidateStems.remove(edge[1])
      if len(candidateStems) == 0:
        stem = self.context.newNounPhrase(stemJSON['concept'])
      elif len(candidateStems) > 1:
        raise Exception('retrieveComponent: Too many matching stems')
      else:
        (stem,) = candidateStems
      edges = self.context.componentGraph.out_edges(stem, data=True)
      branches = set()
      for edge in edges:
        if edge[2]['label'] == branchPhrase or edge[1].name == branchPhrase:
          branches.add(edge[1])
      if len(branches) == 0:
        branch = self.context.newNounPhrase(None, 'unspecified')
        branch.classify(branchPhrase)
        self.context.setComponent(stem, branchPhrase, branch)
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
    (branches, stems) = self.retrieveComponent(componentJSON['stem'], componentJSON['branch'], returnLastStems=True)
    if not branches:
      for stem in stems:    
        branch = self.context.newNounPhrase(None, 'unspecified')
        branch.classify(componentJSON['branch'])
        self.context.setComponent(stem, componentJSON['branch'], branch)
  
  def assertComponentAssignment(self, componentAssertionJSON):
    (branches, stems) = self.retrieveComponent(componentAssertionJSON['target']['component']['stem'], componentAssertionJSON['target']['component']['branch'], returnLastStems=True)
    if branches:
      if isinstance(branches, set):
        for branch in branches:
          if branch.isA('unspecified'): self.context.removeConcept(branch)
      else:
        if branches.isA('unspecified'): self.context.removeConcept(branches)
    assignments = list()
    if isinstance(componentAssertionJSON['assignment'], list):
      for concept in componentAssertionJSON['assignment']:
          x = self.context.queryExact(concept['concept'])
          if x: assignments.append(x)
    else:
      x = self.context.queryExact(componentAssertionJSON['assignment']['concept'])
      if x: assignments.append(x)

    if not assignments:
      for stem in stems:    
        assignment = self.context.newNounPhrase(None, componentAssertionJSON['assignment']['concept'])
        assignment.classify(componentAssertionJSON['target']['component']['branch'])
        self.context.setComponent(stem, componentAssertionJSON['target']['component']['branch'], assignment)
    else:
      for assignment in assignments:
        for stem in stems:    
          self.context.setComponent(stem, componentAssertionJSON['target']['component']['branch'], assignment)
  
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
  
  def inspectConcept(self, concept):
    if concept.parents():
      puts(colored.green(concept.name) + ' is a ' + ', '.join(concept.parents()))
    else:
      puts(colored.green(concept.name))
    for edge in self.context.componentGraph.out_edges(concept, data=True):
      with indent(2):
        puts(colored.yellow(edge[0].name) + ' (has ' + edge[2]['label'] + ') --> ' + edge[1].name)
    for edge in self.context.componentGraph.in_edges(concept, data=True):
      with indent(2):
        puts(edge[0].name + ' (has ' + edge[2]['label'] + ') --> ' + colored.yellow(edge[1].name))
    for actor_act in self.context.actionGraph.edges(concept):
      with indent(2):
        puts(actor_act[0].name + ' ' + actor_act[1].name)
      for act_target in context.actionGraph.edges(actor_act[1]):
        with indent(8):
          puts(actor_act[0].name + ' (' + act_target[0].name + ') --> ' + act_target[1].name) 
  
  def queryConcept(self, conceptPhrase):
    results = self.context.queryNounPhrases(conceptPhrase)
    if results:
      for result in results:
        self.inspectConcept(result)
    else:
      print 'No matching concepts found.'
  
  def queryComponent(self, componentJSON):
    branches = self.retrieveComponent(componentJSON['stem'], componentJSON['branch'])
    if not branches:
      print 'No matching components found.'
    elif isinstance(branches, list):
      self.inspectConcept(branches)
    else:
      for branch in branches:
        self.inspectConcept(branch)
  
  def interpret(self, JSON):
    if 'statement' in JSON:
      self.assertStatement(JSON['statement'])
    elif 'query' in JSON:
      if 'concept' in JSON['query']:
        self.queryConcept(JSON['query']['concept'])
      if 'component' in JSON['query']:
        self.queryComponent(JSON['query']['component'])
  
          
    
  
    