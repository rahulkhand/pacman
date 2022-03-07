# Written by Rahul Khandelwal
# Last update:  November 30, 2020

'''Prior to coding my map generator, I viewed the map examples and code from:
 https://shaunlebron.github.io/pacman-mazegen/
 This is where I got the idea to start out with half a board
 and reflect it horizontally for symmetrical aesthetic.
 All code below, however, is my own.''' 

import random

class HalfBoard(object):
    def __init__(self):
        self.rows = 31
        self.cols = 14
        self.mapList = \
            [[False for i in range(self.cols)] for j in range(self.rows)]
        self.keyRows = {1, self.rows-2}
        self.keyCols = {1, 2*self.cols-2}
        self.keyPairRows = {i for i in range(11, 18)}
        self.keyPairCols = {j for j in range(9, 18)} 

class rowColSaver(object):
    def __init__(self, cRow, cCol):
        self.cRow = cRow
        self.cCol = cCol

def offLimits(board, row, col):
    if row in board.keyRows or col in board.keyCols or \
        (row in board.keyPairRows and col in board.keyPairCols):
        return True
    else:
        return False

# new random board generator, (6 to 9 proved to be a good range for recursive chunk generation)
def boardGenerate(lowRep=6, highRep=9):
    # template functions
    board = HalfBoard()
    fillEdges(board)
    outerPath(board)
    ghostHouse(board)
    
    # random function
    chunkIt(board, lowRep, highRep)

    # corrector functions
    deadEnd(board)
    patchUp(board)
    removeFillers(board)
    mirror(board)
    patchMirroredBoard(board)
    preserveLeftHalf(board)
    fillEnclosedPaths(board)
    return board.mapList

# fills in the outer border of the half-board to be reflected eventually
def fillEdges(board):
    for i in range(board.rows):
        board.mapList[i][0] = True
    for j in range(board.cols):
        board.mapList[0][j] = True
    for j in range(board.cols):
        board.mapList[board.rows-1][j] = True

