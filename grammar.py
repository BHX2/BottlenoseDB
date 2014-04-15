from parsimonious.grammar import Grammar

grammar = Grammar(
	"""
	input								= rule / statement
	rule 								= law / evidence / simple_rule
	law 								= dependent_clause (">>>" dependent_clause)+
	evidence 						= clause (evidence_operator dependent_clause)+
	evidence_operator		= supports / opposes
	supports						= ">>+"
	opposes							= ">>-"
	dependent_clause		= clause / arithmetic_operation
	arithmetic_operation= (component / concept) ("+" / "-") quantity
	simple_rule					= clause (">>" clause)+
	clause							= (shift_clause / comparison_clause / compound_clause / simple_clause) " "*
	shift_clause				= increment / decrement
	increment						= (component / concept) "++"
	decrement						= (component / concept) "--"
	comparison_clause		=	(component / concept) !">>" (comparison_operator) " "* (quantity / component / concept) 
	comparison_operator	= "==" / "!=" / ">=" / "<=" / ">" / "<"
	compound_clause			= simple_clause (logic_operator simple_clause)+
	logic_operator			= "&" / "|" / "," 
	simple_clause				= statement probability? " "*
	probability					= "[" number "]"
	statement						= arithmetic_operation / taxonomy_assertion / synonym_assertion / state / action / component_assertion / component / concept
	taxonomy_assertion	= concept ("/=" / "=/") concept_or_list
	synonym_assertion		= concept "=" concept_or_list
	state								= (action / component_assertion / component / concept) "#" (quantity / adjective)
	adjective						= ~"!?[A-Z ]*"i
	quantity						= number units?
	units								= ~"[A-Z ]*"i
	action							= (component / concept) "." verb "(" concept_or_list? ")" " "*
	verb								= ~"[A-Z 0-9]*s[A-Z 0-9]*"i
	component_assertion	= component "=" concept_or_list
	component						= (concept) ("." concept !"(")+
	number							= ~"[0-9]*\.?[0-9]+"
	concept_or_list			= concept_list / concept
	concept_list				= concept ("," concept)+
	concept							= ~"!?[A-Z 0-9]*"i
	""")

# if a cat flips then 99% of the time it lands rightside up, but 1% of the time it lands upside down
print grammar.parse('cat.flips() >> cat.lands(rightsideUp)[0.99] | cat.lands(upsideDown)[0.01]')
	
