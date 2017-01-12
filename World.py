__author__ = 'philippe'
from Tkinter import *
import sys
from PIL import Image
master = Tk()


#####################
# Lots of variables #
#####################

# The map image
plan = Image.open("finalfinalZelda.PNG")


# The colour of the platform blocks in rgb and hex
blocks = [
{'name': "background", 'rgb': (0, 64, 64), 'hex': "#004040", 'isWall': True}, 
{'name': "wall", 'rgb': (72, 164, 67), 'hex': "#48A443", 'isWall': True}, 
{'name': "space", 'rgb': (0, 0, 0), 'hex': "#000000", 'isWall': True}, 
{'name': "ground", 'rgb': (0, 96, 0), 'hex': "#006000", 'isWall': False}, 
{'name': "vines", 'rgb': (88, 201, 90), 'hex': "#58C95A", 'isWall': False}, 
{'name': "water", 'rgb': (0, 94, 197), 'hex': "#005EC5", 'isWall': False}, 
{'name': "poison", 'rgb': (89, 0, 140), 'hex': "#59008C", 'isWall': False},

{'name': "end", 'rgb': (0, 255, 0), 'hex': "#00FF00", 'isWall': False}]


triangle_size = 0.1
cell_score_min = -0.2
cell_score_max = 0.2
Width = 3
x = plan.size[0]
y = plan.size[1]

actions = ["up", "down", "left", "right"]

board = Canvas(master, width = x*Width, height = y*Width)

score = 3000
restart = False
ground_reward = -4
vine_reward = -8
water_reward = -12
poison_reward = -16

end = (72, 28)
end_reward = 3000

walls = []
for block in blocks:
    if block['isWall']:
	walls.append(block)

vines = []
waters = []
poisons = []


cell_scores = {}

scores = []

startPositions = [(128, 340), (29, 209), (249, 220)]
player = (128, 340)
currentStartPositionIndex = 0


def create_triangle(i, j, action):
    if action == actions[0]:
        return board.create_polygon((i+0.5-triangle_size)*Width, (j+triangle_size)*Width,
                                    (i+0.5+triangle_size)*Width, (j+triangle_size)*Width,
                                    (i+0.5)*Width, j*Width,
                                    fill="white", width=1)
    elif action == actions[1]:
        return board.create_polygon((i+0.5-triangle_size)*Width, (j+1-triangle_size)*Width,
                                    (i+0.5+triangle_size)*Width, (j+1-triangle_size)*Width,
                                    (i+0.5)*Width, (j+1)*Width,
                                    fill="white", width=1)
    elif action == actions[2]:
        return board.create_polygon((i+triangle_size)*Width, (j+0.5-triangle_size)*Width,
                                    (i+triangle_size)*Width, (j+0.5+triangle_size)*Width,
                                    i*Width, (j+0.5)*Width,
                                    fill="white", width=1)
    elif action == actions[3]:
        return board.create_polygon((i+1-triangle_size)*Width, (j+0.5-triangle_size)*Width,
                                    (i+1-triangle_size)*Width, (j+0.5+triangle_size)*Width,
                                    (i+1)*Width, (j+0.5)*Width,
                                    fill="white", width=1)



######################
# Initialize Dungeon #
######################
def initialize_dungeon():
    global dungeon, blocks
    dungeon = []
    for i in range(0, x):
        row = []
        for j in range(0, y):

	    currentBlockColour = plan.getpixel((i, j))
		
	    for block in blocks:
                if currentBlockColour == block['rgb']:
            	    row.append(block)
        dungeon.append(row)

initialize_dungeon()



def render_grid():
    global specials, walls, Width, player, blocks

    for row in range(0, len(dungeon)):
	for block in range(0, len(dungeon[row])):	
            board.create_rectangle(row*Width, block*Width, (row+1)*Width, (block+1)*Width, fill=dungeon[row][block]['hex'], width=1)
		        
	    if dungeon[row][block]['rgb'] == blocks[4]['rgb']:
		vines.append((row, block))
	    elif dungeon[row][block]['rgb'] == blocks[5]['rgb']:
		waters.append((row, block))
	    elif dungeon[row][block]['rgb'] == blocks[6]['rgb']:
		poisons.append((row, block))

            
            temp = {}
