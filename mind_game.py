import pygame,sys
from pygame.locals import *
import random


FPS = 30
WINDOWWIDTH = 680
WINDOWHEIGHT = 420
REVEALSPEED = 8
BOXSIZE = 40
GAPSIZE = 10
BOARDWIDTH = 10
BOARDHEIGHT = 7

assert(BOARDWIDTH*BOARDHEIGHT)%2==0,''
YMARGIN =int((WINDOWHEIGHT-(BOARDHEIGHT*(BOXSIZE +GAPSIZE)))/2)
XMARGIN =int((WINDOWWIDTH-(BOARDWIDTH*(BOXSIZE +GAPSIZE)))/2)

GRAY= (100, 100, 100)
NAVYBLUE = ( 60, 60, 100)
WHITE= (255, 255, 255)
RED= (255,0,0)
GREEN= ( 0, 255,0)
BLUE= ( 0,0, 255)
YELLOW= (255, 255,0)
ORANGE= (255, 128,0)
PURPLE= (255,0, 255)
CYAN= ( 0, 255, 255)
BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE
DONUT = 'donut'
SQUARE  = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALLCOLORS = (RED,GREEN,BLUE,YELLOW,ORANGE,PURPLE,CYAN)
ALLSHAPES = (DONUT,SQUARE,DIAMOND,LINES,OVAL)
assert len(ALLCOLORS)*len(ALLSHAPES) *2>=BOARDWIDTH*BOARDHEIGHT," Board too big for the assets"

