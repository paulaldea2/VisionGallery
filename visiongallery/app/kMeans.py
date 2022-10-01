import sys
import math
from random import randint
from traceback import print_tb

from attr import NOTHING
class Node:
    name = 0
    ident = 0
    r = 0
    g = 0
    b = 0
    cluster = -1
    def __init__(self, name, ident, r, g, b):
        self.name = name
        self.ident = ident
        self.r = r
        self.g = g
        self.b = b
        self.cluster = -1

class Cluster:
    r = 0
    g = 0
    b = 0
    children = []
    def __init__(self, ident, r, g, b):
        self.ident = ident
        self.r = r
        self.g = g
        self.b = b
        self.children = []

verbose = False
veryVerbose = False
MOVEMENT_CUTOFF = 5

def main():
    args = sys.argv
    verbose = False
    veryVerbose = False
    genClust = False
    fileIn = ''
    fileOut = ''
    clusterFile = ''
    numClusters = -1
    fail = False
    if (len(args) == 2 and str(args[1]) == 'help'):
            printHelpInfo()
            sys.exit(0)
    try:
        if (len(args) < 7):
            if (len(args) > 3):
                fileIn = str(args[1])
                fileOut = str(args[2])
                if (str(args[3]) == '-g'):
                    numClusters = int(args[4])
                    genClust = True
                    if (len(args) > 5 and str(args[5]) == '-v'):
                        verbose = True
                    elif (len(args) > 5 and str(args[5]) == '-vv'):
                        verbose = True
                        veryVerbose = True
                else:
                    clusterFile = str(args[3])
                    if (len(args) > 4 and str(args[4]) == '-v'):
                        verbose = True
                    elif (len(args) > 4 and str(args[4]) == '-vv'):
                        verbose = True
                        veryVerbose = True
                
            else:
                fail = True
        else:
            fail = True
    except:
        fail = True
    
    if (fail):
        printUsage()
        print('alternatively: \'kMeans.py help\' to display help info')
        sys.exit(1)


    # Read data from input file
    if (verbose):
        print('\nReading input data from ' + fileIn, '...')
    dataArray = readDataIn(fileIn)
    
    if (genClust):
        # Generate clusters
        if (verbose):
            print('Generating ' + str(numClusters) + ' clusters...')
        clusters = genClusters(numClusters)
    else:
        # Read in cluster data
        if (verbose):
            print('\nReading cluster data from ' + clusterFile, '...')
        clusterDataArray = readDataIn(clusterFile)
        numClusters = len(clusterDataArray)
        clusters = arrayToClusters(clusterDataArray)
    
    if (veryVerbose):
        for cluster in clusters:
             print('cluster ' + str(cluster.ident) + '\'s rgb values: ' + str(cluster.r) + " " + str(cluster.g) + " " + str(cluster.b))

             
    # Convert input data to nodes
    if (verbose):
        print('\nConverting ' + fileIn + ' to nodes array...') 
    nodes = genNodes(dataArray)

    
    # Begin K-Means
    iterate = True
    allowClusterMovement = True
    clusters = beginKMeans(nodes, clusters, iterate, allowClusterMovement)

    if (verbose):
        print('Writing data to ' + fileOut)
    writeToFile(fileOut, clusters)

def directKMeans(nodeData, clusterData, iterate, allowClusterMovement): # takes in list of photo data:[[photoID, r, g, b], [...]] and outputs: [[cluster1R, cluster1G, cluster1B, photo1ID, photo2ID, photo3ID], [cluster2R, cluster2G, cluster2B, photo4ID, photo5ID, photo6ID], ...]
    try:
        # Create Nodes
        nodes = genNodes(nodeData)

        # Create Clusters
        clusters = arrayToClusters(clusterData)

        # Begin K-Means
        #iterate = True
        #allowClusterMovement = True
        clusters = beginKMeans(nodes, clusters, iterate, allowClusterMovement)

        # Convert clusters object list to list of cluster data
        clusterList = clustersToArray(clusters)
    except Exception as e:
        print(e)
        traceback = e.__traceback__
        print_tb(traceback)
    return clusterList

