'''
BottlenoseDB / Command-Line Interface (CLI)

Copyright 2014 Bharath Panchalamarri Bhushan

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''

#!usr/bin/python2.7 -tt

import os
import sys
import traceback
import re
from clint import arguments
from clint.textui import puts, colored, indent, columns

sys.dont_write_bytecode = True
# Keeps directory clean by not compiling local files to bytecode

from bottlenose import Bottlenose
import utilities

def green(text):
  return colored.green(text, bold=True)

def teal(text):
  return colored.cyan(text, bold=False)

def cyan(text):
  return colored.cyan(text, bold=True)
  
def magenta(text):
  return colored.magenta(text, bold=False)
  
def red(text):
  return colored.red(text, bold=True)

def grey(text):
  return colored.black(text, bold=True)
  
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

def help():
  col1 = 30
  col2 = 40
  puts('\nusage: bootstrap-cli.py [file or directory] [--bootstrap]')
  puts('\nlist of commands:')
  with indent(2):
    puts(columns([':exit', col1],['Exit Bottlenose', col2]))
    puts(columns([':load <file or directory>', col1],['Load a .bottle file or directory', col2]))
    puts(columns([':context', col1],['Switch between contexts', col2]))
    puts(columns([':help', col1],['Bring back this help info', col2]))
  puts('\nfor a guide to script syntax go to:')
  with indent(2):
    puts('https://github.com/BHX2/BottlenoseDB')
  puts()
        
def main():
  args = arguments.Args()
  if '--bootstrap' in args.flags or '-b' in args.flags:
    bottlenose = Bottlenose(bootstrapVocabulary=True)
  else:
    bottlenose = Bottlenose()
  if args.files:
    for file in args.files:
      if re.match('(.*)(\.bottle$)', file):
        bottlenose.loadFile(file, onlyBeliefs=True)
    for file in args.files:
      if re.match('(.*)(\.bottle$)', file):
        bottlenose.loadFile(file, onlyStatements=True)
  puts('\n' + cyan('BottlenoseDB (v 1.0) ') + grey('type \':help\' for a list of commands') + '\n')
  while True:
    input = raw_input('> ')
    if input == ':exit' or input == ':x': 
      sys.exit()
    elif input == ':context' or input == ':c':
      switchContext(bottlenose)
    elif input == ':help' or input == ':h':
      help()
    elif re.match('^:l', input):
      match = re.match('(^:l.*)\s(.*)', input)
      if not match:
        puts(red('usage: :load <directoryName>'))
      else:
        cargoIsFile = re.match('(.*)(\.bottle$)', match.group(2))
        if cargoIsFile:
          filePath = cargoIsFile.group(0)
          if os.path.isfile(filePath):
            bottlenose.loadFile(filePath, onlyBeliefs=True)
            bottlenose.loadFile(filePath, onlyStatements=True)
          else:
            puts(red('File not found'))
        else:
          dirPath = match.group(2)
          if os.path.isdir(dirPath):
            bottlenose.loadDirectory(dirPath)
          else:
            puts(red('Directory not found'))
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