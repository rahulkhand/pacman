# Written by Rahul Khandelwal
# Last update:  December 9, 2020
# This is the main executable file which runs all the others

from cmu_112_graphics import *
from mapGen import *
from graphAndNodes import *
from PIL import Image, ImageDraw
import string, time, random

'''Pac-Man logo image from https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.bandainamcoent.com%2Fgames%2Fpac-man&psig=AOvVaw0rTPueYFFT36CvchHzIq4G&ust=1607399210016000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCIjW6-n6uu0CFQAAAAAdAAAAABAM '''
'''Pac-Man eating dot image from https://images.fastcompany.net/image/upload/w_596,c_limit,q_auto:best,f_auto/fc/1683023-inline-inline-1-why-video-games-were-never-the-same-after-pac-man-burst-into-arcades.jpg'''
'''Pac-man ghost names used in instructions display. Names, colors, pellet design, and other likenesses of the original Pac-man are accredited to Namco.'''

#TODO
# original graphics

def almostEqualMod1(d1, d2, epsilon=0.01):
    # modified cmu 15-112 function
    return (1 - abs(d2 - d1) < epsilon) or abs(d2 - d1) < epsilon

def almostEqual(d1, d2, epsilon=10**-7):
    # cmu 15-112 function
    return abs(d2 - d1) < epsilon

def appStarted(app):
    setUpSplashWidgets(app)
    app.paused, app.classic, app.revenge, app.instructions = False, False, False, True
    app.ghostSequence = False
    app.levelChange = False
    app.gameOver = False
    app.ghostDelay = 7
    app.gRem = 4
    app.rows = 31
    app.cols = 28
    app.lives, app.level = 3, 1
    app.scatterCount = app.chaseCount = app.stateFlips = 0
    app.powerUps = {(1,1), (app.rows-2, 1), (1, app.cols-2), (app.rows-2, app.cols-2)}
    app.pScore, app.gScore = -10, 0
    app.cellSize = app.height / (app.rows + 2)
    app.margin = app.cellSize
    app.procedure, app.pillEaten = None, False
    app.splashScreen, app.pauseStarted, app.roundStart = True, False, True
    app.scatter = True
    app.chase = False
    app.splashImage = Image.open("pacmanSplash.png")
    # app.selection = Image.open('transparent.jpg')
    app.timerCounter = 0
    app.pFactor = 5
    app.pSpeed = app.cellSize / app.pFactor
    app.gSpeed = app.cellSize / 6
    app.dirs = {'Up': (0, -1), 'Down': (0, 1), 'Left': (-1, 0), 'Right': (1, 0)}
    app.topBorder = app.leftBorder = app.margin
    app.gR1, app.gR2, app.gC1, app.gC2 = 12, 16, 10, 17
    app.rightBorder = app.margin + app.cellSize * app.cols
    app.bottomBorder = app.margin + app.cellSize * app.rows
    app.wallColor = 'turquoise'
    app.background = '#000080'
    generateMap(app)
    condenseWalls(app)
    developImage(app)
    setPlayers(app)
    

def mousePressed(app, event):
    if app.splashScreen:
        clickedInWidget(app, event.x, event.y)
    elif not app.gameOver:
        clickedHome(app, event.x, event.y)
    elif app.gameOver:
        appStarted(app)

def clickedHome(app, x, y):
    x1 = 2*app.margin + app.cols*app.cellSize
    w, h = app.width, app.height
    y1 = h-80
    x2 = w-20
    y2 = h-app.margin

    if inRectangle(x, y, x1, y1, x2, y2):
        appStarted(app)

def inRectangle(x, y, x1, y1, x2, y2):
    if x <= x2 and x >= x1 and y <= y2 and y >= y1:
        return True
    else:
        return False

def midPoint(c1, c2):
    return (c1 + c2) / 2

def semiAxis(c1, c2):
    return (c2 - c1) / 2

def setUpSplashWidgets(app):
    app.LX1, app.LX2, app.LY1, app.LY2 = 30, 480, 460, 600
    app.RX1, app.RX2, app.RY1, app.RY2 = 500, 950, 460, 600
    app.GX1, app.GX2, app.GY1, app.GY2 = 500, 20, 600, 60

    app.h1 = midPoint(app.LX1, app.LX2)
    app.k1 = midPoint(app.LY1, app.LY2)
    app.h2 = midPoint(app.RX1, app.RX2)
    app.k2 = midPoint(app.RY1, app.RY2)
    app.a1 = semiAxis(app.LX1, app.LX2)
    app.b1 = semiAxis(app.LY1, app.LY2)
    app.a2 = semiAxis(app.RX1, app.RX2)
    app.b2 = semiAxis(app.RY1, app.RY2)
    
    app.h3 = midPoint(app.GX1, app.GX2)
    app.k3 = midPoint(app.GY1, app.GY2)
    app.a3 = midPoint(app.GX1, app.GX2)
    app.b3 = midPoint(app.GY1, app.GY2)

def pointInEllipse(x, y, h, k, a, b):
    if ((x - h) ** 2 / a ** 2) + ((y - k) ** 2 / b ** 2) <= 1:
        return True
    else:
        return False

# only call this function if app.splashScreen is live
def clickedInWidget(app, x, y):
    if pointInEllipse(x, y, app.h1, app.k1, app.a1, app.b1):
        app.classic = True
        app.splashScreen = False
        app.ghostSequence = True
        app.ghostTimer = time.time()
        app.playerSelect = app.playerList[0]
    elif pointInEllipse(x, y, app.h2, app.k2, app.a2, app.b2):
        app.revenge = True
        app.splashScreen = False
        app.ghostSequence = True
        app.ghostTimer = time.time()
        app.playerSelect = None

