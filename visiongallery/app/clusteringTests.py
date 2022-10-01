from random import randint

def main():
    nodes = ''
    clusters = ''
    nodesFile = 'rgbTestData.txt'
    clustersFile = 'clusters.txt'
    
    numNodes = int(input('Number of nodes to generate: '))
    numClusters = int(input('Number of clusters to generate: '))
    
    print('Generating nodes...')
    nodes = genNodes(numNodes)

    print('Generating clusters...')
    clusters = genClusters(numClusters)
    
    print('Writing nodes to ' + nodesFile)
    writeToFile(nodesFile, nodes)

    print('Writing clusters to ' + clustersFile)
    writeToFile(clustersFile, clusters)

def genNodes(num):
    nodes = ''
    for i in range(num):
        current = str(i) + ' ' + genRGB()
        nodes += current + '\n'
    nodes = nodes[:nodes.rfind('\n')]
    print('Nodes:')
    print(nodes)
    return nodes

def genClusters(num):
    clusters = ''
    for i in range(num):
        current = genRGB()
        clusters += current + '\n'
    clusters = clusters[:clusters.rfind('\n')]
    print('Clusters:')
    print(clusters)
    return clusters

def genRGB():
    r = randint(0,255)
    g = randint(0,255)
    b = randint(0,255)
    rgb = str(r) + ' ' + str(g) + ' ' + str(b)
    return rgb

def writeToFile(filename, data):
    file = open(filename, 'w')
    file.write(data)
    file.close()

if __name__ == "__main__":
    main()
