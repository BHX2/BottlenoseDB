import re
import copy
from parsimonious.grammar import Grammar
from parsimonious.grammar import NodeVisitor

grammar = Grammar("""
  input                 = belief / taxonomy_assignment / synonym_assignment / statement
  taxonomy_assignment   = concept_or_component (type_includes / is_a) concept_or_list
  type_includes         = "/="
  is_a                  = "=/"
  synonym_assignment    = concept "~" concept_or_list
  query                 = "?" concept ("(" (state / action / direct_object / component_assignment / component / concept) ")")?
  belief                = law / rule
  law                   = clause ">>>" clause
  arithmetic_operation  = (component / concept) arithmetic_operator quantity
  arithmetic_operator   = "+" / "-"
  rule                  = clause ">>" clause
  clause                = (comparison_clause / compound_clause / simple_clause) " "*
  comparison_clause     = (component / concept) !">>" (comparison_operator) " "* (quantity / component / concept) 
  comparison_operator   = "==" / "!=" / ">=" / "<=" / ">" / "<"
  compound_clause       = simple_clause logic_unit+
  logic_unit            = logic_operator simple_clause
  logic_operator        = "&" / "|" / "," 
  simple_clause         = " "* "!"? statement probability? " "*
  probability           = "[" number "]"
  statement             = arithmetic_operation / state / action / component_addition / component_subtraction / component_assignment / component / concept
  state                 = (component / concept) "#" (quantity / quality)
  quality               = ~"\s*!?[A-Z]*\s*"i
  quantity              = number units?
  units                 = ~"\s*[A-Z]*\s*"i
  action                = (component / concept) "." verb "(" concepts_or_component? ")" " "*
  direct_object         = " "* verb "(" concept ")" " "*
  concept_or_component  = component / concept
  concepts_or_component = component / concept_or_list
  verb                  = ~"\s*[A-Z0-9]*s[A-Z0-9]*\s*"i
  component_assignment  = component "=" concept
  component_addition    = component "+=" concept_or_list
  component_subtraction = component "-=" concept_or_list
  component             = concept ("." concept !"(")+
  number                = ~"\s*[0-9]*\.?[0-9]+\s*"
  concept_or_list       = concept_list / concept
  concept_list          = concept ("," concept)+
  concept               = " "* (query / simple_concept) " "*
  simple_concept        = ~"\s*!?[A-Z0-9]*\*?\s*"i
""")