def resetPlayers(app):
    app.pac.x, app.pac.y = app.pX, app.pY
    app.blinky.x, app.blinky.y = app.bGX, app.bGY
    app.inky.x, app.inky.y = app.iGX, app.iGY
    app.pinky.x, app.pinky.y = app.pGX, app.pGY
    app.clyde.x, app.clyde.y = app.cGX, app.cGY
    app.pac.cDir, app.pac.tDir = app.dirs['Right'], app.dirs['Right']
    app.inky.cDir = app.blinky.cDir = app.pinky.cDir = app.clyde.cDir = None
    app.inky.tDir = app.blinky.tDir = app.pinky.tDir = app.clyde.tDir = None
    # ghosts back off at the start of every spawn
    app.anxious, app.scatter = False, True
    if app.stateFlips > 0:  app.stateFlips -= 1
    app.pScore -= 10
    app.slow = app.gSpeed / 2

def setPlayers(app):
    gap = app.cellSize
    app.pX = app.margin + int(app.cols / 2) * app.cellSize - app.cellSize / 2
    app.pY = app.pX + (int((app.rows - app.cols) / 2) + 3) * app.cellSize
    app.bGX, app.bGY = app.pX, app.pY - 2*app.cellSize
    app.iGX, app.iGY = app.pX+gap, app.pY - 2*app.cellSize
    app.pGX, app.pGY = app.pX+2*gap, app.pY - 2*app.cellSize
    app.cGX, app.cGY = app.pX-gap, app.pY - 2*app.cellSize
    app.pac = Runner(app.pX, app.pY, 'yellow', app.pSpeed)
    app.pac.cDir, app.pac.tDir = app.dirs['Right'], app.dirs['Right']
    app.blinky = Ghost(app.bGX, app.bGY, 'red', app.gSpeed)
    app.inky = Ghost(app.iGX, app.iGY, 'blue', app.gSpeed)
    app.pinky = Ghost(app.pGX, app.pGY, 'pink', app.gSpeed)
    app.clyde = Ghost(app.cGX, app.cGY, 'orange', app.gSpeed)
    app.anxious = False
    app.playerList = [app.pac, app.blinky, app.inky, app.pinky, app.clyde]
    app.playerSelect = None
    app.anxiousGhosts = 4
    app.slow = app.gSpeed / 2
    app.freeze = app.anxiousTime = time.time()
        
def developImage(app):
    app.scoreCount = 0
    if app.gScore < 0:  app.gScore = 0
    app.dotR = r = 0.2 * app.cellSize / 2
    app.dotBigR = bR = 3 * r
    image1 = Image.new('RGB', (app.width, app.height), app.background)
    app.draw = ImageDraw.Draw(image1)
    for i in range(app.rows):
        for j in range(app.cols):
            r1, c1, r2, c2 = getCellBounds(app, i, j)
            midX, midY = (r1 + r2) / 2, (c1 + c2) / 2
            if (i, j) in app.powerUps:  
                app.draw.ellipse((midX-bR, midY-bR, midX+bR, midY+bR), fill='#FCED58')
                app.scoreCount += 50
                app.gScore += 50
            elif app.board[i][j] == None:
                app.draw.rectangle((midX-r, midY-r, midX+r, midY+r), fill='#FAE100')
                app.scoreCount += 10
                app.gScore += 10

    app.gScore += 8000 # potential score to be lost if pac man eats every ghost
    app.scoreCount += 8000
    
    app.image = image1

def overcoat(app, i, j):
    app.draw.rectangle(getCellBounds(app, i, j), fill=app.background)

def distance(x1, y1, x2, y2):
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** (1 / 2)

def outOfBoard(app, row, col):
    if row < 0 or col < 0 or row >= app.rows or col >= app.cols:    return True
    return False

def collideWithDot(app):
    r, pR, bR = app.dotR, 0.9 * app.cellSize / 2, app.dotBigR
    x1, y1 = pacCell(app)
    for (cellR, cellC) in [(x1-1, y1), (x1, y1), (x1+1, y1), (x1, y1-1), (x1, y1+1)]:
        if outOfBoard(app, cellR, cellC):
            continue
        else:
            dotX = app.margin + app.cellSize * (cellC + 0.5)
            dotY = app.margin + app.cellSize * (cellR + 0.5)
            if app.pacDots[cellR][cellC] == True:
                if collision(app.pac.x, app.pac.y, pR, dotX, dotY, r):
                    app.pacDots[cellR][cellC] = None
                    overcoat(app, cellR, cellC)
                    app.dotCount -= 1
                    app.pScore += 10
                    app.gScore -= 10
            elif app.pacDots[cellR][cellC] == 'power':
                if collision(app.pac.x, app.pac.y, pR, dotX, dotY, bR):
                    app.pacDots[cellR][cellC] = None
                    app.pillEaten = True
                    app.anxious = True
                    app.anxiousTime = time.time()
                    overcoat(app, cellR, cellC)
                    app.powerCount -= 1
                    app.pScore += 50
                    app.gScore -= 50
                    app.anxiousGhosts = 4
                    purplize(app)

def purplize(app):
    for ghost in app.playerList[1:]:
        gRow, gCol = getCell(app, ghost.x, ghost.y)
        if ghost.color == 'white':  continue
        ghost.color = 'purple'
    if type(app.playerSelect) == Ghost:
        app.playerSelect.speed = app.slow    
# takes in the x, y coordinates and radius of two circles and detects collision
def collision(x1, y1, r1, x2, y2, r2):
    if distance(x1, y1, x2, y2) <= (r1 + r2):    return True
    elif almostEqual(x1, x2) and almostEqual(y1, y2):   return True
    else:   return False

