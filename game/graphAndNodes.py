# Last Update: December 6, 2020
# Rahul Khandelwal
# This file is for the implementation of Dijkstra's algorithm for shortest path
# finding for the pac-man AI

from mapGen import *

# important temporary node remover
class tempConnecter(object):
    def __init__(self):
        self.basket = {}

    def fakeNode(self, fake, graphMap):
        self.basket[fake] = graphMap[fake]

    def addTempOn(self, pseudo, graphMap):
        for node in self.basket[pseudo]:
            dictBuild(graphMap, node, pseudo)

    def removeGivenTemp(self, temp, graphMap):
        removeSet = self.basket[temp]
        for real in removeSet:
            if real in graphMap:
                graphMap[real].remove(temp)
        
        self.basket.pop(temp)

    def removeAllTemps(self, graphMap):
        for fake in self.basket:
            for real in self.basket[fake]:
                if real in graphMap:
                    graphMap[real].remove(fake)

        self.basket = {}

connecter = tempConnecter()

# takes input board and the type for a wall and type for a path
def noding(board, wall, path):
    rowNodes, colNodes, totalNodes = {}, {}, set()
    rows = len(board)
    cols = len(board[0])
    for row in range(rows):
        for col in range(cols):
            if board[row][col] == path:
                if detNode(board, row, col, path):
                    dictBuild(rowNodes, row, col)
                    dictBuild(colNodes, col, row)
                    totalNodes.add((row, col))

    return rowNodes, colNodes, totalNodes

# builds up/adds onto key and sets of a dictionary
def dictBuild(d, key, val):
    if key not in d:
        d[key] = {val}
    else:
        d[key].add(val)

def notOnBoard(row, col, board):
    rows = len(board)
    cols = len(board[0])
    if row < 0 or col < 0 or row >= rows or col >= cols:    return True
    else:   return False

# this function assumes the node being checked is indeed a path cell
# it determines whether a path cell has an orthogonal junction
def detNode(board, row, col, path):
    nodeDirs = set()
    sumRow, sumCol = 0, 0
    dirs = {(-1, 0), (1, 0), (0, -1), (0, 1)}
    for direction in dirs:
        nRow, nCol = row + direction[0], col + direction[1]
        if notOnBoard(nRow, nCol, board):   continue
        elif board[nRow][nCol] == path:
            nodeDirs.add(direction)
            sumRow += direction[0]
            sumCol += direction[1]

    if len(nodeDirs) > 2:   return True
    elif len(nodeDirs) == 2:
        if (sumRow, sumCol) != (0, 0):  return True
    return False

# denote cNode as a neighboring node
# returns a map of nodes and edges in the form {node: (cNodeRow, cNodeCol, dist), ...}
def makeMap(board, wall, path, extras=False):
    dirs = {(-1, 0), (1, 0), (0, -1), (0, 1)}
    rowNodes, colNodes, totalNodes = noding(board, wall, path)
    graphMap = {}
    for (row, col) in totalNodes:
        nodeAdder(totalNodes, dirs, row, col, board, path, graphMap)

    if extras:  return rowNodes, colNodes, totalNodes, graphMap        
    return graphMap


# adds a node, corresponding to its neighbors, to the main graph map
def nodeAdder(totalNodes, dirs, row, col, board, path, graphMap):
    for d in dirs:
        nRow, nCol = row + d[0], col + d[1]
        if notOnBoard(nRow, nCol, board): continue
        elif board[nRow][nCol] != path: continue
        else:
            while (nRow, nCol) not in totalNodes:
                nRow += d[0]
                nCol += d[1]
            
            dictBuild(graphMap, (row, col), (nRow, nCol))

# returns distance between two nodes
def nodeDist(node1, node2):
    return abs(node1[0] - node2[0]) + abs(node1[1] - node2[1])

# returns the shortest path and that distance between two nodes
def shortestPathBetweenNodes(startNode, endNode, graphMap):
    if startNode not in graphMap or endNode not in graphMap:   return None
    solvedNodes = {startNode}
    nodesAndDist = {startNode: 0}
    redirect = {}

    solvedNodes, nodesAndDist, redirect = \
        shortestSearch(endNode, solvedNodes, nodesAndDist, redirect, graphMap)
    shortestPath = pathTransform(startNode, endNode, redirect)
    return shortestPath, nodesAndDist[endNode]
    
