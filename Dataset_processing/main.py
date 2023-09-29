# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import csv
import numpy as np

with open("./dataset.csv", 'r') as file
    csvreader = csv.reader(file)
    for row in csvreader:
        print(row)


# function to calculate the position of the car relative to absolute coordinate (0,0)
# p is position of the object
# v is velocity of the object
def car_position_calculation(v):
    Pc = [[0,0]]
    delt = 0.5 #delta t => timestamp
    new_p = []
    for i in range(len(v)):
        pxi = Pc[i][0] + v[i+1][0] * delt
        pyi = Pc[i][1] + v[i+1][1] * delt
        new_p = [pxi, pyi]
        Pc.append(new_p)
        new_p = []

    return Pc


def obj_position_calculation():