class Runner(object):

    def __init__(self, x, y, color, speed):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.originalColor = self.color
        self.cDir = None
        self.tDir = None
    
    # updates entity location when called
    def moving(self, app):
        
        # ensures player is in the center of a cell before changing direction
        epX = (self.x - app.pX) / app.cellSize
        epY = (self.y - app.pY) / app.cellSize
        if almostEqualMod1(epX, int(epX)) and almostEqualMod1(epY, int(epY)):
            self.cDir = self.tDir

        # actual movement code
        if self.cDir != None and self.keepPlayerOutofWall(app):
            self.x += self.cDir[0] * self.speed
            self.y += self.cDir[1] * self.speed

    # permits player warping on board edges and prevents movement out of canvas        
    def keepPlayerInBounds(self, app):
        if self.x > app.rightBorder:
            self.x = app.margin + app.cellSize / 2
        elif self.y > app.bottomBorder:
            self.y = app.margin + app.cellSize / 2
        elif self.y < app.topBorder:
            self.y = app.bottomBorder - app.cellSize / 2
        elif self.x < app.leftBorder:
            self.x = app.rightBorder - app.cellSize / 2
    
    # returns true if a runner is at the center of a cell
    def centered(self, app):
        (playerRow, playerCol) = getCell(app, self.x, self.y)
        (x0, y0, x1, y1) = getCellBounds(app, playerRow, playerCol)
        midCellX = (x0 + x1) / 2
        midCellY = (y0 + y1) / 2
        if almostEqual(midCellX, self.x) and almostEqual(midCellY, self.y):
            return True
        else:
            return False

    def isPerpendicular(self, app, direction):
        x1, x2 = self.cDir[0] + direction[0], self.cDir[1] + direction[1]
        if x1 % 2 == 1 and x2 % 2 == 1:
            return True
        return False

    def validDirs(self, app, targetRow, targetCol, gRow, gCol):
        leastSquare = []
        for direction in app.dirs:
            dCol, dRow = app.dirs[direction][0], app.dirs[direction][1]
            nRow, nCol = gRow + dRow, gCol + dCol
            if not outOfBoard(app, nRow, nCol) and app.board[nRow][nCol] == None:
                if dRow != -self.cDir[1] or dCol != -self.cDir[0] or \
                    self.color == 'yellow':
                    dist = boardDistance(nRow, nCol, targetRow, targetCol)
                    leastSquare.append((direction, dist))

        return leastSquare

    # algorithm for entity to chase a given tile
    def chase(self, app, targetRow, targetCol):
        if not self.centered(app): return

        (gRow, gCol) = getCell(app, self.x, self.y)
        if app.board[gRow][gCol] != None:   return

        leastSquare = self.validDirs(app, targetRow, targetCol, gRow, gCol)

        # ghost chooses the direction that yields the least separation
        minDir, minVal = leastSquare[0][0], leastSquare[0][1]
        for (smallDir, smallVal) in leastSquare:
            if smallVal < minVal:
                minDir = smallDir
        self.tDir = app.dirs[minDir]

    def isReverse(self, dRow, dCol):
        if self.cDir == None:   return False
        elif self.cDir[0] == -dCol and self.cDir[1] == -dRow:   return True
        return False

    # denies player from passing through walls
    def keepPlayerOutofWall(self, app):
        if self.centered(app):
            (playerRow, playerCol) = getCell(app, self.x, self.y)
            nextRow, nextCol = playerRow + self.cDir[1], playerCol + self.cDir[0]
            if app.board[nextRow][nextCol] == True:
                return False
            elif app.board[nextRow][nextCol] == False and self.color == 'yellow':
                return False
        return True 

    # prevents early player key presses from registering
    def shiftTempDir(self, app):
        if self.tDir != self.cDir and self.cDir != None:
            # allows going backwards instantly to avoid danger
            if self.cDir[0] == -self.tDir[0] and self.cDir[1] == -self.tDir[1]:
                self.cDir = self.tDir
                return
            # eT just indicates that an entity must be more than
            # halfway through the cell before change in direction will register
            eT, fullT = app.cellSize/2.1, app.cellSize
            nextRowPix = self.y + self.cDir[1] * eT + self.tDir[1] * fullT
            nextColPix = self.x + self.cDir[0] * eT + self.tDir[0] * fullT
            (nextRow, nextCol) = getCell(app, nextColPix, nextRowPix)
            
            if app.board[nextRow][nextCol] == True:
                self.tDir = self.cDir
            elif app.board[nextRow][nextCol] == False and self.color == 'yellow':
                self.tDir = self.cDir

def generateMap(app):
    app.board = boardGenerate()
    app.graphMap = makeMap(app.board, True, None)
    generateDots(app)

def generateDots(app):
    app.dotCount = 0
    app.powerCount = 0
    app.pacDots = [[0 for j in range(app.cols)] for i in range(app.rows)]
    for row in range(app.rows):
        for col in range(app.cols):
            if app.board[row][col] == False:
                app.pacDots[row][col] = False
            elif (row, col) in app.powerUps:
                app.pacDots[row][col] = 'power'
                app.powerCount += 1
            else:
                app.pacDots[row][col] = not app.board[row][col]
                if app.pacDots[row][col]:
                    app.dotCount += 1

# from cmu 15-112 course notes
def getCellBounds(app, row, col):
    x0 = app.margin + app.cellSize * col
    x1 = app.margin + app.cellSize * (col + 1)
    y0 = app.margin + app.cellSize * row
    y1 = app.margin + app.cellSize * (row + 1)
    return x0, y0, x1, y1

# from cmu 15-112 course notes
def getCell(app, x, y):
    row = int((y - app.margin) / app.cellSize)
    col = int((x - app.margin) / app.cellSize)
    return row, col

def keyPressed(app, event):
    if app.splashScreen or app.gameOver or app.levelChange:    return

    if event.key == "p":
        if app.paused:
            # paused really does mean paused
            app.extraTime = time.time()
            timeLoss = app.extraTime - app.subtractedTime
            app.ghostTimer += timeLoss
            app.freeze += timeLoss
            app.anxiousTime += timeLoss
        else:
            app.subtractedTime = time.time() 
        app.paused = not app.paused

    elif event.key == 's' and app.paused:
        doStep(app)

    elif event.key == 'r' and app.roundStart:
        app.gScore -= app.scoreCount
        generateMap(app)
        condenseWalls(app)
        developImage(app)
        resetPlayers(app)
        app.ghostTimer = time.time()
    elif event.key == 'i':
        app.instructions = not app.instructions

    # cheat codes
    elif event.key == 'N':
        app.lives += 1
    elif event.key == '-':
        app.dotCount -= 100
        app.powerCount = 0
        if app.dotCount < 100:  app.dotCount = 0
    elif event.key == '+':
        app.dotCount += 100
    elif event.key == 'M':
        app.lives -= 1
    elif event.key == 'S':
        app.scatter = not app.scatter
    elif event.key == 'Y':
        resetPlayers(app)
    
    if app.paused:  return

    # begins the next round
    if event.key == 'Space' and app.roundStart:
        app.roundStart = False
        app.pauseStarted = True
        app.ghostSequence = True
        app.ghostTimer = time.time()
    
    # change user-controlled ghost functionality
    if event.key in string.digits and int(event.key) < len(app.playerList) and app.revenge:
        app.playerSelect = app.playerList[int(event.key)]
        if event.key == '0':    app.playerSelect = None

    # allows user to change direction
    if event.key in app.dirs:
        d = app.dirs[event.key]
        dRow, dCol = d[1], d[0]
        # but not backwards for ghosts
        if type(app.playerSelect) == Ghost and app.playerSelect.isReverse(dRow, dCol):  
            return
        elif app.playerSelect == None:  return

        app.playerSelect.tDir = d
        app.playerSelect.shiftTempDir(app)

