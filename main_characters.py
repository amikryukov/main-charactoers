# -*- coding: utf_8 -*-

import sys
import epub
import html2text
from nltk import *
from nltk.tokenize import *

def define_path():
  try:
    return sys.argv[1]
  except:
    print 'Pass file path to process'
    exit() 


def open_book(path):
  try:
    return epub.open_epub(path)
  except:
    print 'Can`t open', path

def traverse_tree(t):
    named_entities = []
    if hasattr(t, 'node') and t.node:
        # если вершина помечена строкой NE - значит это именованная сущность
        if t.node == 'NE':
            # собираем все листья в одну строку 
            if t.leaves()[0][0][:1] > 'A' and t.leaves()[0][0][:1] < 'Z' :   
                named_entities.append(' '.join([child[0] for child in t.leaves()]))
        else:
            for child in t:
                named_entities.extend(traverse_tree(child))
    return named_entities

book = open_book(define_path())

main_dict = {}

#for testing
k = 0

index = 0
# - - -
for item_id, liner in book.opf.spine.itemrefs:
# for testing
  index = index + 1
  k = k + 1
  if k < 7: continue
#  if k > 7: break
# - - -
  item = book.get_item(item_id)
  if liner:
    text = html2text.html2text(book.read_item(item))
    # split for sentences
    sentences = sent_tokenize(text)
    # split each sentence in to tokens
    words_sentences = [word_tokenize(sentence) for sentence in sentences]
    # part of speach tagging for each sentence
    tagged_sentences = [pos_tag(sentence) for sentence in words_sentences]
    
    # magic goes here - tree creation
    ne_sentences = batch_ne_chunk(tagged_sentences, binary=True)
    #ne_sentences[3].draw()
    
    named_entities = []

    for tree in ne_sentences:
      named_entities.extend(traverse_tree(tree))
    for name in named_entities:
      if main_dict.has_key(name):
        if not main_dict[name].has_key(index):
          main_dict[name][index] = 0
        main_dict[name][index] = main_dict[name][index] + 1
      else: 
        main_dict[name] = {index: 1}


def count_dict_values(dict):
  total_count=0
  chapters_count = 0;
  for chapter in dict:
    total_count = total_count + dict[chapter]
    chapters_count = chapters_count + 1
  return (chapters_count, total_count)


new_dict = {}
for name in main_dict : 
  new_dict[name] =  count_dict_values(main_dict[name])
 
nn_dict = sorted(new_dict, key=new_dict.get, reverse=True)

temp = 0
for key in nn_dict:
  var = str(key) + '\n'
  for chapter in main_dict[key]:
    var = var + '(' + str(chapter) + '\t' +  str(main_dict[key][chapter]) + ') '
  print var + '---------'
  temp = temp + 1
  if temp > 10: break


print 'This is the End'
