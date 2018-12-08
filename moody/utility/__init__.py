'''
Created on 29 set 2018

@author: mar

Utility package

'''


def differences(l):
    diff = []
    c = 0

    while c < len(l) - 1:
        diff.append(abs(l[c + 1] - l[c]))
        c += 1

    return diff


def average(l):

    avg = sum(l) / len(l)

    return avg