# rereflects the left half of the board
def preserveLeftHalf(board):
    for row in range(board.rows):
        halftime = board.mapList[row][:board.cols//2]
        board.mapList[row] = halftime + list(reversed(halftime))

# fills in enclosed paths
def fillEnclosedPaths(board):
    enclosedRows(board)
    enclosedColumns(board)

# checks column to column for enclosed paths
def enclosedColumns(board):
    b = board.mapList
    tRows, tCols = len(board.mapList), len(board.mapList[0])
    for row in range(1, tRows-1):
        for col in range(1, tCols-1):
            nRow, nCol = row, col
            if b[row][col] != True:    continue
            while b[nRow][col] == True:
                nRow += 1
            nRow -= 1
            while b[nRow][nCol] == True and b[row][nCol] == True:
                nCol += 1
            nCol -= 1
            for i in range(row, nRow + 1):
                if b[i][nCol] != True:
                    break
                elif i == nRow:
                    for k in range(row + 1, nRow):
                        for j in range(col + 1, nCol):
                            b[k][j] = True

# checks row to row for enclosed paths
def enclosedRows(board):
    b = board.mapList
    tRows, tCols = len(board.mapList), len(board.mapList[0])
    for row in range(1, tRows-1):
        for col in range(1, tCols-1):
            nRow, nCol = row, col
            if b[row][col] != True:    continue
            while b[row][nCol] == True:
                nCol += 1
            nCol -= 1
            while b[nRow][nCol] == True and b[nRow][col] == True:
                nRow += 1
            nRow -= 1
            for j in range(col, nCol + 1):
                if b[nRow][j] != True:
                    break
                elif j == nCol:
                    for i in range(row + 1, nRow):
                        for k in range(col + 1, nCol):
                            b[i][k] = True
            

# develops the main path of the board along the outer edge
def outerPath(board):
    for i in range(1, board.rows-1):
        board.mapList[i][1] = None
    for j in range(1, board.cols):
        board.mapList[1][j] = None
    for j in range(1, board.cols):
        board.mapList[board.rows-2][j] = None

# eliminates double paths down any part of the board
def patchUp(board):
    # eliminates double paths down middle of board to keep ghost house intact
    keyC = 13
    for row in range(board.rows):
        if board.mapList[row][keyC-1]:
            board.mapList[row][keyC] = True

    # then eliminates double paths everywhere else
    rStart, rEnd = 1, board.rows-2
    cStart, cEnd = 1, board.cols-2
    for row in range(rStart, rEnd+1):
        for col in range(cStart, cEnd+1):
            # check through the 4 tiles of the definite double path
            quartile(board, row, col)

# patches up doubled paths caused by mirroring
def patchMirroredBoard(board):
    rStart, rEnd = 1, board.rows-2
    cStart, cEnd = 1, board.cols-2
    for row in range(rStart, rEnd+1):
        for col in range(cStart, cEnd+1):
            if doubleFill(board, row, col):
                pass
                

# checks 2x2 cells to remove awkward alternating diagonal patterns                            
def quartile(board, row, col):
    keyRows = {1, board.rows-2}
    keyPairRows = {i for i in range(11, 18)}
    keyPairCols = {j for j in range(9, board.cols)} 
    if board.mapList[row][col] == board.mapList[row][col+1] == \
        board.mapList[row+1][col] == board.mapList[row+1][col+1] == None:
        for fillRow in (row, row+1):
            for fillCol in (col, col+1):
                if fillRow in keyRows or fillCol == 1 or \
                    (fillRow in keyPairRows and fillCol in keyPairCols):
                    continue
                board.mapList[fillRow][fillCol] = True
                # if filling creates a checker board pattern
                if checkerBoard(board, fillRow, fillCol):
                    board.mapList[fillRow][fillCol] = None
                    continue
                # or if filling the cell creates a dead end
                adjacentPath = deadEndCheck(board, fillRow, fillCol)
                for (tempRow, tempCol) in adjacentPath:
                    if deadEndCheck(board, tempRow, tempCol, True):
                        # leave it the way it is
                        board.mapList[fillRow][fillCol] = None
                        continue
                # when a square gets filled in the quartile has been fixed
                if board.mapList[fillRow][fillCol] == True:
                    return

# fills in a 2 x 2 path with 2 cells in one pass if no dead ends form
def doubleFill(board, row, col):
    b = board.mapList
    if b[row][col] == b[row+1][col+1] == b[row][col+1] == b[row+1][col] == None:
        pass
    else:
        return
    for x in range(4):
        if x == 0:
            row1, col1, row2, col2 = row, col, row, col + 1
        elif x == 1:
            row1, col1, row2, col2 = row, col, row + 1, col
        elif x == 2:
            row1, col1, row2, col2 = row, col + 1, row + 1, col + 1
        else:
            row1, col1, row2, col2 = row + 1, col, row + 1, col + 1

        if offLimits(board, row1, col1) or offLimits(board, row2, col2):    continue
        board.mapList[row1][col1] = board.mapList[row2][col2] = True
        adjacentPath1 = deadEndCheck(board, row1, col1)
        adjacentPath2 = deadEndCheck(board, row2, col2)
        flag = False

        for (pathRow, pathCol) in adjacentPath1.union(adjacentPath2):
            if deadEndCheck(board, pathRow, pathCol, True) and \
                board.mapList[pathRow][pathCol] != True:
                board.mapList[row1][col1] = board.mapList[row2][col2] = None
                flag = True

        if flag and x == 3:   return flag
        elif flag:  continue
        else:   return flag
               

# checks for unwanted diagonal board patterns
def checkerBoard(board, row, col):
    b = board.mapList
    rowChgs = colChgs = [-1, 1]
    for rowChg in rowChgs:
        for colChg in colChgs:
            diagRow, diagCol = row + rowChg, col + colChg
            if outOfRange(board, diagRow, diagCol):
                continue
            else:
                rowBox, colBox = (diagRow, col), (row, diagCol)
                if b[rowBox[0]][rowBox[1]] == None\
                    and b[colBox[0]][colBox[1]] == None\
                        and b[diagRow][diagCol] == True:
                        return True
    return False

# determines a cell to be a dead end by creating a set of legal exit points
def deadEndCheck(board, row, col, justChecking=False):
    dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    adjacentPath = set()
    for direction in dirs:
        curRow = row + direction[0]
        curCol = col + direction[1]
        
        if outOfRange(board, curRow, curCol):
            continue
        elif board.mapList[curRow][curCol] == None:
            adjacentPath.add((curRow, curCol))

    # cases for different uses of deadEndCheck
    if len(adjacentPath) <= 1 and justChecking:
        return True
    elif justChecking:
        return False
    else:
        return adjacentPath

# removes dead ends
def deadEnd(board):
    for row in range(board.rows):
        for col in range(board.cols):
            if board.mapList[row][col] == None:
                # check to see if there are at least two adjacent path cells 
                # to every path cell
                deadEndRecurse(board, row, col)

# helper to deadEnd                
def deadEndRecurse(board, row, col):
    # finds all the adjacent paths
    adjacentPath = deadEndCheck(board, row, col)
    # if on the right edge before the mirror do not mistake for a dead end
    if col == board.cols-1 and len(adjacentPath) == 1:
        pass
    # otherwise fill in all dead ends where applicable
    elif len(adjacentPath) == 0:
        board.mapList[row][col] = True
    elif len(adjacentPath) == 1:
        board.mapList[row][col] = True
        newRow, newCol = adjacentPath.pop()
        # filling in a deadEnd might create a new one, so recursion is necessary
        deadEndRecurse(board, newRow, newCol)

# completes the board by reflecting across vertical axis
def mirror(board):
    for row in range(board.rows):
        board.mapList[row] += list(reversed(board.mapList[row]))
    board.cols *= 2

# makes a solid block, primitive ghost house
def ghostHouse(board):
    r1, r2 = 12, 16
    c1, c2 = 10, 13
    # magic numbers in for loops to emulate real board size of pac-man
    for i in range(r1, r2+1):
        for j in range(c1, c2+1):
            board.mapList[i][j] = True
    surround(board, r1, c1, r2, c2)

# creates the chunks of walls in the maze
def chunkIt(board, lowRep, highRep):
    randTrans = {'extCol': 1, 'extRowDown': 1, 'extRowUp':1, 'tessallate': 1}
    for i in range(2, board.rows-2):
        for j in range(2, board.cols):
            occurrence = random.randint(lowRep, highRep)
            form = random.choice(list(randTrans))
            save = rowColSaver(i+1, j+1)
            chunkGen(board, occurrence, form, i, j, i+1, j+1, save)
            # call a random chunk generator

# iterates through a chunk and randomly extends wall cells sidewards
def extCol(board, r1, c1, r2, c2):
    for row in range(r1, r2):
        for col in range(c1, c2):
            randomExt = random.choice([True, False])
            if outOfRange(board, row, col+1) or not randomExt:
                continue
            elif board.mapList[row][col] and board.mapList[row][col+1] == False:
                board.mapList[row][col+1] = True
    return r2, c2+1

# iterates through a chunk and randomly extends wall cells downwards
def extRowDown(board, r1, c1, r2, c2):
    for row in range(r1, r2):
        for col in range(c1, c2):
            randomExt = random.choice([True, False])
            if outOfRange(board, row+1, col) or not randomExt:
                continue
            elif board.mapList[row][col] and board.mapList[row+1][col] == False:
                board.mapList[row+1][col] = True
    return r2+1, c2

# iterates through a chunk and randomly extends wall cells upwards
def extRowUp(board, r1, c1, r2, c2):
    for row in range(r1, r2):
        for col in range(c1, c2):
            randomExt = random.choice([True, False])
            if outOfRange(board, row, col) or\
                outOfRange(board, row-1, col) or not randomExt:
                continue
            elif board.mapList[row][col] and board.mapList[row-1][col] == False:
                board.mapList[row-1][col] = True
    return r1-1, c1

# magnifies a chunk through row and column extensions
def tessallate(board, r1, c1, r2, c2):
    r2, c2 = extCol(board, r1, c1, r2, c2)
    r2, c2 = extRowDown(board, r1, c1, r2, c2)
    return r2, c2

# an absolute beast of a generator that uses multiple helpers to do magic
def chunkGen(board, occurrence, form, row, col, cRow, cCol, save, depth=1, cont=True):
    b = board.mapList
    if occurrence == 0:
        placeBlock(board, row, col)
        surround(board, row, col, cRow, cCol)
        return
    # in case the random range specified in chunkIt is <= 1
    if depth > occurrence or (b[row][col] != False and cont):
        return
    else:
        randomR = random.randint(0, 3)
        if depth == 1 and b[row][col] == False:
            b[row][col] = True    
            cRow, cCol = tessallate(board, row, col, cRow, cCol)
        elif randomR == 0:
            cRow, cCol = extCol(board, row, col, cRow, cCol)
        elif randomR == 1:
            cRow, cCol = extRowDown(board, row, col, cRow, cCol)
        elif randomR == 2:
            cRow, cCol = tessallate(board, row, col, cRow, cCol)
        else:
            row, col = extRowUp(board, row, col, cRow, cCol)
        # After making a random chunk through recursive block transformations, 
        # the chunk is surrounded by a path in the base case
        cont = False
        if depth == occurrence - 1:
            save.cRow, save.cCol = cRow, cCol
        chunkGen(board, occurrence, form, row, col, cRow, cCol, save, depth + 1, cont)
        if depth == 1:
            surround(board, row, col, save.cRow, save.cCol)
       
def placeBlock(board, row, col):
    b = board.mapList
    if b[row][col] == False:
        b[row][col] = True        

# not within board bounds
def outOfRange(board, row, col):
    if row >= board.rows or col >= board.cols or row < 0 or col < 0:
        return True
    return False

# draws a path around a newly formed wall
def surround(board, r1, c1, r2, c2):
    # takes in parameters for outline of the chunk
    topRow, topCol = r1 - 1, c1 - 1
    bottomRow, bottomCol = r2 + 1, c2 + 1
    for i in range(topRow, bottomRow+1):
        for j in range(topCol, bottomCol+1):
            if outOfRange(board, i, j):
                continue
            elif wordSearchFromCell(board, i, j):
                board.mapList[i][j] = None

def wordSearchFromCell(board, row, col):
    # technique derived from 15-112 notes
    if board.mapList[row][col] != False:
        # cant overwrite a previously determined cell
        return False
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    for direction in dirs:
        newRow = row + direction[0]
        newCol = col + direction[1]
        if outOfRange(board, newRow, newCol):
            continue
        elif board.mapList[newRow][newCol] == True:
            # undetermined cell that is next to a wall turns into a path cell
            return True

# removes excess wallspace
def removeFillers(board):
    if board.rows != 31 or board.cols != 14:
        return
    board.mapList[12][13] = False
    for r in range(13, 16):
        for c in range(11, 14):
            board.mapList[r][c] = False


