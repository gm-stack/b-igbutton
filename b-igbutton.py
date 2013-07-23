import pygame, os, random, shutil

# /b/igbutton.py - collaborative image sorting of large folders
# gm_stack, gm@stackunderflow.com

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
PLAYERS = 4
PLAYERBUTTONS = 4
TEXTSIZE = 24

pygame.init()
pygame.joystick.init()

joysticks = []
jscount = pygame.joystick.get_count()

if jscount == 0:
	print "There are no joysticks attached to your computer.  Joystick support disabled."
else:
	if jscount > 4:
		jscount = 4
	for x in range(jscount):
		thisjs = pygame.joystick.Joystick(x)
		#if "Microsoft X-Box 360 Big Button IR" in thisjs.get_name():
		#	# this is a controller we want to use
		joysticks.append(thisjs)
		print "- Using joystick %s: %s" % (x, thisjs.get_name())
		thisjs.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
running = 1

font = pygame.font.Font(None, TEXTSIZE)

fileList = os.listdir("incoming")
random.shuffle(fileList)

def trymkdir(path):
	try:
		os.mkdir(path)
	except OSError:
		pass

trymkdir("outgoing/")
trymkdir("outgoing/images")
trymkdir("outgoing/tags")
categoryList = open("categories.txt").read().split("\n")
for category in categoryList:
	trymkdir("outgoing/tags/" + category)

total = len(fileList)
current = -1
filename = fileList[current]
imageData = None

playercategories = []
categoriesselected = []
categoriesUsed = 0

colours = [(0,255,0),(255,0,0),(0,0,255),(255,255,0)]
darkcolours = [(0,64,0),(64,0,0),(0,0,32),(32,32,0)]


def transprect(x,y,w,h,r,g,b,a):
	rectsurf = pygame.Surface((w,h))
	rectsurf.fill((r,g,b))
	rectsurf.set_alpha(a)
	screen.blit(rectsurf,(x,y))
	

def drawPlayerCategories():
	for player in xrange(PLAYERS):
		xpos = (200*player)+20
		transprect(xpos-10,50,200,120,128,128,128,230)
		#pygame.draw.rect(screen,(128,128,128,128),(xpos-10,50,220,120))
		text = font.render("Player %i Categories:" % (player + 1) ,1,colours[player])
		screen.blit(text,(xpos,60))
		
		ypos = 0
		for catnum in xrange(PLAYERBUTTONS):
			category = playercategories[player][catnum]
			selected = categoriesselected[player][catnum]
			colour = colours[catnum] if selected else darkcolours[catnum]
			text = font.render(category,1,colour)
			screen.blit(text,(xpos,80+ypos))
			ypos += 20

def redrawScreen():
	screen.fill((0,0,0))
	text = font.render("/b/igbutton.py 0.01",1,(255,255,255))
	screen.blit(text, (5,0))
	
	text = font.render("Image %i of %i: %s" % (current,total,filename),1,(255,255,255) )
	screen.blit(text, (5,20))
	
	tagsLeft = (len(categoryList) - categoriesUsed)
	text = font.render("%i tags left" % tagsLeft,1,(255,255,255) if tagsLeft > 0 else (255,0,0) )
	screen.blit(text, (400,20))
	
	if imageData != None:
		screen.blit(imageData, (0,40))
	else:
		txt = "Unable to display %s" % filename
		size = font.size(txt)[0]
		text = font.render(txt,1,(255,255,255))
		screen.blit(text, (512-(size/2),360))
	
	if len(playercategories):
		drawPlayerCategories()
	
	pygame.display.flip()

def loadImage(number):
	global imageData
	print "loading %s" % filename
	try:
		imageData = pygame.image.load("incoming/%s" % filename).convert()
		imageData = pygame.transform.scale(imageData, (SCREEN_WIDTH, SCREEN_HEIGHT - 40))
	except:
		imageData = None

