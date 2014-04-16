#!usr/bin/python2.7 -tt

import sys
sys.dont_write_bytecode = True
# Keeps directory clean by not compiling local files to bytecode
import grammar
import utilities
import synonyms
import taxonomy
import concepts

def main():
  print 'Hello World'
  
if __name__ == '__main__':
  main()