'''Pathfinding algorithm intuition from: 
http://optlab-server.sce.carleton.ca/POAnimations2007/DijkstrasAlgo.html'''

# obtains the shortest path through Dijkstra's pathfinding algorithm
def shortestSearch(endNode, solvedNodes, nodesAndDist, redirect, graphMap):

    while endNode not in solvedNodes:
        minCost = 100 # this number is sufficiently large, ideally should be infinity
        solved, direct = None, None
        for solvedNode in solvedNodes:
            neighborNodes = graphMap[solvedNode]
            for neighbor in neighborNodes:
                if neighbor not in solvedNodes:
                    traverseDist = nodesAndDist[solvedNode]
                    curDist = nodeDist(solvedNode, neighbor)
                    curCost = traverseDist + curDist
                    if curCost < minCost:
                        minCost, solved, direct = curCost, neighbor, solvedNode

        solvedNodes.add(solved)
        nodesAndDist[solved] = minCost
        redirect[solved] = direct

    return solvedNodes, nodesAndDist, redirect

# converts a dictionary of connecting nodes to a list format procedure
def pathTransform(startNode, endNode, redirect):
    # must consider trivial case of the immediate path
    if endNode == startNode:    return [endNode]

    step = redirect[endNode]
    steps = [endNode, step]
    while step != startNode:
        step = redirect[step]
        steps.append(step)
    steps.reverse()
    return steps

# adds the pac man node to the graph
def addPlayerNode(pRow, pCol, graphMap, board, path):
    if (pRow, pCol) in graphMap:    return 'PLEASE DONT DELETE'
    dirs = {(-1, 0), (1, 0), (0, -1), (0, 1)}
    totalNodes = set(graphMap.keys())
    nodeAdder(totalNodes, dirs, pRow, pCol, board, path, graphMap)

# after updating player location, the player node must be deleted and replaced
def deletePlayerNode(pRow, pCol, graphMap):
    key = (pRow, pCol)
    if key in graphMap: graphMap.pop(key)

# returns the very next intersection where the ghost can change direction
def ghostNode(gRow, gCol, cDir, graphMap):
    if (gRow, gCol) in graphMap:    return (gRow, gCol)
    nRow, nCol = gRow + cDir[1], gCol + cDir[0]
    while (nRow, nCol) not in graphMap:
        nRow += cDir[1]
        nCol += cDir[0]

    return (nRow, nCol)

# returns the direction from pacman to a ghost and the path distance between
def pacmanToGhost(pRow, pCol, gRow, gCol, cDir, graphMap, board, path, gPos=False, option=False):
    delFlag = addPlayerNode(pRow, pCol, graphMap, board, path)
    connecter.fakeNode((pRow, pCol), graphMap)
    connecter.addTempOn((pRow, pCol), graphMap)

    if gPos:
        gFlag = addPlayerNode(gRow, gCol, graphMap, board, path)
        gNode = (gRow, gCol)
        connecter.fakeNode(gNode, graphMap)
        connecter.addTempOn(gNode, graphMap)
    else:
        gNode = ghostNode(gRow, gCol, cDir, graphMap)
        gFlag = None

    procedure, distance = shortestPathBetweenNodes((pRow, pCol), gNode, graphMap)

    if gFlag != 'PLEASE DONT DELETE' and gPos:
        connecter.removeGivenTemp(gNode, graphMap) 
        deletePlayerNode(gRow, gCol, graphMap)
        
    if delFlag != 'PLEASE DONT DELETE':
        connecter.removeGivenTemp((pRow, pCol), graphMap)
        deletePlayerNode(pRow, pCol, graphMap)

        # a route that is only one stage long while pacman itself is at a node
        if len(procedure) > 1:  firstSite = procedure[1]
        else:   firstSite = procedure[0]
    else:
        if len(procedure) > 1:  firstSite = procedure[1]
        else:   firstSite = procedure[0]
    alpha, beta = 1, 1
    if firstSite[0] < 0:    alpha = -1
    if firstSite[1] < 0:    beta = -1
    deltaRow = ((firstSite[0] - pRow) % 2) * alpha
    deltaCol = ((firstSite[1] - pCol) % 2) * beta

    if option:  return procedure, distance
    else:   return (deltaCol, deltaRow), distance