class Translator(NodeVisitor):
  def visit_input(self, node, input):
    return input[0]
  
  def visit_query(self, node, (_1, subject, clause_expression)):
    if not clause_expression:
      return {'query':{'subject': subject, 'clause':None}}
    else:
      return {'query':{'subject': subject, 'clause':clause_expression}}
  
  def visit_belief(self, node, (rule_or_law)):
    return {'belief': rule_or_law[0]}
  
  def visit_law(self, node, (first_clause, _, second_clause)):
    return {'law': {'independent_clause': first_clause, 'dependent_clause': second_clause}}

  def visit_arithmetic_operation(self, node, (concept_or_component, operator, quantity)):
    return {'arithmetic_operation': {'variable': concept_or_component, 'operator': operator, 'quantity': quantity}}
    
  def visit_arithmetic_operator(self, node, _):
    return node.text
    
  def visit_rule(self, node, (first_clause, _, second_clause)):
    return {'rule': {'independent_clause': first_clause, 'dependent_clause': second_clause}}
    
  def visit_clause(self, node, (clause, _2)):
    return clause
      
  def visit_comparison_clause(self, node, (component_or_concept, _1, operator, _, component_concept_or_quantity)):
    return {'comparison': {'variable': component_or_concept, 'sign': operator, 'measure': component_concept_or_quantity}}
  
  def visit_comparison_operator(self, node, _):
    return node.text
  
  def visit_compound_clause(self, node, (simple_clause, logic_units)):
    clauses = [simple_clause]
    
    index = 0
    string_map = str(index)
    
    for thing in logic_units:
      # Triggers if there is only one logic unit
      if thing == 'AND' or thing == 'OR' or thing == 'XOR':
        return {logic_units[0]: [simple_clause, logic_units[1]]}
    
    for (operator, clause) in logic_units:
      index = index + 1
      clauses.append(clause)
      string_map = string_map + operator + str(index)
    
    sub_expression_tree = []
    
    for (XOR_index, XOR_sub_expression) in enumerate(string_map.split('XOR')):
      sub_expression_tree.append(list())
      for (OR_index, OR_sub_expression) in enumerate(XOR_sub_expression.split('OR')):
        sub_expression_tree[XOR_index].append(list())
        for (AND_index, AND_sub_expression) in enumerate(OR_sub_expression.split('AND')):
          sub_expression_tree[XOR_index][OR_index].append(AND_sub_expression)
    
    response = dict()
    if len(sub_expression_tree) > 1:
      response['XOR'] = list()
      for (i, XOR_branch) in enumerate(sub_expression_tree):
        if len(XOR_branch) > 1:
          response['XOR'].append({'OR': list()})
          for (j, OR_branch) in enumerate(sub_expression_tree[i]):
            if len(OR_branch) > 1:
              response['XOR'][i]['OR'].append({'AND': list()})
              for (k, AND_branch) in enumerate(sub_expression_tree[i][j]):
                response['XOR'][i]['OR'][j]['AND'].append(clauses[int(sub_expression_tree[i][j][k])])
            else:
              response['XOR'][i]['OR'].append(clauses[int(sub_expression_tree[i][j][0])])
        else:
          if len(XOR_branch[0]) > 1:
            response['XOR'].append({'AND': list()})
            for (k, AND_branch) in enumerate(sub_expression_tree[i][0]):
              response['XOR'][i]['AND'].append(clauses[int(sub_expression_tree[i][0][k])])
          else:
            response['XOR'].append(clauses[int(sub_expression_tree[i][0][0])])
    else:
        if len(sub_expression_tree[0]) > 1:
          response['OR'] = list()
          for (j, OR_branch) in enumerate(sub_expression_tree[0]):
            if len(OR_branch) > 1:
              response['OR'].append({'AND': list()})
              for (k, AND_branch) in enumerate(sub_expression_tree[0][j]):
                response['OR'][j]['AND'].append(clauses[int(sub_expression_tree[0][j][k])])
            else:
              response['OR'].append(clauses[int(sub_expression_tree[0][j][0])])
        else:
          if len(sub_expression_tree[0][0]) > 1:
            response['AND'] = list()
            for (k, AND_branch) in enumerate(sub_expression_tree[0][0]):
              response['AND'].append(clauses[int(sub_expression_tree[0][0][k])])
          else: 
            response = sub_expression_tree[0][0][0]
    return response
        
  def visit_logic_unit(self, node, (operator, clause)):
    return [operator['operator'], clause]
  
  def visit_logic_operator(self, node, operator):
    if (node.text == "&"):
      return {'operator' : 'AND'}
    elif (node.text == "|"):
      return {'operator' : 'OR'}
    elif (node.text == ","):
      return {'operator' : 'OR'}
    
  def visit_simple_clause(self, node, (_1, negative, statement, probability, _2)):    
    response = {'statement': statement['statement']}
    if probability:
      response['probability'] = probability['probability']
    if negative == None:
      return response
    else:
      return {'NOT': [response]}
  
  def visit_probability(self, node, (_1, number, _2)):
    return {'probability': number}
  
  def visit_taxonomy_assignment(self, node, (concept_or_component, operator, concept_or_list)):
    if "is_a" in operator.keys():
      return {'statement': {'taxonomy_assignment':{'parent': concept_or_list, 'child': concept_or_component, 'type':'is_a'}}}
    elif "type_includes" in operator.keys():
      return {'statement': {'taxonomy_assignment':{'parent': concept_or_component, 'child': concept_or_list, 'type':'type_includes'}}}
  
  def visit_synonym_assignment(self, node, (concept, _, concept_or_list)):
    synonyms = [concept['concept']]
    if isinstance(concept_or_list, list): 
      for element in concept_or_list: 
        if not isinstance(element['concept'], dict):
          synonyms.append(element['concept'])
    elif not isinstance(concept_or_list['concept'], dict):
      synonyms.append(concept_or_list['concept'])
    return {'statement': {'synonym_assignment': {'concepts': synonyms}, 'subject': concept}}
  
  def visit_state(self, node, (subject, _, description)):
    return {'state': {'subject': subject, 'description': description}}
  
  def visit_quantity(self, node, (number, units)):
    if units:
      return {'quantity': number, 'units': units['units']}
    else:
      return {'quantity': number, 'units': None}   
  
  def visit_direct_object(self, node, (_1, verb, _2, target, _3, _4)):
    return {'action': {'actor': None, 'act': verb, 'target': target}}
    
  def visit_action(self, node, (actor, _1, verb, _2, target, _3, _4)):
    return {'action': {'actor': actor, 'act': verb, 'target': target}}
  
  def visit_concept_or_component(self, node, (concept_or_component)):
    return concept_or_component[0]
  
  def visit_concepts_or_component(self, node, (concepts_or_component)):
    return concepts_or_component

  def visit_component_assignment(self, node, (target, _, assignment )):
    return {'component_assignment': {'target': target, 'assignment': assignment}}
    
  def visit_component_addition(self, node, (target, _, addition)):
    return {'component_addition': {'target': target, 'addition': addition}}

  def visit_component_subtraction(self, node, (target, _, unassignment)):
    return {'component_subtraction': {'target': target, 'unassignment': unassignment}}    
  
  def visit_component(self, node, (stem, branch_expressions)):
    tree = {'stem': stem}
    for branch_expression in node.children[1].children:
      tree['branch'] = branch_expression.children[1].text.strip()
      tree = {'stem': tree}
    return {'component': tree['stem']}
    
  def visit_number(self, node, _):
    return float(node.text.strip())
  
  def visit_concept_or_list(self, node, visited_children):
    if len(visited_children) == 1:
      return visited_children[0]
    else:
      return visited_children
  
  def visit_concept_list(self, node, (first_concept, other_concepts)):
    concepts = [first_concept]
    if isinstance(other_concepts, list):
      concepts.extend(other_concepts)
    else:
      concepts.append(other_concepts)
    return concepts
    
  def visit_concept(self, node, (_1, query_or_concept, _2)):
    if query_or_concept:
      if 'simple_concept' in query_or_concept:
        if query_or_concept['simple_concept']:
          return {'concept': query_or_concept['simple_concept']}
        else:
          return None
      else:
        return {'concept': query_or_concept}
    else:
      return None
  
  def generic_visit(self, node, visited_children):
    if not node.expr_name:
      if isinstance(visited_children, list):
        response = []
        if not len(visited_children):
          return None
        for child in visited_children:
          if child:
            response.append(child)
        while isinstance(response, list) and len(response) == 1:
          response = response[0]
        return response
      else:
        return visited_children
    expression = node.text.strip()
    if re.match('[().]', expression) or not expression: return None
    if not visited_children:
      #print {node.expr_name: node.text.strip()}
      return {node.expr_name: node.text.strip()}
    else:
      #print {node.expr_name: visited_children[0]}
      return {node.expr_name: visited_children[0]}