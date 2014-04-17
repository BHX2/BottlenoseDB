import re
from parsimonious.grammar import Grammar
from parsimonious.grammar import NodeVisitor

grammar = Grammar("""
  input                 = rule / statement
  rule                  = law / evidence / simple_rule
  law                   = dependent_clause (">>>" dependent_clause)+
  evidence              = clause (evidence_operator dependent_clause)+
  evidence_operator     = supports / opposes
  supports              = ">>+"
  opposes               = ">>-"
  dependent_clause      = clause / arithmetic_operation
  arithmetic_operation  = (component / concept) ("+" / "-") quantity
  simple_rule           = clause (">>" clause)+
  clause                = (shift_clause / comparison_clause / compound_clause / simple_clause) " "*
  shift_clause          = increment / decrement
  increment             = (component / concept) "++"
  decrement             = (component / concept) "--"
  comparison_clause     =  (component / concept) !">>" (comparison_operator) " "* (quantity / component / concept) 
  comparison_operator   = "==" / "!=" / ">=" / "<=" / ">" / "<"
  compound_clause       = simple_clause (logic_operator simple_clause)+
  logic_operator        = "&" / "|" / "," 
  simple_clause         = statement probability? " "*
  probability           = "[" number "]"
  statement             = arithmetic_operation / taxonomy_assertion / synonym_assertion / state / action / component_assertion / component / concept
  taxonomy_assertion    = concept ("/=" / "=/") concept_or_list
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

class Interpreter(NodeVisitor):
  def visit_synonym_assertion(self, node, (concept, _, concept_or_list)):
    synonyms = [concept['concept']]
    if isinstance(concept_or_list, list): 
      for element in concept_or_list: synonyms.append(element['concept'])
    else:
      synonyms.append(concept_or_list['concept'])
    print {'synonym_assertion': {'concepts': synonyms}}
    return {'synonym_assertion': {'concepts': synonyms}}
  
  def visit_action(self, node, (actor, _1, verb, _2, target, _3, _4)):
    print {'action': {'actor': actor, 'act': verb, 'target': target}}
    return {'action': {'actor': actor, 'act': verb, 'target': target}}
  
  def visit_concepts_or_component(self, node, visited_nodes):
    return visited_nodes[0]
  
  def visit_component_assertion(self, node, (target, _, assignment )):
    return {'component_assertion': {'target': target, 'assignment': assignment}}
    
  def visit_component(self, node, (stem, branch_expressions)):
    tree = {'stem': stem}
    for branch_expression in node.children[1].children:
      tree['branch'] = branch_expression.children[1].text.strip()
      tree = {'stem': tree}
    return {'component': tree['stem']}
    
  def visit_number(self, node, visited_children):
    return {'number': float(node)}
  
  def visit_concept_or_list(self, node, visited_children):
    if isinstance(visited_children, list):
      return visited_children[0]
    else:
      return visited_children
  
  def visit_concept_list(self, node, (firstConcept, other_concepts)):
    concepts = [firstConcept]
    for expression in node.children[1].children:
      concepts.append({'concept': expression.children[1].text.strip()})
    return concepts
    
  def generic_visit(self, node, visited_children):
    if not node.expr_name: 
      if len(visited_children) > 0:
        return visited_children[0]
      else:
        return visited_children
    expression = node.text.strip()
    if re.match('[().]', expression) or not expression: return None
    if not visited_children:
      print {node.expr_name: node.text.strip()}
      return {node.expr_name: node.text.strip()}
    else:
      print {node.expr_name: visited_children[0]}
      return {node.expr_name: visited_children[0]}

tree = grammar.parse('cat.meows(dog)')
i = Interpreter()
i.visit(tree)
    