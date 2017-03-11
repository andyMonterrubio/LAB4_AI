import sys
import copy
import fileinput

#main
input = fileinput.input()
aux = 0
bayesNet = []
Queries = []
Probabilities = []
states = []
states2 = []

#Get Nodes, Probabilities and Queries from the file
for line in input:
    #Get Nodes
    if aux == 1:
        states2 = line.rstrip('\n')
        states2 = states2.split(", ")
        aux = 0

    if aux == 2:
        if line != '\n':
            probability = line.rstrip('\n')
            Probabilities.append(probability)
        else:
            aux = 0

    if aux == 3:
        if line != '\n':
            query = line.rstrip('\n')
            Queries.append(query)
        else:
            aux = 0

    if line == "[Nodes]\n":
        aux = 1

    if line == "[Probabilities]\n":
        aux = 2

    if line == "[Queries]\n":
        aux = 3