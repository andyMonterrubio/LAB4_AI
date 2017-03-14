import sys
import copy
import fileinput

#REFERENCES: http://isites.harvard.edu/fs/docs/icb.topic540049.files/cs181_lec22_handout.pdf

#define the structure
class Node(object):
    def __init__(self):
        self.name = None #actual value (Node name)
        self.ancestors = None  
        self.probabilities = None  #probabilities given from the input file
        
#return False, True value of the sign given
def getValue(p):
    sign = p[0]
    if sign == "+":
        sign = True
    else:
        sign = False
    return sign
    
        
#main
input = fileinput.input()
aux = 0
bayesNet = []
nodes = []
Queries = []
Probabilities = []
states = [] #all variables

#Get Nodes, Probabilities and Queries from the file
for line in input:
    #Get Nodes
    if aux == 1:
        nodes = line.rstrip('\n')
        nodes = nodes.split(", ")
        aux = 0
    
    #Get probabilities
    if aux == 2:
        if line != '\n':
            probability = line.rstrip('\n')
            Probabilities.append(probability)
        else:
            aux = 0
    
    #Get Queries
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
    
# print 'nodes', nodes;
# print 'Queries', Queries;
# print 'Probabilities', Probabilities;

#create nodes
for state in nodes:
    node = Node();
    node.name = state
    node.ancestors = []
    node.probabilities = {}
    #add node to the bayes Net
    bayesNet.append(node)

#for each probability, add ancestors and probabilities to the node
for prob in Probabilities:
    prob = prob.replace(" ", "") #remove blank spaces
    
    #if there is evidence 
    if prob.find('|') != -1: 
        getGiven = prob.find('|')
        variable = prob[1:getGiven]
        if not variable in states:
            states.append(variable)
    else:
        getEqual = prob.find('=') + 1
        variable = prob[1:getEqual-1]
        if not variable in states:
            states.append(variable)

    #find the corresponded node
    for node in bayesNet:
        if node.name == variable:
            #get value, variable and ancestors
            if prob.find('|') != -1:
                #Get the value
                getEqual = prob.find('=') + 1
                value = prob[getEqual:]
                #get ancestors
                ancestors = []

                if prob.find(',') != -1:
                    conditions = prob[getGiven+1: getEqual-1].split(',')

                    signs = []
                    for condition in conditions:
                        sign = getValue(condition)
                        signs.append(sign)
                        ancestor = condition[1:]
                        ancestors.append(ancestor)

                    node.probabilities.update({tuple(signs):float(value)})
                    node.ancestors = ancestors
                else:
                    #get value of sign
                    sign = getValue(prob[getGiven+1:])

                    #Get value of prob
                    getEqual = prob.find('=') + 1
                    value = float(prob[getEqual:])

                    ancestors.append(prob[getGiven+2: getEqual-1])
                    node.ancestors = ancestors #add ancestors to the node

                    node.probabilities.update({(sign,):value}) #add probabilities

            else:
                #get value of sign
                sign = getValue(prob)

                #Get the value
                getEqual = prob.find('=') + 1
                value = float(prob[getEqual:])
                node.ancestors = []
                node.probabilities = {(sign,):value}
                
# for node in bayesNet:
#     print 'variable:', node.name
#     print 'ancestors:', node.ancestors
#     print 'probabilities:', node.probabilities

#for each Query, get each state and sign
for query in Queries:
    query = query.replace(" ", "") # delete blank spaces

    queryAssignment = []
    evidence = []
    events = {}
    
    #if there is evidence
    if query.find('|') != -1:
        getGiven = query.find('|')
        assigment = query[:getGiven]
        ev = query[getGiven+1:]
        
        #more than one query
        if assigment.find(',') != -1: 
            queryAssignment = assigment.split(',')
            evidence = ev.split(',')

            #create dictionary of events
            signs = []
            for e in evidence:
                sign = getValue(e)
                value = e[1:]
                events.update({value:sign})

        else: # only one query
            evidence = ev.split(',')

            typeRes = getValue(assigment)
            variable = assigment[1:]

            #create dictionary of events
            signs = []
            for e in evidence:
                sign = getValue(e)
                value = e[1:]
                events.update({value:sign})
                
            # print 'queryAssignment', queryAssignment
            # print 'events', events
                

    else:
        typeRes = getValue(query)
        variable = query[1:]