def processFile():
	tags = getPlayerSelections()
	print "Tags for image %s were %s" % (filename,tags)
	shutil.move("incoming/"+filename,"outgoing/images/"+filename)
	for tag in tags:
		os.symlink("../../images/"+filename,"outgoing/tags/%s/%s" % (tag,filename))

def nextImage():
	global playercategories
	global current
	global filename
	global categoryList
	global categoriesUsed
	if ((len(categoryList) - categoriesUsed) > 0) and (current != -1):
		print "Not all tags done!"
		return
	if len(playercategories):
		processFile()
	current += 1
	filename = fileList[current]
	global categoriesselected
	categoriesUsed = PLAYERS*PLAYERBUTTONS
	random.shuffle(categoryList)
	categories = categoryList[:PLAYERS*PLAYERBUTTONS]
	playercategories = []
	categoriesselected = []
	for player in xrange(PLAYERS):
		playercategories.append(categories[player*PLAYERBUTTONS:(player+1)*PLAYERBUTTONS])
		categoriesselected.append([False]*PLAYERBUTTONS)
	loadImage(current)

def togglePlayerCategory(player,category):
	player = player - 1
	category = category - 1
	global categoriesselected
	categoriesselected[player][category] = not categoriesselected[player][category]

def rejectCategories(player):
	global categoryList
	global playercategories
	global categoriesUsed
	global categoriesselected
	for catnum in xrange(PLAYERBUTTONS):
		if not categoriesselected[player-1][catnum]:
			if len(categoryList) - categoriesUsed > 0:
				playercategories[player-1][catnum] = categoryList[categoriesUsed]
				categoriesUsed += 1

def getPlayerSelections():
	selected = []
	for player in xrange(PLAYERS):
		for catnum in xrange(PLAYERBUTTONS):
			if categoriesselected[player][catnum]:
				selected.append(playercategories[player][catnum])
	return selected

nextImage()
redrawScreen()

keys = {'1': {'func': togglePlayerCategory, 'args': (1,1)},
		'\'':{'func': togglePlayerCategory, 'args': (1,2)},
		'a': {'func': togglePlayerCategory, 'args': (1,3)},
		';': {'func': togglePlayerCategory, 'args': (1,4)},
		'2': {'func': rejectCategories,		'args': (1,)},
		
		'4': {'func': togglePlayerCategory, 'args': (2,1)},
		'p': {'func': togglePlayerCategory, 'args': (2,2)},
		'u': {'func': togglePlayerCategory, 'args': (2,3)},
		'k': {'func': togglePlayerCategory, 'args': (2,4)},
		'5': {'func': rejectCategories,		'args': (2,)},
		
		'7': {'func': togglePlayerCategory, 'args': (3,1)},
		'g': {'func': togglePlayerCategory, 'args': (3,2)},
		'h': {'func': togglePlayerCategory, 'args': (3,3)},
		'm': {'func': togglePlayerCategory, 'args': (3,4)},
		'8': {'func': rejectCategories,		'args': (3,)},
		
		'0': {'func': togglePlayerCategory, 'args': (4,1)},
		'l': {'func': togglePlayerCategory, 'args': (4,2)},
		's': {'func': togglePlayerCategory, 'args': (4,3)},
		'z': {'func': togglePlayerCategory, 'args': (4,4)},
		'[': {'func': rejectCategories,		'args': (4,)},
}

while running:
	event = pygame.event.wait()
	#print pygame.event.event_name(event.type)
	
	if event.type == pygame.QUIT:
		running = 0
	if event.type == pygame.KEYDOWN:
		if event.unicode == " ":
			nextImage()
			redrawScreen()
		if event.unicode in keys:
			func = keys[event.unicode]['func']
			args = keys[event.unicode]['args']
			func(*args)
			redrawScreen()
	
	if event.type == pygame.JOYBUTTONDOWN:
		if event.button == 6:
			nextImage()
		elif event.button == 5:
			rejectCategories(event.joy + 1)
		elif event.button < 4:
			togglePlayerCategory(event.joy + 1, event.button + 1)
			
		redrawScreen()
		
