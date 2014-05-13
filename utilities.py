'''
BottlenoseDB / Utilities

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

import re
import string

def camelCase(text):
  isNegative = re.match('(^!)(.*)', text)
  if isNegative:
    text = isNegative.group(2)
  response = ''
  isQuantitative = True if re.search('(^[0-9.]+)(.*)', text) else False
  if isQuantitative:
    quantity = re.search('(^[0-9.]+)(.*)', text).group(1)
    text = re.search('(^[0-9.]+)(.*)', text).group(2)
    response += quantity
  words = text.replace("'s", "s").translate(string.maketrans(string.punctuation, ' '*len(string.punctuation))).split()
  if words: response += words.pop(0)
  if isNegative:
    response = '!' + response
  for word in words:
    response += word.capitalize()
  return response
  
def unCamelCase(text):
  isNegative = re.match('(^!)(.*)', text)
  if isNegative:
    text = isNegative.group(2)
  response = ''
  isQuantitative = True if re.search('(^[0-9.]+)(.*)', text) else False
  if isQuantitative:
    quantity = re.search('(^[0-9.]+)(.*)', text).group(1)
    text = re.search('(^[0-9.]+)(.*)', text).group(2)
    response += quantity
  text = re.sub("([A-Z0-9]*)([A-Z][a-z0-9]+)","\g<1> \g<2>", text)
  text = re.sub("([a-z0-9])([A-Z])","\g<1> \g<2>", text).strip()
  if text.istitle():
    return (response + text)
  else:
    words = text.split()
    if words: response += words.pop(0)
    for word in words:
      if word.isupper():
        response += (' ' + word)
      else:
        response += (' ' + word.lower())
    if isNegative:
      response = '!' + response
    return response
 
def sanitize(text):
  result = unCamelCase(camelCase(text))
  return result
  
def unicodeDecode(patternUnicodeStrings):
  patternStrings = map(str, patternUnicodeStrings)
  return map(camelCase, patternStrings)