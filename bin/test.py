#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os

import logging
import time
import cherrypy
from bbots.webapp import WebApp
from bbots.webdata import *




def test_bin_list():
    inputlist = [0]
    list = bin_list(inputlist,5)
    print str(inputlist),'->',str(list)
    assert(
        list[0]==[0] and
        list[1]==[0] and
        list[2]==[0] and
        list[3]==[0] and
        list[4]==[0])

    inputlist = [0,1]
    list = bin_list(inputlist, 5)
    print str(inputlist), '->', str(list)
    assert (
        list[0] == [0] and
        list[1] == [0] and
        list[2] == [0] and
        list[3] == [1] and
        list[4] == [1])


    inputlist = [0, 1, 2]
    list = bin_list(inputlist, 5)
    print str(inputlist), '->', str(list)
    assert (
        list[0] == [0] and
        list[1] == [0] and
        list[2] == [1] and
        list[3] == [1] and
        list[4] == [2])

    inputlist = [0, 1, 2, 3]
    list = bin_list(inputlist, 5)
    print str(inputlist), '->', str(list)
    assert (
        list[0] == [0] and
        list[1] == [0] and
        list[2] == [1] and
        list[3] == [2] and
        list[4] == [3])

    inputlist = [0, 1, 2, 3, 4]
    list = bin_list(inputlist, 5)
    print str(inputlist), '->', str(list)
    assert (
        list[0] == [0] and
        list[1] == [1] and
        list[2] == [2] and
        list[3] == [3] and
        list[4] == [4])

    inputlist = [0, 1, 2, 3, 4, 5]
    list = bin_list(inputlist, 5)
    print str(inputlist), '->', str(list)
    # assert (
    #     list[0] == [0] and
    #     list[1] == [1] and
    #     list[2] == [2] and
    #     list[3] == [3,4] and
    #     list[4] == [5])

    inputlist = [0, 1, 2, 3, 4, 5, 6]
    list = bin_list(inputlist, 5)
    print str(inputlist), '->', str(list)
    # assert (
    #     list[0] == [0] and
    #     list[1] == [1, 2] and
    #     list[2] == [3] and
    #     list[3] == [4] and
    #     list[4] == [5,6])

    inputlist = range(17)
    list = bin_list(inputlist, 5)
    print str(inputlist), '->', str(list)
    # assert (
    #     list[0] == [0] and
    #     list[1] == [1, 2] and
    #     list[2] == [3] and
    #     list[3] == [4] and
    #     list[4] == [5, 6])

    inputlist = range(32)
    list = bin_list(inputlist, 5)
    print str(inputlist), '->', str(list)


import cPickle
from datetime import datetime
import time

def test_serialize():
    d = datetime.now()
    f = 1.2
    import


def main():
    pass

if __name__ == '__main__':
    main()



