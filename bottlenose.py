#!usr/bin/python2.7 -tt

import sys
sys.dont_write_bytecode = True
# Keeps directory clean by not compiling local files to bytecode

from concepts import Concept
from contexts import Context
from translator import grammar, Translator
from interpreter import Interpreter

class Bottlenose:
  def __init__(self, bootstrapVocabulary=False):
    Concept(bootstrapVocabulary)
    self._universalContext = Context(universal=True)
    self._contexts = [self._universalContext, Context()]
    self._context = self._contexts[1]
    self._translator = Translator()
    self._interpreter = Interpreter(self._context)
    
  def tell(self, input):
    JSON = self._translator.visit(grammar.parse(input))
    results = self._interpreter.interpret(JSON)
    self._context.ponderRecentMentions()
    if isinstance(results, set) or isinstance(results, list):
      return (list(results), self._context)
    elif not results:
      return (None, self._context)
    else:
      return ([results], self._context)
  
  def context(self):
    return self._context
    
  def listContexts(self):
    return self._contexts
    
  def setContext(self, index):
    if index >= 0 and index < len(self._contexts):
      self._context = self._contexts[index]
      self._interpreter.setContext(self._contexts[index])