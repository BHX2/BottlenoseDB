#!usr/bin/python2.7 -tt

import sys
import traceback
import re
from clint.textui import puts, colored, indent

sys.dont_write_bytecode = True
# Keeps directory clean by not compiling local files to bytecode

from bottlenose import Bottlenose
import utilities

def switchContext(bottlenose):
  currentContext = bottlenose.context()
  i = 1
  puts()
  for context in bottlenose.listContexts():
    if context is currentContext:
      with indent(2):
        puts(colored.yellow(str(i) + '. ' + context.name))
    else:
      with indent(2):
        puts(str(i) + '. ' + context.name)
    i = i + 1
  puts('\nType a context number:')
  if bottlenose.context().isUniversal:
    input = raw_input(colored.cyan('> '))
  else:
    input = raw_input('> ')
  if re.match(".*([0-9]+)", input):
    bottlenose.setContext(int(re.match(".*([0-9]+)", input).group(1))-1)
  return

def inspectConcept(concept, context=None):
  parents = concept.parents()
  puts()
  if not context:
    with indent(2):
      puts(colored.green(concept.name))
  else:
    conceptHash = None
    for hash in context.conceptHashTable:
      if context.conceptHashTable[hash] is concept:
        conceptHash = hash
        break
    if conceptHash:
      if conceptHash in context.prototypes.values():
        with indent(2):
          puts(colored.cyan(concept.name + ' (prototype)'))
      else:
        with indent(2):
          puts(colored.yellow(concept.name) + ' (' + conceptHash + ')')
  if parents:
    with indent(4):
      puts(colored.green(concept.name) + ' is a ' + ', '.join(parents))
  synonyms = concept.synonyms().copy()
  if synonyms:
      if utilities.camelCase(concept.name) in synonyms: synonyms.remove(utilities.camelCase(concept.name))
      if len(synonyms):
        with indent(4):
          puts(colored.green(concept.name) + ' is also known as: ' + ', '.join(synonyms))
  if not context: return
  descriptors = context.stateGraph.successors(concept)
  temp = list()
  for descriptor in descriptors:
    temp.append(descriptor.name)
  descriptors = temp
  if descriptors:
    with indent(4):
      puts(colored.yellow(concept.name) + ' is ' + ', '.join(descriptors))
  for edge in context.componentGraph.out_edges(concept, data=True):
    with indent(4):
      puts(colored.yellow(edge[0].name) + ' (has ' + edge[2]['label'] + ') --> ' + edge[1].name)
  for edge in context.componentGraph.in_edges(concept, data=True):
    with indent(4):
      puts(edge[0].name + ' (has ' + edge[2]['label'] + ') --> ' + colored.yellow(edge[1].name))
  acts = set(context.actionGraph.neighbors(concept))
  for actor_act in context.actionGraph.out_edges(concept):
    for act_target in context.actionGraph.out_edges(actor_act[1]):
      with indent(4):
        puts(colored.yellow(actor_act[0].name) + ' (' + utilities.unCamelCase(act_target[0].name) + ') --> ' + act_target[1].name)
        acts.remove(act_target[0])
  for act in acts:
    with indent(4):
      puts(colored.yellow(concept.name) + ' (' + utilities.unCamelCase(act.name) + ') --> None')
  for act_target in context.actionGraph.in_edges(concept):
    for actor_act in context.actionGraph.in_edges(act_target[0]):
      with indent(4):
        puts(actor_act[0].name + ' (' + utilities.unCamelCase(act_target[0].name) + ') --> ' + colored.yellow(act_target[1].name))
          
def main():
  bottlenose = Bottlenose()
  while True:
    if bottlenose.context().isUniversal:
      input = raw_input(colored.cyan('> '))
    else:
      input = raw_input('> ')
    if input == ':exit' or input == ':x': 
      sys.exit()
    elif input == ':context' or input == ':c':
      switchContext(bottlenose)
    elif input == ':universal' or input == ':u':
      bottlenose.setContext(0)
    elif input.strip() == '':
      continue
    else:
      try:
        (response, context) = bottlenose.tell(input)
        if isinstance(response, list):
          if not response:
            with indent(2):
              puts(colored.red('No matching concepts found.'))
          else:
            for result in response:
              inspectConcept(result, context)
            puts()
      except Exception as error:
        if error.args:
          with indent(2):
            puts(colored.red(str(error.args[0])))
        else:
          with indent(2):
            puts(colored.red('Unknown command or incoherent Cogscript.'))
        traceback.print_exc()
if __name__ == '__main__':
  main()