def beginKMeans(nodes, clusters, iterate, allowClusterMovement):
    if (verbose):
        print('\n=====Beginning K-Means=====')
    #input('Press enter to continue')

    finishedMoving = False
    count = 1
    while (finishedMoving == False):
        if (verbose):
            print('Iteration ' + str(count))
        #input('Press enter to continue');
        
        # Begin stage 1
        temp = stage1(nodes, clusters)
        if len(temp) == 0:
            return []
        #nodes.clear()
        #clusters.clear()
        nodes = temp[0]
        clusters = temp[1]

       
        # Begin stage 2
        if (allowClusterMovement):
            temp2 = stage2(clusters)
            #clusters.clear()
            clusters = temp2[0]
            clusterMovement = []
            clusterMovement = temp2[1]

        #print('\n')
        finishedMoving = True
        if (allowClusterMovement):
            for i in range(len(clusterMovement)):
                if (veryVerbose):
                    print('cluster ' + str(i) + ' movement: ' + str(clusterMovement[i]))
                if (clusterMovement[i] != -1):
                    x = 1
                if (math.sqrt(clusterMovement[i]) > MOVEMENT_CUTOFF and iterate):
                    finishedMoving = False
        count+=1

    if (verbose):
        print('=====K-Means Finished!=====')
        print('\nTook ' + str(count-1) + ' iteration(s)')
    if (veryVerbose):
        print('\nClusters\' rgb values:')
        for i in range(len(clusters)):
            print(str(clusters[i].ident) + " " + str(clusters[i].r) + " " + str(clusters[i].g) + " " + str(clusters[i].b))
    return clusters

def stage1(nodes, clusters):
    for i in range(len(clusters)):
        clusters[i].children.clear()
    for i in range(len(nodes)):
        nodes[i].cluster = -1
    
    if len(clusters) == 0:
        return []

    index = 0
    minClusterNode = 0
    for i in range(len(nodes)): # for each node
        #print('i: ' + str(i))
        minimum = 200000 # max possible value for rgb dist is (255^2 + 255^2 + 255^2) = 195,075
        index = -1
        minClusterNode = -1

        for j in range(len(clusters)): # for each cluster
            # find r,g,b distances from node to cluster
            distance = dist(nodes[i], clusters[j])
            #print('cluster ' + str(clusters[j].ident) + '\'s rgb values in stage1: ' + str(clusters[j].r) + " " + str(clusters[j].g) + " " + str(clusters[j].b))
            if (distance < minimum): # if this distance is smaller than the current min, set min and index
                minimum = distance
                index = clusters[j].ident

        if (minClusterNode != index):
            minClusterNode = index
        nodes[i].cluster = clusters[index].ident # set node's cluster to closest cluster
        clusters[index].children.append(nodes[i]); # add node to closest cluster's children
    
    output = [nodes, clusters]
    return output

def stage2(clusters):
    distChange = []
    for i in range(len(clusters)): # for each cluster
        distance = 0
        if (len(clusters[i].children)>0):
            # find average r,g,b of children
            avgR = avg([n.r for n in clusters[i].children])
            avgG = avg([n.g for n in clusters[i].children])
            avgB = avg([n.b for n in clusters[i].children])
            distance = dist(Node(-1, -1, avgR, avgG, avgB), clusters[i])
            clusters[i].r = avgR
            clusters[i].g = avgG
            clusters[i].b = avgB
        distChange.append(distance)
    return [clusters, distChange]

def dist(node, cluster):
    dR = abs(cluster.r - node.r)
    dG = abs(cluster.g - node.g)
    dB = abs(cluster.b - node.b)
    distance = ((dR*dR) + (dG*dG) + (dB*dB))
    return distance
    
def avg(nums):
    return sum(nums) / len(nums)

def genClusters(num):
    clusters = []
    for i in range(num):
        r = randint(0, 255)
        g = randint(0, 255)
        b = randint(0, 255)
        clusters.append(Cluster(i,r,g,b))
    return clusters

def arrayToClusters(data):
    clusters = []
    for i in range(len(data)):
        rgb = data[i]
        r = int(rgb[0])
        g = int(rgb[1])
        b = int(rgb[2])
        curCluster = Cluster(i, r, g, b)
        clusters.append(curCluster)
    return clusters

