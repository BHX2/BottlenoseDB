#!usr/bin/python2.7 -tt

import sys
from clint.textui import puts, colored, indent

sys.dont_write_bytecode = True
# Keeps directory clean by not compiling local files to bytecode

from bottlenose import Bottlenose
import utilities

def inspectConcept(concept, context=None):
  parents = concept.parents()
  if parents:
    puts(colored.green(concept.name) + ' is a ' + ', '.join(parents))
  else:
    puts(colored.green(concept.name))
  synonyms = concept.synonyms()
  if synonyms:
    if utilities.camelCase(concept.name) in synonyms: synonyms.remove(utilities.camelCase(concept.name))
    if len(synonyms):
      puts('also known as: ' + ', '.join(synonyms))
  if not context: return
  for edge in context.componentGraph.out_edges(concept, data=True):
    with indent(2):
      puts(colored.yellow(edge[0].name) + ' (has ' + edge[2]['label'] + ') --> ' + edge[1].name)
  for edge in context.componentGraph.in_edges(concept, data=True):
    with indent(2):
      puts(edge[0].name + ' (has ' + edge[2]['label'] + ') --> ' + colored.yellow(edge[1].name))
  acts = set(context.actionGraph.neighbors(concept))
  for actor_act in context.actionGraph.out_edges(concept):
    for act_target in context.actionGraph.out_edges(actor_act[1]):
      with indent(2):
        puts(colored.yellow(actor_act[0].name) + ' (' + utilities.unCamelCase(act_target[0].type) + ') --> ' + act_target[1].name)
        acts.remove(act_target[0])
  for act in acts:
    with indent(2):
      puts(colored.yellow(concept.name) + ' (' + utilities.unCamelCase(act.type) + ') --> None')
  for act_target in context.actionGraph.in_edges(concept):
    for actor_act in context.actionGraph.in_edges(act_target[0]):
      with indent(2):
        puts(actor_act[0].name + ' (' + utilities.unCamelCase(act_target[0].type) + ') --> ' + colored.yellow(act_target[1].name))
          
def main():
  bottlenose = Bottlenose()
  while True:
    input = raw_input("> ")
    if input == "exit": sys.exit()
    (response, context) = bottlenose.tell(input)
    if isinstance(response, list):
      if not response:
        print 'No matching concepts found.'
      else:
        for result in response:
          inspectConcept(result, context)
          
if __name__ == '__main__':
  main()