def main():
    global FPSCLOCK
    global DISPLAYSURF
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF =pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))

    mousex = 0
    mousey = 0
    pygame.display.set_caption("Smashy")

    mainboard = getRandomizedBoard()
    revealedBoxes = generateRevealBoxesData(False)

    firstSelection = None

    DISPLAYSURF.fill(BGCOLOR)
    startGameAnimation(mainboard)

    while True:
        mouseClicked = False
        DISPLAYSURF.fill(BGCOLOR) #drawing the window
        drawBoard(mainboard,revealedBoxes)

        for event in pygame.event.get():
            if event.type == quit or (event.type == KEYUP and event.key==K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                mousex,mousey = event.pos
            elif event.type == MOUSEBUTTONUP:
                mousex,mousey = event.pos
                mouseClicked = True

        boxx ,boxy = getBoxAtPixel(mousex,mousey)
        if boxx != None and boxy!=None:
            if not revealedBoxes[boxx][boxy]:
                drawHighlightedBox(boxx,boxy)
            if not revealedBoxes[boxx][boxy] and mouseClicked:
                revealedBoxesAnimation(mainboard,[(boxx,boxy)])
                revealedBoxes[boxx][boxy]=True

                if firstSelection ==None:
                    firstSelection = (boxx,boxy)
                else:   
                    icon1shape,icon1color = getShapeandColor(mainboard,firstSelection[0],firstSelection[1])
                    icon2shape,icon2color = getShapeandColor(mainboard,boxx,boxy)
                    if icon1shape != icon2shape or icon1color !=icon2color:
                        pygame.time.wait(1000)
                        coverBoxesAnimation(mainboard,(firstSelection[0],firstSelection[1]))
                        revealedBoxes[firstSelection[0]][firstSelection[1]]=False
                        revealedBoxes[boxx][boxy]
                    elif hasWon(revealedBoxes):
                        gameWonAnimation(mainboard)
                        pygame.time.wait(2000)

                        #reset the board
                        mainboard = getRandomizedBoard()    
                        revealedBoxes = generateRevealBoxesData(False)

                        #show the fully unrevealed board for a second
                        drawBoard(mainboard,revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        #Replay the start game animation.
                        startGameAnimation(mainboard)
                    firstSelection = None
        pygame.display.update()   
        FPSCLOCK.tick(FPS)

def generateRevealBoxesData(val):
    revealedBoxes = []
    for i in range(BOARDWIDTH):
        revealedBoxes.append([val]*BOARDHEIGHT)
    return revealedBoxes


def getRandomizedBoard():
    icons = []
    for color in ALLCOLORS:
        for shape in ALLSHAPES:
            icons.append((shape,color))
    random.shuffle(icons)
    numIconUsed = int(BOARDWIDTH*BOARDHEIGHT/2)
    icons = icons[:numIconUsed]*2
    random.shuffle(icons)

    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(icons[0])
            del icons[0]
        board.append(column)
    return board

def splitIntoGroupsOf(groupSize,theList):
    result = []
    for i in range(0,len(theList),groupSize):
        result.append(theList[i:i +groupSize])
    return result

def leftTopCoordsOfBox(boxx,boxy):
    left = boxx *(BOXSIZE + GAPSIZE) + XMARGIN
    top = boxy*(BOXSIZE + GAPSIZE) + YMARGIN
    return (left,top)

def getBoxAtPixel(x,y):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left,top = leftTopCoordsOfBox(boxx,boxy) 
            boxRect = pygame.Rect(left,top,BOXSIZE,BOXSIZE)
            if boxRect.collidepoint(x,y):
                return (boxx,boxy)
    return (None,None)

def drawIcon(shape,color,boxx,boxy):
    quarter = int(BOXSIZE*0.25)
    half = int(BOXSIZE * 0.25)
    left,top = leftTopCoordsOfBox(boxx,boxy)

    if shape ==DONUT:
        pygame.draw.circle(DISPLAYSURF,color,(left+half,top+half),half-5)
        pygame.draw.circle(DISPLAYSURF,BGCOLOR,(left+half,top+half),quarter-5)
    elif shape ==SQUARE:
        pygame.draw.rect(DISPLAYSURF,color,(left+quarter,top+quarter,BOXSIZE-half,BOXSIZE-half))
    elif shape==DIAMOND:
        pygame.draw.polygon(DISPLAYSURF,color,((left+half,top),(left+BOXSIZE-1,top+half),(left+half,top+BOXSIZE-1),(left,top +half))) 
    elif shape ==LINES:
        for i in range(0,BOXSIZE,4):                           
            pygame.draw.line(DISPLAYSURF,color,(left,top+i),(left+i,top))
            pygame.draw.line(DISPLAYSURF,color,(left+i,top+BOXSIZE-1),(left+BOXSIZE-1,top+i))
    elif shape == OVAL:
        pygame.draw.ellipse(DISPLAYSURF,color,(left,top+quarter,BOXSIZE,half))

def getShapeandColor(board,boxx,boxy):
    return board[boxx][boxy][0],board[boxx][boxy][1]

def drawBoxCovers(board,boxes,coverage):
    for box in boxes:
        left,top = leftTopCoordsOfBox(box[0],box[1])
        pygame.draw.rect(DISPLAYSURF,BGCOLOR,(left,top,BOXSIZE,BOXSIZE))
        shape,color = getShapeandColor(board,box[0],box[1])
        drawIcon(shape,color,box[0],box[1])
        if coverage>0:
            pygame.draw.rect(DISPLAYSURF,BOXCOLOR,(left,top,coverage,BOXSIZE))
    pygame.display.update()
    FPSCLOCK.tick(FPS)


def revealedBoxesAnimation(board,boxesToReveal):
    for coverage in range(BOXSIZE,(-REVEALSPEED)-1,-REVEALSPEED):
        drawBoxCovers(board,boxesToReveal,coverage)

def coverBoxesAnimation(board,boxesToCover):
    for coverage in range(0,BOXSIZE+REVEALSPEED,REVEALSPEED):
        drawBoxCovers(board,boxesToCover,coverage)

def drawBoard(board,revealed):
    for boxx in range(BOARDWIDTH):
        for boxy in range(BOARDHEIGHT):
            left,top = leftTopCoordsOfBox(boxx,boxy)
            if not revealed[boxx][boxy]:
                pygame.draw.rect(DISPLAYSURF,BOXCOLOR,(left,top,BOXSIZE,BOXSIZE))
            else:
                shape,color = getShapeandColor(board,boxx,boxy)
                drawIcon(shape,color,boxx,boxy)

def drawHighlightedBox(boxx,boxy):
    left,top =leftTopCoordsOfBox(boxx,boxy)
    pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5,BOXSIZE + 10, BOXSIZE + 10), 4)

def startGameAnimation(board):
    coveredBoxes = generateRevealBoxesData(False)
    boxes = []
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            boxes.append( (x, y) )
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)
    drawBoard(board, coveredBoxes)
    for boxGroup in boxGroups:
        revealedBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)

def gameWonAnimation(board):
    coverBoxes = generateRevealBoxesData(True)
    color1 = LIGHTBGCOLOR
    color2 = BGCOLOR

    for i in range(13):
        color1,color2 = color2,color1
        DISPLAYSURF.fill(color1)
        drawBoard(board,coverBoxes)
        pygame.display.update()
        pygame.time.wait(300)


def hasWon(revealedBoxes):
    for i in revealedBoxes:
        if False in i:        
            return False
    return True 

if __name__ =='__main__':
    main()
