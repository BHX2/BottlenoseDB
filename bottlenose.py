#!usr/bin/python2.7 -tt

import sys
sys.dont_write_bytecode = True
# Keeps directory clean by not compiling local files to bytecode

from concepts import Concept
from contexts import Context
from translator import grammar, Translator
from interpreter import Interpreter

def main():
  context = Context()
  translator = Translator()
  interpreter = Interpreter(context)
  while True:
    cogscript = raw_input("> ")
    if cogscript == "exit": sys.exit()
    JSON = translator.visit(grammar.parse(cogscript))
    interpreter.interpret(JSON)
  
if __name__ == '__main__':
  main()