def clustersToArray(clusters):
    clusterData = []
    for i in range(len(clusters)):
        line = []
        line.append(clusters[i].r)
        line.append(clusters[i].g)
        line.append(clusters[i].b)
	# this now appends the cluster's rgb and all of its children to the final cluster list
        for j in range(len(clusters[i].children)):
            line.append(clusters[i].children[j].name)
        clusterData.append(line)
    return clusterData

def genRandNodes(num):
    count = 0
    nodes = []
    for i in range(num):
        curNode = Node(int(count), int(count), int(randint(0,255)), int(randint(0,255)), int(randint(0,255)))
        nodes.append(curNode)
        count+=1
    return nodes

def genNodes(arr):
    count = 0
    nodes = []
    for x in arr:
        curNode = Node(int(x[0]), int(count), int(x[1]), int(x[2]), int(x[3]))
        nodes.append(curNode)
        count+=1
    return nodes
import os
def readDataIn(fileName):
    try:
        fileIn = NOTHING
        if os.path.exists(fileName):
            fileIn = open(fileName, 'r')
        else:
            open(fileName, 'w')
            fileIn = open(fileName, 'r')
        lines = fileIn.readlines()

        count = 0
        data = []
        for line in lines:
            data.append(line.split())
            count+=1
    except Exception as e:
        print(e)
        traceback = e.__traceback__
        print_tb(traceback)
        return []
    return data

def writeToFile(filename, clusters):
    file = open(filename, 'w')
    data = ''
    for i in range(len(clusters)):
        names = [n.name for n in clusters[i].children]
        data+=('Cluster ' + str(int(clusters[i].r)) + ' ' + str(int(clusters[i].g)) + ' ' + str(int(clusters[i].b)) + '\n')
        for j in range(len(names)):
            data+=(str(names[j]) + '\n')
    data = data[:data.rfind('\n')]
    file.write(data)
    file.close()

def printUsage():
    print('usage: \'kMeans.py <input file> <output file> <cluster file or -g [number of clusters to generate]> <optional -v for verbose or -vv for very verbose>\'')

def printHelpInfo():
    print('\nK-Means rgb clustering algorithm\n')

    printUsage()
    
    # print input file info
    print('\n\tInput file\n\t----------')
    print('\tdescription: rgb data input file')
    print('\tformat:')
    print('\t\t<identifier> <r value> <g value> <b value>')
    print('\t\t<identifier> <r value> <g value> <b value>')
    print('\t\t<identifier> <r value> <g value> <b value>')
    print('\t\t...')

    # print output file info
    print('\n\tOutput file\n\t----------')
    print('\tdescription: clustered rgb data output file')
    print('\tformat:')
    print('\t\tCluster <r value> <g value> <b value>')
    print('\t\t<rgb point identifier> <r value> <g value> <b value>')
    print('\t\t<rgb point identifier> <r value> <g value> <b value>')
    print('\t\t<rgb point identifier> <r value> <g value> <b value>')
    print('\t\tCluster <r value> <g value> <b value>')
    print('\t\t<rgb point identifier> <r value> <g value> <b value>')
    print('\t\t<rgb point identifier> <r value> <g value> <b value>')
    print('\t\t<rgb point identifier> <r value> <g value> <b value>')
    print('\t\t...')

    # print cluster file info
    print('\n\tCluster file\n\t----------')
    print('\tdescription: cluster data input file')
    print('\tformat:')
    print('\t\t<r value> <g value> <b value>')
    print('\t\t<r value> <g value> <b value>')
    print('\t\t<r value> <g value> <b value>')
    print('\t\t...')

    # print -g flag info
    print('\n\t-g flag\n\t----------')
    print('\tdescription: generate flag used to generate random clusters instead of importing clusters from preset cluster file')

    # print -v flag info
    print('\n\t-v flag\n\t----------')
    print('\tdescription: verbose flag used to output basic running info')

    # print -vv flag info
    print('\n\t-vv flag\n\t----------')
    print('\tdescription: very-verbose flag used to output detailed running info')
    

if __name__ == "__main__":
    main()