def doStep(app):
    
    if app.splashScreen or app.gameOver:    return
    gameOver(app)
    collideWithDot(app)
    nextRound(app)
    collideWithGhost(app)
    
    if app.pauseStarted:
        if app.ghostSequence:  ghostSequence(app)
        if app.revenge: identifyThreats(app)
        scatterTicks(app)
        for player in app.playerList:
            if type(player) == Ghost:   player.healedUp(app)
            row, col = getCell(app, player.x, player.y)
            if player.color == 'white':   
                player.runHome(app)
            elif type(player) == Ghost and playerCell(app, player) == False and app.ghostSequence: continue
            if not app.anxious: originalSpeeds(app)
            player.moving(app)
            player.keepPlayerInBounds(app)
            if player.color == 'white': continue
            if type(player) == Ghost and app.playerSelect != player:
                if app.scatter and not app.anxious:
                    player.scatter(app)
                elif app.anxious and player.color == 'purple':
                    player.anxious(app)
                    player.keepPlayerOutofWall(app)
                else:
                    player.AI(app)
        if app.pillEaten: 
            goBackwards(app)

def scatterTicks(app):
    # 50 ticks a second with current timerFired settings
    secondTicks = 1000 // app.timerDelay
    chaseTime = 20
    scatterTime = 4

    if app.anxious: return # anxious mode should not interrupt the sequence
    elif app.level > 4 or app.stateFlips >= 3:   
        app.chase = True
        app.scatter = False
        return
    elif app.scatter == False:
        app.chaseCount += 1
    elif app.scatter == True:
        app.scatterCount += 1
    
    # state flipping mechanism
    if app.chase and app.chaseCount % (chaseTime * secondTicks) == 0:
        app.scatter = True
        app.chase = False
    elif app.scatter and app.scatterCount % (scatterTime * secondTicks) == 0:
        app.scatter = False
        app.chase = True
        app.stateFlips += 1


def goBackwards(app):
    for ghost in app.playerList[1:]:
        gRow, gCol = getCell(app, ghost.x, ghost.y)
        if ghost.tDir == None or app.board[gRow][gCol] == False or \
            (app.board[gRow+1][gCol] == False and ghost.cDir == (0, -1)) or ghost.color == 'white':  continue
        elif app.playerSelect != ghost:
            ghost.tDir = (-ghost.cDir[0], -ghost.cDir[1])
            ghost.cDir = ghost.tDir
    app.pillEaten = False

def playerCell(app, player):
    row, col = getCell(app, player.x, player.y)
    return app.board[row][col]

def freezeFrame(app, color=None):
    if color in ['white', 'purple']:
        return False
    elif app.pauseStarted:    
        app.freeze = time.time()
        app.lives -= 1
        app.pauseStarted = False
        app.ghostSequence = True
    elif app.freeze <= time.time() - 3:
        app.pauseStarted = True
        app.ghostTimer = time.time()
        app.pScore += 10
        return True

def collideWithGhost(app):
    r = app.cellSize * 0.9 / 2
    for player in app.playerList[1:]:
        if collision(app.pac.x, app.pac.y, r, player.x, player.y, r):
            frame = freezeFrame(app, player.color)
            if frame:
                resetPlayers(app)
                originalColors(app)
            elif frame == False:
                if player.color != 'white':
                    app.pScore += 200 * (5 - app.anxiousGhosts)
                    app.gScore -= 200 * (5 - app.anxiousGhosts)
                    app.anxiousGhosts -= 1
                player.color = 'white'

def timerFired(app):
    if not app.paused:
        doStep(app)
    else:
        pass
        

# draws the top, left, right, and bottom walls of the game
def drawBorderWalls(app, canvas):
    topL = (app.margin, app.margin)
    topR = (app.margin + app.cols*app.cellSize, app.margin)
    botL = (app.margin, app.height-app.margin)
    botR = (app.margin + app.cols*app.cellSize, app.height-app.margin)
    s = app.cellSize
    c = app.wallColor
    canvas.create_rectangle(topL, botL[0]+s, botL[1], fill=c, outline=c)
    canvas.create_rectangle(topL, topR[0], topR[1]+s, fill=c, outline=c)
    canvas.create_rectangle(botL, botR[0], botR[1]-s, fill=c, outline=c)
    canvas.create_rectangle(botR[0]-s, botR[1], topR, fill=c, outline=c)

# removes the gridlike appearance on all walls
def condenseWalls(app):
    app.canvasWalls = []
    condensedChecker = [ [False for j in range(app.cols)] for i in range(app.rows)]
    for row in range(2, app.rows-2):
        for col in range(2, app.cols-2):
            if app.board[row][col] == True and not condensedChecker[row][col]:
                blockSearch(app, condensedChecker, row, col) 
    return

# algorithm to search for large chunks of walls together
def blockSearch(app, checkList, row, col):
    r, c = row, col
    # looks for connecting walls by columns
    while app.board[r][c] == True:
        checkList[row][c] = True
        c += 1

    stopper = True
    r += 1
    # looks for connecting rows of walls
    while stopper:
        for j in range(col, c):
            if not app.board[r][j]:
                stopper = False
                break
        if stopper:
            for j in range(col, c):
                checkList[r][j] = True
        r += 1

    # piecing together the block for canvas    
    (x0, y0, ignore, ignoreAgain) = getCellBounds(app, row, col)
    (x1, y1, ignore, ignoreAgain) = getCellBounds(app, r, c)
    y1 -= app.cellSize
    app.canvasWalls.append((x0, y0, x1, y1))
                    
