#!/usr/bin/python
# -*- coding: utf-8 -*-
import fileinput


# define the structure
class Node(object):
    def __init__(self):
        self.name = None  # actual value (Node name)
        self.ancestors = None
        self.probabilities = None  # probabilities given from the input file


# create all nodes
def createNodes(nodes):
    for name in nodes:
        # create node
        node = Node()
        node.name = name
        node.ancestors = []
        node.probabilities = {}

        # add node to the bayes Net
        bayesNet[name] = node


# return False, True value of the sign given
def getSign(p):
    sign = p[0]
    if sign == "+":
        sign = True
    else:
        sign = False
    return sign


# for each probability given, add ancestors and probabilities to the node
def createProbabilities(probabilities):
    for prob in probabilities:
        prob = prob.replace(" ", "")

        # if there is evidence
        if prob.find('|') != -1:
            getGiven = prob.find('|')
            variable = prob[1:getGiven]
            if variable not in states:
                states.append(variable)
        else:
            getEqual = prob.find('=') + 1
            variable = prob[1:getEqual-1]
            if variable not in states:
                states.append(variable)

        node = bayesNet[variable]

        if prob.find('|') != -1:
            # Get the value
            getEqual = prob.find('=') + 1
            value = prob[getEqual:]
            # get ancestors
            ancestors = []

            if prob.find(',') != -1:
                conditions = prob[getGiven+1: getEqual-1].split(',')

                signs = []
                for condition in conditions:
                    sign = getSign(condition)
                    signs.append(sign)
                    ancestor = condition[1:]
                    ancestors.append(ancestor)

                node.probabilities.update({tuple(signs): float(value)})
                node.ancestors = ancestors
            else:
                # get value of sign
                sign = getSign(prob[getGiven+1:])

                # Get value of prob
                getEqual = prob.find('=') + 1
                value = float(prob[getEqual:])

                ancestors.append(prob[getGiven+2: getEqual-1])
                node.ancestors = ancestors  # add ancestors to the node

                node.probabilities.update({(sign,): value})  # add probabilities

        else:
            # get value of sign
            sign = getSign(prob)

            # Get the value
            getEqual = prob.find('=') + 1
            value = float(prob[getEqual:])
            node.ancestors = []
            node.probabilities = {(sign,): value}


# returns the probability of node with nodeName being isTrue
def getProbability(nodeName, isTrue, events, bayesNet):
    ancestors = bayesNet[nodeName].ancestors

    if len(ancestors) == 0:
        probability = bayesNet[nodeName].probabilities[(True,)]
    else:
        permutation = []
        for ancestor in ancestors:
            permutation.append(events[ancestor])
        probability = bayesNet[nodeName].probabilities[tuple(permutation)]

    if isTrue:
        return probability
    else:
        return 1.0 - probability


# calculates total probability by enumeration
def enumerate(states, bayesNet, query, isTrue, events):
    totalProb = {}
    auxevents = events

    # enumerate for positive
    auxevents[query] = True
    totalProb[True] = enumerateAll(states, auxevents, bayesNet)

    # enumerate for negative
    auxevents[query] = False
    totalProb[False] = enumerateAll(states, auxevents, bayesNet)

    # normalize the probabilities
    toalSum = totalProb[True] + totalProb[False]
    totalProb[True] /= toalSum
    totalProb[False] /= toalSum

    return totalProb[isTrue]


def enumerateAll(states, events, bayesNet):
    if len(states) == 0:
        return 1.0
    currentState = states[0]
    if currentState in events:
        # if the state is not hidden
        val = getProbability(currentState, events[currentState], events, bayesNet)
        val *= enumerateAll(states[1:], events, bayesNet)
        return val
    else:
        # if the state is hidden and not in events, eliminate summation variables
        total = 0
        events[currentState] = True
        total += getProbability(currentState, True, events, bayesNet) * enumerateAll(states[1:], events, bayesNet)
        events[currentState] = False
        total += getProbability(currentState, False, events, bayesNet) * enumerateAll(states[1:], events, bayesNet)
        del events[currentState]
        return total


def getSign(p):
    sign = p[0]
    if sign == "+":
        sign = True
    else:
        sign = False
    return sign


if __name__ == "__main__":
    aux = 0
    bayesNet = {}
    nodes = []
    Queries = []
    Probabilities = []
    states = []  # all variables

    # Get Nodes, Probabilities and Queries from the file
    for line in fileinput.input():
        # Get Nodes
        if aux == 1:
            nodes = line.rstrip('\r\n')
            nodes = nodes.split(", ")
            aux = 0

        # Get Probabilities
        if aux == 2:
            probability = line.rstrip('\r\n')
            if len(probability) > 0:
                Probabilities.append(probability)
            else:
                aux = 0

        # Get Queries
        if aux == 3:
            query = line.rstrip('\r\n')
            if len(query) > 0:
                Queries.append(query)
            else:
                aux = 0

        if line.startswith("[Nodes]"):
            aux = 1

        if line.startswith("[Probabilities]"):
            aux = 2

        if line.startswith("[Queries]"):
            aux = 3

        # print 'nodes', nodes;
        # print 'Queries', Queries;
        # print 'Probabilities', Probabilities;

    # create nodes
    createNodes(nodes)

    # for each probability, add ancestors and probabilities to the node
    createProbabilities(Probabilities)

    # for each Query, get each state and sign
    for query in Queries:
        query = query.replace(" ", "")

        queryAssign = []
        evidence = []
        events = {}

        # if there is evidence
        if query.find('|') != -1:
            getGiven = query.find('|')
            assigment = query[:getGiven]
            ev = query[getGiven+1:]

            # more than one query
            if assigment.find(',') != -1:
                queryAssign = assigment.split(',')
                evidence = ev.split(',')

                # create dictionary of events
                signs = []
                for e in evidence:
                    sign = getSign(e)
                    value = e[1:]
                    events.update({value: sign})

                # print 'queryAssign', queryAssign
                # print 'events', events

                # call the enumerate function to figure out a probability.
                count = 0
                result = 1
                for i in range(0, len(queryAssign)):
                    if count == 0:
                        isTrue = getSign(queryAssign[i])
                        variable = queryAssign[i][1:]
                        result = enumerate(states, bayesNet, variable, isTrue, events)
                        count += 1
                    else:
                        sign = getSign(queryAssign[i-1])
                        value = queryAssign[i-1][1:]
                        events.update({value: sign})
                        isTrue = getSign(queryAssign[i])
                        variable = queryAssign[i][1:]
                        result *= enumerate(states, bayesNet, variable, isTrue, events)
                        count += 1
                print(('%.7f' % result).rstrip('0'))

            else:
                # only one query
                evidence = ev.split(',')

                isTrue = getSign(assigment)
                variable = assigment[1:]

                # create dictionary of events
                signs = []
                for e in evidence:
                    sign = getSign(e)
                    value = e[1:]
                    events.update({value: sign})

                # print 'queryAssign', queryAssign
                # print 'events', events
                # call the enumerate function to figure out a probability.
                result = enumerate(states, bayesNet, variable, isTrue, events)
                print(('%.7f' % result).rstrip('0'))

        else:
            # there are no events
            isTrue = getSign(query)
            variable = query[1:]
            # print isTrue
            # print variable

            # call the enumerate function to figure out a probability.
            result = enumerate(states, bayesNet, variable, isTrue, {})
            print(('%.7f' % result).rstrip('0'))
