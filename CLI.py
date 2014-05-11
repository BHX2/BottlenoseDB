#!usr/bin/python2.7 -tt

import sys
import traceback
import re
from clint.textui import puts, colored, indent, columns

sys.dont_write_bytecode = True
# Keeps directory clean by not compiling local files to bytecode

from bottlenose import Bottlenose
import utilities

def green(text):
  return colored.green(text, bold=True)

def teal(text):
  return colored.cyan(text, bold=False)
  
def magenta(text):
  return colored.magenta(text, bold=False)
  
def red(text):
  return colored.red(text, bold=True)
  
def switchContext(bottlenose):
  currentContext = bottlenose.context()
  i = 1
  puts()
  for context in bottlenose.listContexts():
    if context is currentContext:
      with indent(2):
        puts(teal(str(i) + '. ' + context.name))
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
      puts(green(object.name) + ' (' + object.hashcode + ')')
  with indent(4):
    if object.synonyms:
      puts(green(object.name) + ' is also known as: ' + ', '.join(object.synonyms))
    if object.parents:
      puts(green(object.name) + ' is a ' + ', '.join(object.parents))
    for stateTuple in object.states:
      if (stateTuple[1] == 100):
        puts(green(object.name) + ' is ' + stateTuple[0])
      else:
        puts(green(object.name) + ' is ' + stateTuple[0] + magenta(" [" + str(stateTuple[1]) + "]"))
    for componentTuple in object.components:
      if (componentTuple[2] == 100):
        puts(green(object.name) + ' (has ' + componentTuple[0] + ') --> ' + componentTuple[1])
      else:
        puts(green(object.name) + ' (has ' + componentTuple[0] + ') --> ' + componentTuple[1] + magenta(" [" + str(componentTuple[2]) + "]"))
    for componentOfTuple in object.componentOf:
      if (componentOfTuple[2] == 100):
        puts(componentOfTuple[1] + ' (has ' + componentOfTuple[0] + ') --> ' + green(object.name))
      else:
        puts(componentOfTuple[1] + ' (has ' + componentOfTuple[0] + ') --> ' + green(object.name) + magenta(" [" + str(componentOfTuple[2]) + "]"))
    for actionTuple in object.actions:
      if (actionTuple[2] == 100):
        puts(green(object.name) + ' (' + actionTuple[0] + ') --> ' + str(actionTuple[1]))
      else:
        puts(green(object.name) + ' (' + actionTuple[0] + ') --> ' + str(actionTuple[1]) + magenta(" [" + str(actionTuple[2]) + "]"))
    for actedOnByTuple in object.actedOnBy:
      if (actedOnByTuple[2] == 100):
        puts(actedOnByTuple[1] + ' (' + actedOnByTuple[0] + ') --> ' + green(object.name))
      else:
        puts(actedOnByTuple[1] + ' (' + actedOnByTuple[0] + ') --> ' + green(object.name) + magenta(" [" + str(actedOnByTuple[2]) + "]"))
          
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
              puts(red('No matching concepts found.\n'))
          else:
            for object in response:
              puts()
              inspectConcept(object)
            puts()
      except Exception as error:
        if error.args:
          with indent(2):
            puts(red(str(error.args[0])))
        else:
          with indent(2):
            puts(red('Unknown command or incoherent scripting.\n'))
        traceback.print_exc()
if __name__ == '__main__':
  main()