def drawWallsTogether(app, canvas):
    drawBorderWalls(app, canvas)
    for chunk in app.canvasWalls:
        canvas.create_rectangle(chunk, fill=app.wallColor, outline=app.wallColor)

def drawPills(app, canvas):
    canvas.create_image(app.width/2, app.height/2, image=ImageTk.PhotoImage(app.image))
    
def drawEntities(app, canvas):

    for bod in app.playerList:
        cx, cy = bod.x, bod.y
        r = 0.9 * app.cellSize / 2
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=bod.color)

def drawHUD(app, canvas):
    if app.classic:
        drawClassic(app, canvas)
    elif app.revenge:
        drawRevenge(app, canvas)
    drawInstructions(app, canvas)
    x1 = 2*app.margin + app.cols*app.cellSize
    w, h = app.width, app.height
    y1 = h-80
    x2 = w-20
    y2 = h-app.margin
    canvas.create_rectangle(x1, y1, x2, y2, fill='tan')
    canvas.create_text((x1+x2)/2, (y1+y2)/2, text='Home', fill='white', font='fixedsys 20')

def drawClassic(app, canvas):
    if app.pScore < 0:  tScore = 0
    else:   tScore = app.pScore
    boardWidth = 2 * app.margin + app.cellSize * app.cols
    scoreH = app.margin + 10
    dotH = scoreH * 2
    levelH = scoreH * 3
    livesH = scoreH * 4
    canvas.create_text(boardWidth, scoreH, text=f'Score: {tScore}', font='fixedsys 18 bold', anchor='nw', fill='white')
    canvas.create_text(boardWidth, dotH, text=f'Dots Left: {app.dotCount + app.powerCount}',
    anchor='nw', fill='#FAE100', font='fixedsys 18 bold')
    canvas.create_text(boardWidth, levelH, text=f'Level: {app.level}', font='fixedsys 18 bold', anchor='nw', fill='yellow')
    canvas.create_text(boardWidth, livesH, text=f'Lives: {app.lives}', font='fixedsys 18 bold', anchor='nw', fill='light green')

def drawRevenge(app, canvas):
    tScore = app.gScore
    boardWidth = 2 * app.margin + app.cellSize * app.cols
    scoreH = app.margin + 10
    levelH = scoreH * 2
    livesH = scoreH * 3
    ghostH = scoreH * 4
    canvas.create_text(boardWidth, scoreH, text=f'Score: {tScore}', font='fixedsys 18 bold', anchor='nw', fill='white')
    #canvas.create_text(boardWidth, ghostH, text=f'Ghosts Remaining: {app.gRem}',
    #font='fixedsys 17 bold', anchor='nw', fill='light green') ### will have to add this another time
    canvas.create_text(boardWidth, levelH, text=f'Level: {app.level}', font='fixedsys 18 bold', anchor='nw', fill='yellow')
    canvas.create_text(boardWidth, livesH, text=f'Pac-man Lives: {app.lives}', font='fixedsys 18 bold', anchor='nw', fill='red')

def drawGameOver(app, canvas):
    w, h = app.width, app.height
    canvas.create_rectangle(0, 0, w, h, fill='black')
    canvas.create_text(w/2, h/2, text='Game Over', font='fixedsys 50 bold', fill='red')
    if app.classic: tScore = app.pScore
    else:   tScore = app.gScore
    canvas.create_text(w/2, 2*h/3, text=f'Score: {tScore}', font='fixedsys 40 bold', fill='white')
    canvas.create_text(w/2, 2.5*h/3, text='Click anywhere to return home', font='fixedsys 25', fill='tan')