#            for action in actions:
#                temp[action] = create_triangle(i, j, action)
#            cell_scores[(i,j)] = temp
#    for (i, j, c, w) in specials:
#       board.create_rectangle(i*Width, j*Width, (i+1)*Width, (j+1)*Width, fill=c, width=1)
#    for wall in walls:
#        board.create_rectangle(i*Width, j*Width, (i+1)*Width, (j+1)*Width, fill="black", width=1)

render_grid()




def set_cell_score(state, action, val):
    global cell_score_min, cell_score_max
#    triangle = cell_scores[state][action]
    green_dec = int(min(255, max(0, (val - cell_score_min) * 255.0 / (cell_score_max - cell_score_min))))
    green = hex(green_dec)[2:]
    red = hex(255-green_dec)[2:]
    if len(red) == 1:
        red += "0"
    if len(green) == 1:
        green += "0"
    color = "#" + red + green + "00"
#    board.itemconfigure(triangle, fill=color)


def try_move(dx, dy):
    global player, x, y, score, walk_reward, me, restart, end, scores, startPositions, currentStartPositionIndex
    if restart == True:
        restart_game()
    new_x = player[0] + dx
    new_y = player[1] + dy
    score += ground_reward
    if (new_x >= 0) and (new_x < x) and (new_y >= 0) and (new_y < y) and not (dungeon[new_x][new_y] in walls):
        board.coords(me, new_x*Width+Width*2/10, new_y*Width+Width*2/10, new_x*Width+Width*8/10, new_y*Width+Width*8/10)
        player = (new_x, new_y)

        if new_x == end[0] and new_y == end[1]:
            score -= ground_reward
            score += end_reward
            if score > 0:
                print "Success! score: ", score
            else:
                print "Fail! score: ", score
	    
	    scores.append(score)

	    if len(scores) >= 3:



	    	lastThreeScores = scores[len(scores) - 3:]

	    	if lastThreeScores[0] == lastThreeScores[1] and lastThreeScores[0] == lastThreeScores[2]:
		    print "The agent has reached a state of convergence around the optimal path at episode " + str(len(scores)) + " with a score of " + str(score)
		    currentStartPositionIndex += 1
	    
            	    resultsFile = open("results.txt", "a")
	            resultsFile.write("The agent " + str(currentStartPositionIndex) + " has reached a state of convergence around the optimal path at episode " + str(len(scores)) + " with a score of " + str(score) + "\n")
	    	    resultsFile.close()

		    scores = []
		
		    if currentStartPositionIndex > 2:
		    	sys.exit()


	    
            restart = True
            return




	for vine in vines:
	    if new_x == vine[0] and new_y == vine[1]:
                score -= ground_reward
                score += vine_reward

	for water in waters:
	    if new_x == water[0] and new_y == water[1]:
                score -= ground_reward
                score += vine_reward

	for poison in poisons:
	    if new_x == poison[0] and new_y == poison[1]:
                score -= ground_reward
                score += vine_reward

		

	
	


def call_up(event):
    try_move(0, -1)


def call_down(event):
    try_move(0, 1)


def call_left(event):
    try_move(-1, 0)


def call_right(event):
    try_move(1, 0)


def restart_game():
    global player, score, me, restart
    player = startPositions[currentStartPositionIndex]
    score = 100
    initialize_dungeon()
    restart = False
    board.coords(me, player[0]*Width+Width*2/10, player[1]*Width+Width*2/10, player[0]*Width+Width*8/10, player[1]*Width+Width*8/10)

def has_restarted():
    return restart

master.bind("<Up>", call_up)
master.bind("<Down>", call_down)
master.bind("<Right>", call_right)
master.bind("<Left>", call_left)

me = board.create_rectangle(player[0]*Width, player[1]*Width,
                            player[0]*Width, player[1]*Width, fill="white", width=1, tag="me")

board.grid(row=0, column=0)


def start_game():
	master.mainloop()
