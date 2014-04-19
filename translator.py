import re
import copy
from parsimonious.grammar import Grammar
from parsimonious.grammar import NodeVisitor

grammar = Grammar("""
  input                 = belief / statement
  belief                = law / evidence / rule
  law                   = dependent_clause (">>>" dependent_clause)+
  evidence              = clause (evidence_operator dependent_clause)+
  evidence_operator     = supports / opposes
  supports              = ">>+"
  opposes               = ">>-"
  dependent_clause      = clause / arithmetic_operation
  arithmetic_operation  = (component / concept) ("+" / "-") quantity
  rule                  = clause (">>" clause)+
  clause                = (shift_clause / comparison_clause / compound_clause / simple_clause) " "*
  shift_clause          = increment / decrement
  increment             = (component / concept) "++"
  decrement             = (component / concept) "--"
  comparison_clause     = (component / concept) !">>" (comparison_operator) " "* (quantity / component / concept) 
  comparison_operator   = "==" / "!=" / ">=" / "<=" / ">" / "<"
  compound_clause       = simple_clause logic_unit+
  logic_unit            = logic_operator simple_clause
  logic_operator        = "&" / "|" / "," 
  simple_clause         = statement probability? " "*
  probability           = "[" number "]"
  statement             = arithmetic_operation / taxonomy_assertion / synonym_assertion / state / action / component_assertion / component / concept
  taxonomy_assertion    = concept (type_includes / is_a) concept_or_list
  type_includes         = "/="
  is_a                  = "=/"
  synonym_assertion     = concept "=" concept_or_list
  state                 = (action / component_assertion / component / concept) "#" (quantity / qualifier)
  qualifier             = ~"!?[A-Z ]*"i
  quantity              = number units?
  units                 = ~"[A-Z ]*"i
  action                = (component / concept) "." verb "(" concepts_or_component? ")" " "*
  concepts_or_component = component / concept_or_list
  verb                  = ~"[A-Z 0-9]*s[A-Z 0-9]*"i
  component_assertion   = component "=" concept_or_list
  component             = concept ("." concept !"(")+
  number                = ~"[0-9]*\.?[0-9]+"
  concept_or_list       = concept_list / concept
  concept_list          = concept ("," concept)+
  concept               = ~"!?[A-Z 0-9]*"i
""")

class Translator(NodeVisitor):
  def visit_compound_clause(self, node, (simple_clause, logic_units)):
    clauses = [simple_clause['clause']]
    
    index = 0
    string_map = str(index)
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
    print response
    return response
        
  def visit_logic_unit(self, node, (operator, clause)):
    return [operator['operator'], clause['clause']]
  
  def visit_logic_operator(self, node, operator):
    if (node.text == "&"):
      return {'operator' : 'AND'}
    elif (node.text == "|"):
      return {'operator' : 'XOR'}
    elif (node.text == ","):
      return {'operator' : 'OR'}
    
  def visit_simple_clause(self, node, (statement, probability, _)):
    if probability:
      return {'clause': {'statement': statement['statement'], 'probability': probability['probability']}}
    else:
      return {'clause': {'statement': statement['statement']}}
  
  def visit_probability(self, node, (_1, number, _2)):
    return {'probability': number}

  def visit_taxonomy_assertion(self, node, (concept, operator, concept_or_list)):
    if "is_a" in operator.keys():
      return {'taxonomy_assertion':{'parent': concept_or_list, 'child': concept}}
    elif "type_includes" in operator.keys():
      return {'taxonomy_assertion':{'parent': concept, 'child': concept_or_list}}
  
  def visit_synonym_assertion(self, node, (concept, _, concept_or_list)):
    synonyms = [concept['concept']]
    if isinstance(concept_or_list, list): 
      for element in concept_or_list: synonyms.append(element['concept'])
    else:
      synonyms.append(concept_or_list['concept'])
    return {'synonym_assertion': {'concepts': synonyms}}
  
  def visit_state(self, node, (subject, _, description)):
    return {'state': {'subject': subject, 'description': description}}
  
  def visit_quantity(self, node, (number, units)):
    if units:
      return {'quantity': number, 'units': units['units']}
    else:
      return {'quantity': number, 'units': None}   
    
  def visit_action(self, node, (actor, _1, verb, _2, target, _3, _4)):
    return {'action': {'actor': actor, 'act': verb, 'target': target}}
  
  def visit_concepts_or_component(self, node, (concepts_or_component)):
    return concepts_or_component
  
  def visit_component_assertion(self, node, (target, _, assignment )):
    return {'component_assertion': {'target': target, 'assignment': assignment}}
    
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

tree = grammar.parse('')
i = Translator()
i.visit(tree)
    