def classicInstructions(app, canvas):
    iColor = '#C2D1A3'
    xShift = 2 * app.margin + app.cellSize * app.cols
    yShift = app.margin + app.cellSize * (5 + app.rows // 2)
    dy = app.cellSize
    canvas.create_text(xShift, yShift+dy, text=
    '''Eat all the dots to reach 
the next level! Stay away 
from red, blue, pink, and 
orange ghosts. Power-up 
pellets turn the ghosts 
purple and allow you to 
eat them until their color 
changes back.''', fill=iColor, anchor='nw', font='fixedsys 16')

def revengeInstructions(app, canvas):
    iColor = '#C2D1A3'
    fixed = 'fixedsys 16'
    xShift = 2 * app.margin + app.cellSize * app.cols
    yShift = app.margin + app.cellSize * (5 + app.rows // 2)
    dy = app.cellSize
    canvas.create_text(xShift, yShift+dy, text=
    '''Catch pac-man to take his
lives away before he eats 
all your dots! But avoid 
being eaten while your 
ghosts are purple.

Note: Ghosts can never
willingly turn backwards.''', fill=iColor, anchor='nw', font=fixed)
    canvas.create_text(xShift, yShift-9*dy, fill='sky blue', 
    text='- Change ghost with numbers:', anchor='nw', font=fixed)

    canvas.create_text(xShift, yShift-7*dy, fill='red', 
    text='1 - Red (Blinky)', anchor='nw', font=fixed)
    canvas.create_text(xShift, yShift-6*dy, fill='blue', 
    text='2 - Blue (Inky)', anchor='nw', font=fixed)
    canvas.create_text(xShift, yShift-5*dy, fill='pink', 
    text='3 - Pink (Pinky)', anchor='nw', font=fixed)
    canvas.create_text(xShift, yShift-4*dy, fill='orange', 
    text='4 - Orange (Clyde)', anchor='nw', font=fixed)
    canvas.create_text(xShift, yShift-3*dy, fill='#FAD232', 
    text='0 - AFK mode (Default)', anchor='nw', font=fixed)

def drawInstructions(app, canvas):
    if not app.instructions:    return
    iColor = '#C2D1A3'
    xShift = 2 * app.margin + app.cellSize * app.cols
    yShift = app.margin + app.cellSize * (5 + app.rows // 2)
    dy = app.cellSize
    canvas.create_text(xShift, yShift, text='Instructions:', fill=iColor, anchor='nw', font='fixedsys 16')
    if app.classic: classicInstructions(app, canvas)
    elif app.revenge:   revengeInstructions(app, canvas)

    canvas.create_text(xShift, yShift-13*dy, text=
    'Controls:', fill='sky blue', anchor='nw', font='fixedsys 16')
    canvas.create_text(xShift, yShift-12*dy, text=
    '- Move with the arrow keys', fill='sky blue', anchor='nw', font='fixedsys 16')
    canvas.create_text(xShift, yShift-11*dy, text=
    '- Toggle pause with "p"', fill='sky blue', anchor='nw', font='fixedsys 16')
    canvas.create_text(xShift, yShift-10*dy, text=
    '- Toggle rules with "i"', fill='sky blue', anchor='nw', font='fixedsys 16')

def redrawAll(app, canvas):
    if app.splashScreen:
        drawSplashScreen(app, canvas)
    elif app.gameOver:
        drawGameOver(app, canvas)
    else:
        drawPills(app, canvas)
        drawWallsTogether(app, canvas)
        drawEntities(app, canvas)
        drawRoundStart(app, canvas)
        drawHUD(app, canvas)

######################
# Splash Screen and UI
######################
def drawSplashScreen(app, canvas):
    #canvas.create_rectangle(0, 0, app.width, app.height, fill='#EC1C24')
    canvas.create_rectangle(0, 0, app.width, app.height, fill='#B83DBA')
    canvas.create_image(app.width/2, app.height/3, image=ImageTk.PhotoImage(app.splashImage))
    canvas.create_oval(30, 460, 480, 600, fill='royal blue')
    canvas.create_oval(500, 460, 950, 600, fill='gold')
    
    canvas.create_text(app.width/3 - 90, 2*app.height/3, text='CLASSIC', font='fixedsys 60 bold', fill='violet')
    canvas.create_text(2*app.width/3 + 50, 2*app.height/3, text='REVENGE', font='fixedsys 60 bold', fill='white')
    canvas.create_text(app.width/2, 5*app.height/6, text='Select a game mode to begin!', font="fixedsys 30 italic", fill='#94DEB4')
    
def drawRoundStart(app, canvas):
    if app.roundStart:
        dy = app.cellSize
        x1, y1, no, nono = getCellBounds(app, app.gR1, app.gC1)
        no, nono, x2, y2 = getCellBounds(app, app.gR2, app.gC2)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        canvas.create_rectangle(x1, y1, x2, y2, fill='#426890', outline=app.wallColor)
        canvas.create_text(cx, cy-dy, text=f'Round {app.level}', font='fixedsys 14', fill='white')
        canvas.create_text(cx, cy+dy, text='Press "Space" to begin', font='fixedsys 12', fill='lime')
        canvas.create_text(cx, cy+2*dy, text='Or change map with "r"', font='fixedsys 12', fill='orange')

########################
# Ghost AI functionality
########################
def pacCell(app):
    # find the cell that pac-man is in
        return getCell(app, app.pac.x, app.pac.y)

def ghostCells(app):
    bR, bY = getCell(app, app.blinky.x, app.blinky.y)
    iR, iY = getCell(app, app.inky.x, app.inky.y)
    pR, pY = getCell(app, app.pinky.x, app.pinky.y)
    cR, cY = getCell(app, app.clyde.x, app.clyde.y)
    return ((bR, bY), (iR, iY), (pR, pY), (cR, cY))

'''ideas for ghost AI from here:
https://www.youtube.com/watch?v=ataGotQ7ir8&ab_channel=RetroGameMechanicsExplained
'''

class Ghost(Runner):
    def healedUp(self, app):
        gRow, gCol = getCell(app, self.x, self.y)
        if app.board[gRow][gCol] != False and self.centered(app) and self.color == self.originalColor:
            self.speed = app.gSpeed

    def AI(self, app):
        pRow, pCol = pacCell(app)
        gRow, gCol = getCell(app, self.x, self.y)
        if self.color == 'red' or \
            (self.color == 'orange' \
                # orange ghost has to be at least 8 tiles away to chase pacman
                and boardDistance(gRow, gCol, pRow, pCol) > 64):
            self.chase(app, pRow, pCol)
        
        elif self.color == 'orange' and boardDistance(gRow, gCol, pRow, pCol) <= 64:
            self.scatter(app)
        
        elif self.color == 'blue':
            if app.pac.cDir == None:    return
            cRow, cCol = app.pac.cDir[1], app.pac.cDir[0]
            halfRow, halfCol = pRow + 2 * cRow, pCol + 2 * cCol
            rRow, rCol = getCell(app, app.blinky.x, app.blinky.y)
            dRow, dCol = halfRow - rRow, halfCol - rCol
            self.chase(app, halfRow + dRow, halfCol + dCol)
        
        elif self.color == 'pink':
            if app.pac.cDir == None:    return
            cRow, cCol = app.pac.cDir[1], app.pac.cDir[0]
            self.chase(app, pRow + 4 * cRow, pCol + 4 * cCol)

    
    # function which spreads out the ghosts
    def scatter(self, app):
        # scatter corners for each ghost
        bLRow, bLCol = app.rows - 2, 1                  # orange
        bRRow, bRCol = app.rows - 2, app.cols - 2       # pink
        tLRow, tLCol = 1, 1                             # blue
        tRRow, tRCol = 1, app.cols - 2                  # red

        if self.color == 'orange':
            self.chase(app, bLRow, bLCol)
        elif self.color == 'red':
            self.chase(app, tRRow, tRCol)
        elif self.color == 'pink':
            self.chase(app, tLRow, tLCol)
        elif self.color == 'blue':
            self.chase(app, bRRow, bRCol)

    def anxious(self, app):
        if app.classic:
            interval = 11 - app.level
        elif app.revenge:
            interval = 9 + app.level
        
        elif interval > 15: interval = 15
        
        dist = 10000
        if interval > 0:
            self.speed = app.slow
            gRow, gCol = getCell(app, self.x, self.y)
            chgDir = self.tDir
            if self.centered(app):
                if app.board[gRow][gCol] == False:  return
                legalDirs = findLegalDirs(app, gRow, gCol)
                trueDirs = []
                for (dCol, dRow) in legalDirs:
                    if not self.isReverse(dRow, dCol):  trueDirs.append((dCol, dRow))
                if len(trueDirs) != 0:
                    self.tDir = random.choice(trueDirs)
        if time.time() > app.anxiousTime + interval:    
            app.anxious = False
            originalColors(app, False)
            stayOutOfWalls(app)

    def runHome(self, app):

        gRow, gCol = getCell(app, self.x, self.y)
        # somewhere on the board outside the house
        if self.color == 'white' and (gRow, gCol) != (11, 13) and app.board[gRow][gCol] != False:
            if self.centered(app): self.speed = app.cellSize / 3
            procedure, cDist = pacmanToGhost(gRow, gCol, 11, 13, (0, 0), \
                            app.graphMap, app.board, None, True, True)
            chaseThePathGhost(app, procedure, self)
        # entering the house
        elif self.color == 'white' and (gRow, gCol) == (11, 13):
            self.tDir = (0, 1)
        # leaving the house
        elif self.color == 'white' and gRow == 15 and self.centered(app):
            self.color = self.originalColor
            self.tDir = (0, -1)
            self.speed = app.slow
        elif self.color == self.originalColor and gRow == 11 and self.centered(app):
            self.speed = app.gSpeed

def stayOutOfWalls(app):
    for player in app.playerList:
        player.keepPlayerInBounds(app)
        if player.cDir != None:
            player.keepPlayerOutofWall(app)

def originalColors(app, home=True):
    for player in app.playerList:
        if home:
            player.color = player.originalColor
        elif player.color != 'white':
            player.color = player.originalColor

def originalSpeeds(app):
    app.pac.speed = app.pSpeed
    for player in app.playerList[1:]:
        if player.centered(app) and player.speed < app.gSpeed:
            player.speed = app.gSpeed

def boardDistance(row1, col1, row2, col2):
    return (row1-row2)**2 + (col1-col2)**2
    


def ghostSequence(app):
    ((bR, bY), (iR, iY), (pR, pY), (cR, cY)) = ghostCells(app)
    mult = -1
    for ghost in app.playerList[1:]:
        mult += 1
        gRow, gCol = getCell(app, ghost.x, ghost.y)
        if app.board[gRow][gCol] == False and time.time() > app.ghostTimer + mult * app.ghostDelay and ghost.color != 'white':
            ghost.speed = app.slow
            if gCol == 12:  ghost.tDir = [1, 0]
            elif gCol == 15:    ghost.tDir = [-1, 0]
            else:   ghost.tDir = [0, -1]
            ghost.moving(app)
            ghost.keepPlayerInBounds(app)
            if ghost.centered(app):
                ghost.speed = app.gSpeed
    
    # check clydes cell at the end when done
    if app.board[cR][cY] == None and app.clyde.centered(app):   app.ghostSequence = False
    # moving functionality
#####################
# Level Functionality
#####################
def gameOver(app):
    if app.classic and app.lives == 0 and app.pauseStarted:
        app.gameOver = True
    elif app.revenge and app.dotCount == 0 and app.powerCount == 0 and app.pauseStarted:
        app.gameOver = True
''' Classic Game Mode '''

def nextRound(app):
    if app.classic and app.dotCount == 0 and app.powerCount == 0: 
        app.level += 1 
        if app.level == 5:  app.gSpeed = app.pSpeed  
        app.ghostDelay -= 1
        roundSetUp(app)
        
    elif app.revenge and app.lives == 0:
        app.lives = 3
        app.level += 1
        app.ghostDelay -= 1
        updatePacDifficulty(app)
        roundSetUp(app)
    
    if app.ghostDelay < 3:  app.ghostDelay = 3

def roundSetUp(app):
    generateMap(app)
    condenseWalls(app)
    developImage(app)
    resetPlayers(app)
    app.pauseStarted = False
    app.roundStart = True
    originalColors(app)
    ## change speeds later as the levels progress
    originalSpeeds(app)
    app.scatter = True
    app.chase = False
    app.chaseCount = app.scatterCount = app.stateFlips = 0
############
# Pac-man AI
############
def updatePacDifficulty(app):
    if app.level >= 2:  app.lives += 1
    if app.level % 5 == 0:
        app.pFactor -= 1
        if app.pFactor < 3: app.pFactor = 3
        app.pSpeed = app.cellSize / app.pFactor

def largestSeparation(app, gRow, gCol, pRow, pCol):
    possibilities = app.pac.validDirs(app, gRow, gCol, pRow, pCol)
    maxDir, maxVal = possibilities[0][0], possibilities[0][1]
    for (bigDir, bigVal) in possibilities:
        if bigVal > maxVal:
            maxDir = bigDir
    app.pac.tDir = app.dirs[maxDir]

def findLegalDirs(app, pRow, pCol):
    legalDirs = []
    for direction in app.dirs:
        (dCol, dRow) = app.dirs[direction]
        if not app.pac.centered(app) and app.pac.isPerpendicular(app, (dCol, dRow)):
            continue
        else:
            nRow, nCol = pRow + dRow, pCol + dCol
            if app.board[nRow][nCol] == None or notOnBoard(nRow, nCol, app.board):
                legalDirs.append((dCol, dRow))
    return legalDirs

def nextStep(row, col, dRow, dCol):
    nRow, nCol = row + dRow, col + dCol
    return nRow, nCol

# close quarters run away mechanism
def identifyThreats(app):
    (pRow, pCol) = pacCell(app)
    legalDirs = findLegalDirs(app, pRow, pCol)
    totalDistances = [0] * len(legalDirs)
    minProcedureSize, minProcedure = 100, [(0, 0)] * 100
    i = -1
    for direction in legalDirs:
        i += 1
        for ghost in app.playerList[1:]:
            gRow, gCol = getCell(app, ghost.x, ghost.y)
            if app.board[gRow][gCol] == False:  continue
            # ignore ghost moving in and out of house
            elif ghost.cDir in [(0, -1), (0, 1)] and (gRow and gCol in (13, 14)): continue
            else:
            # obtain path finding procedure and direct distance for each ghost
                procedure, cDist = pacmanToGhost(pRow, pCol, gRow, gCol, ghost.cDir, \
                    app.graphMap, app.board, None, True, True)

                if cDist < minProcedureSize:
                    minProcedure, minProcedureSize = procedure, cDist
                rDist = distance(app.pac.x, app.pac.y, ghost.x, ghost.y)
                if rDist == 0:   rDist = 0.2
                weight = 1 / (rDist ** 4)
                fRow, fCol = nextStep(pRow, pCol, direction[1], direction[0])
                fX = app.margin + app.cellSize * (fCol + 0.5)
                fY = app.margin + app.cellSize * (fRow + 0.5)
                totalDistances[i] += weight * distance(ghost.x, ghost.y, fX, fY)

    maxI = totalDistances.index(max(totalDistances))
    if app.anxious:
        canRun = runToGhost(app)
        if canRun == False:
            collectDots(app)
        elif canRun == True:
            app.pac.tDir = legalDirs[maxI]
        return

    if minProcedureSize >= 5 or app.anxious:
        collectDots(app)
        return
    
    app.pac.tDir = legalDirs[maxI]
    
# incentive function for pac man to eat dots    
def collectDots(app):
    (pRow, pCol) = pacCell(app)
    nRow, nCol = nextStep(pRow, pCol, app.pac.cDir[1], app.pac.cDir[0])

    if app.pacDots[nRow][nCol] == True: return
    if app.dotCount > 0:
        minDist = 10**20
        minTile = (1, 1)
        rows = len(app.pacDots)
        cols = len(app.pacDots[0])
        for row in range(rows):
            for col in range(cols):
                if app.pacDots[row][col] == True:
                    pelX = (col + 0.5) * app.cellSize + app.margin
                    pelY = (row + 0.5) * app.cellSize + app.margin
                    dist = distance(app.pac.x, app.pac.y, pelX, pelY)
                    if dist < minDist:
                        minDist = dist
                        minTile = (row, col)
        procedure, cDist = pacmanToGhost(pRow, pCol, minTile[0], minTile[1], (0, 0), \
                            app.graphMap, app.board, None, True, True)
        chaseThePath(app, procedure)
    
    elif app.powerCount > 0:
        runToPowerDot(app)

def runToPowerDot(app):
    pRow, pCol = pacCell(app)
    rows, cols = app.rows, app.cols
    powerList = [(1, 1), (1, cols-2), (rows-2, 1), (rows-2, cols-2)]
    for dotR, dotC in powerList:
        if app.pacDots[dotR][dotC] == 'power':
            procedure, cDist = pacmanToGhost(pRow, pCol, dotR, dotC, (0, 0), \
                        app.graphMap, app.board, None, True, True)
            chaseThePath(app, procedure)

# catch ghosts while power up is active
def runToGhost(app):
    pRow, pCol = pacCell(app)
    minDist = 10**20
    minTile = (1, 1)
    for ghost in app.playerList[1:]:
        gRow, gCol = getCell(app, ghost.x, ghost.y)
        if ghost.color == 'purple' and app.board[gRow][gCol] != False:
            dist = distance(app.pac.x, app.pac.y, ghost.x, ghost.y)
        elif ghost.color == ghost.originalColor and distance(app.pac.x, app.pac.y, ghost.x, ghost.y) < 3 * app.cellSize:
            # don't run into a non purple ghost to get to another purple ghost
            return True
        else:
            dist = 10**20
        
        if dist < minDist:  
            minDist = dist
            minTile = (gRow, gCol)
    if minDist < 10**19:
        #app.pac.chase(app, minTile[0], minTile[1])
        procedure, cDist = pacmanToGhost(pRow, pCol, minTile[0], minTile[1], (0, 0), \
                        app.graphMap, app.board, None, True, True)
        chaseThePath(app, procedure)
    else:
        return False
    
def chaseThePath(app, procedure):
    if len(procedure) == 1:
        app.procedure = None
        return
    pRow, pCol = pacCell(app)
    p1, p2 = procedure[1][0], procedure[1][1]
       
    dCol, dRow = collapseToUnitVec(p2-pCol), collapseToUnitVec(p1-pRow)
    if app.pac.isPerpendicular(app, (dCol, dRow)):
        if not app.pac.centered(app):   return
    if len(procedure) > 1:
        if boardDistance(pRow, pCol, p1, p2) == 0:
            procedure.pop(0)  
    app.pac.tDir = (dCol, dRow) 

def chaseThePathGhost(app, procedure, ghost):
    if len(procedure) == 1:
        app.procedure = None
        return
    gRow, gCol = getCell(app, ghost.x, ghost.y)
    p1, p2 = procedure[1][0], procedure[1][1]
       
    dCol, dRow = collapseToUnitVec(p2-gCol), collapseToUnitVec(p1-gRow)
    if ghost.isPerpendicular(app, (dCol, dRow)):
        if not ghost.centered(app):   return
    if len(procedure) > 1:
        if boardDistance(gRow, gCol, p1, p2) == 0:
            procedure.pop(0)  
    ghost.tDir = (dCol, dRow) 

def collapseToUnitVec(vec):
    if vec < 0: vec = -1
    elif vec > 0: vec = 1
    return vec

# helper function for finding the nearest dot within bounds
def fixBounds(app, bounds):
    for i in range(len(bounds)):
        if i % 2 == 0:  
            bounds[i] -= 1
        else:
            bounds[i] += 1

        if i == 0 and bounds[i] < 0:    bounds[i] = 0
        elif i == 1 and bounds[i] >= app.rows:   bounds[i] = app.rows-1
        elif i == 2 and bounds[i] < 0:    bounds[i] = 0
        elif i == 3 and bounds[i] >= app.cols:    bounds[i] = app.cols-1
        
    return bounds

# returns the first found dot
def findClosestPellet(app, bounds):
    r1, r2, c1, c2 = bounds[0], bounds[1], bounds[2], bounds[3]
    for i in range(r1, r2 + 1):
        for j in range(c1, c2 + 1):
            if app.pacDots[i][j] == True:
                return i, j

    return (None, None)

runApp(width=1020, height=800)