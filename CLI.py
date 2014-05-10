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
  input = raw_input('> ')
  if re.match(".*([0-9]+)", input):
    bottlenose.setContext(int(re.match(".*([0-9]+)", input).group(1))-1)
  return

def inspectConcept(object):
  with indent(2):
    if object.hashcode:
      puts(colored.cyan(object.name) + ' (' + object.hashcode + ')')
  with indent(4):
    if object.synonyms:
      puts(colored.cyan(object.name) + ' is also known as: ' + ', '.join(object.synonyms))
    if object.parents:
      puts(colored.cyan(object.name) + ' is a ' + ', '.join(object.parents))
    if object.states:
      states = list()
      print object.states
      for stateTuple in object.states:
        states.append(stateTuple[0])
      puts(colored.cyan(object.name) + ' is ' + ', '.join(states))
    for componentTuple in object.components:
      puts(colored.cyan(object.name) + ' (has ' + componentTuple[0] + ') --> ' + componentTuple[1] + " [" + str(componentTuple[2]) + "]")
    for componentOfTuple in object.componentOf:
      puts(componentOfTuple[1] + ' (has ' + componentOfTuple[0] + ') --> ' + colored.cyan(object.name))
    for actionTuple in object.actions:
      puts(colored.cyan(object.name) + ' (' + actionTuple[0] + ') --> ' + str(actionTuple[1]))
    for actedOnByTuple in object.actedOnBy:
      puts(actedOnByTuple[1] + ' (' + actedOnByTuple[0] + ') --> ' + colored.cyan(object.name))
          
def main():
  bottlenose = Bottlenose()
  while True:
    input = raw_input('> ')
    if input == ':exit' or input == ':x': 
      sys.exit()
    elif input == ':context' or input == ':c':
      switchContext(bottlenose)
    elif input.strip() == '':
      continue
    else:
      try:
        response = bottlenose.tell(input)
        if isinstance(response, list):
          if not response:
            with indent(2):
              puts(colored.red('No matching concepts found.\n'))
          else:
            for object in response:
              puts()
              inspectConcept(object)
            puts()
      except Exception as error:
        if error.args:
          with indent(2):
            puts(colored.red(str(error.args[0])))
        else:
          with indent(2):
            puts(colored.red('Unknown command or incoherent scripting.\n'))
        traceback.print_exc()
if __name__ == '__main__':
  main()