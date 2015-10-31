#!/usr/bin/env python
"""
This is sample code for Homework Assignment #4 in Fall 2015 91.542/91.442
Natural Language Processing course, @ Computer Science Department @
UMass Lowell.
"""
from __future__ import division
import os, sys
import nltk
import nltk.metrics.confusionmatrix as cm

__author__ = "arum@cs.uml.edu"


#_DEBUG = 2
#_DEBUG = 1
_DEBUG = 0


CORPUS_DIR="./imdb_corpus"
#os.chdir(CORPUS_DIR)


class Instance(object):
    """ Stores all information available about a given instance """
    def __init__(self, title, text, label, all_labels):
        self.title = title
        self.text = text
        self.label = label
        self.all_labels = all_labels

    def __repr__(self):
        return "%s | %s | %s" % (self.title, self.label, self.all_labels)

categories = ['Action', 'Adventure', 'Comedy', 'Drama', 'Fantasy',\
              'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'Western']


def read_corpus(label, label_dir, text_dir):
    """ Use example:

        read_corpus('Drama', 'labels/all', 'records')
        read_corpus('Drama', 'labels/training', 'records')
        read_corpus('Drama', 'labels/test', 'records')
    """
    if _DEBUG == 2:
        global positive_titles, negative_titles

    if not label in categories:
        raise Exception("read_corpus(): Illegal genre category: %s\n" % label +\
                        "Legal categories are: %s" % categories)

    positive_fname = "positive_%s.txt" % label
    negative_fname = "negative_%s.txt" % label

    try:
        positive_f = open(os.path.join(CORPUS_DIR,label_dir,positive_fname))
        negative_f = open(os.path.join(CORPUS_DIR,label_dir,negative_fname))
    except IOError, e:
        sys.stderr.write("read_corpus(): %s\n" % e)

    # create a dictionary of positive titles, with all labels for each title
    positive_titles = {}
    for line in positive_f:
        segs = [x.strip() for x in line.split('|')]
        title, labels = segs[0], segs[1:]
        positive_titles[title] = labels

    # create a dictionary of negative titles, with all labels for each title
    negative_titles = {}
    for line in negative_f:
        segs = [x.strip() for x in line.split('|')]
        title, labels = segs[0], segs[1:]
        negative_titles[title] = labels

    # create a set of positive and negative instances
    try:
        data = []
        for fname in os.listdir(os.path.join(CORPUS_DIR,text_dir)):
            full_fname = os.path.join(CORPUS_DIR,text_dir,fname)

            title = fname[:-4]       # cut away .txt extension

            all_labels = []
            if title in positive_titles:
                all_labels = positive_titles[title]
                text = open(full_fname).read()
                clabel = label
            elif title in negative_titles:
                all_labels = negative_titles[title]
                text = open(full_fname).read()
                clabel = "Not_%s" % label
            else:
                continue

            #print title, all_labels, clabel
            instance = Instance(title, text, clabel, all_labels)

            data.append(instance)

    except IOError, e:
        sys.stderr.write("read_corpus(): %s\n" % e)

    return data



def get_data_from_dir_list(dir_list):
    language_data={}
    for dirname in dir_list:
        language_data[dirname]=[]
        file_list=os.listdir(dirname)
        for filename in file_list:
            pathname=os.path.join(dirname,filename)
            language_data[dirname].append(open(pathname).read())
    return language_data


def extract_features(instance):
    """
    Extracts features from an instance.

    Args:
       instance: an Instance object
    Returns:
       {'feature_name' : feature_value} - feature hashtable
    """
    text = instance.text
    feature_set={}
    feature_set["firstword"]=text.split()[0]
    feature_set["firstletter"]=text[0]
    feature_set["lastword"]=text.split()[-1]
    feature_set["lastletter"]=text[-1]
    return feature_set


def make_training_data(data):
    """
    Args:
       data: list of instances
    Returns:
       [(feature_set, label), ...]
    """
    training_data=[]
    for instance in data:
        feature_set = extract_features(instance)
        label = instance.label
        training_data.append((feature_set,label))
    return training_data

def make_classifier(training_data):
    return nltk.classify.naivebayes.NaiveBayesClassifier.train(training_data)




def split_data(data, category, dev_frac=.3):
    # split the data into training and dev-test portions
    positives = [x for x in data if x.label == category]
    negatives = [x for x in data if x.label == 'Not_%s' % category]

    random.shuffle(positives)
    random.shuffle(negatives)

    dev_size = int(len(positives) * dev_frac)

    dev_set = positives[:dev_size] + negatives[:dev_size]
    training_set = positives[dev_size:] + negatives[dev_size:]

    return training_set, dev_set



if __name__ == '__main__':
    import argparse
    import random
    parser = argparse.ArgumentParser(description='Classify movie categories.')
    parser.add_argument('category', action='store', type=str,
                        help="One of 10 Genre Categories: %s" % categories)

    #args = parser.parse_args()
    args = parser.parse_args(['Drama'])
    category = args.category

    if not category in categories:
        sys.stderr.write("Illegal genre category: %s\n" % category)
        parser.print_help()
        sys.exit()


    # load up the training and test data
    training_data = read_corpus(category, 'labels/training', 'records')
    test_data = read_corpus(category, 'labels/test', 'records')

    # split training data into train and dev sets
    training_set, dev_set = split_data(training_data, category, .3)

    # do it
    train_d = make_training_data(training_set)
    classifier = make_classifier(train_d)

    dev_d = make_training_data(dev_set)
    for e in dev_d:
 	print classifier.classify(e[0]), e[1]
