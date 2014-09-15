import dice

import re
import nose
from sys import argv

""" Tests for Thomson Comer's additions to the dice.py plugin.
    Run with nosetests dice_test.py.  Can also be run interactively
    using python dice_test.py <rollstring>
"""

def get_from_parens(return_string):
  parens = re.compile("\((.+)\)")
  result = parens.search(return_string)
  return result.group(1)

def test_1d6():
  roll = dice.groups("1d6")
  result = get_from_parens(roll)
  assert int(result) in range(1,7)

def test_2_1d6():
  roll = dice.groups("2#1d6")
  result = get_from_parens(roll)
  x, y = result.split()
  assert int(x) in range(1,7)
  assert int(y) in range(1,7)

def test_a_1d6():
  roll = dice.groups("a#1d6")
  assert 'Bad' in roll

def test_1_aaa():
  roll = dice.groups("1#aaa")
  assert 'Bad' in roll

def test_garbage():
  roll = dice.groups("as@#5a%4!!7.>f")
  assert 'Bad' in roll

def main():
  print(dice.groups(roll))
  roll = argv[1]

