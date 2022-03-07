Project Title:	Pac-man Remastered
User Note: Run pac-man_revenge_v1.2.exe file to play game without running scripts in python

Description:	This project is my variant of a sequel to the original Pac-man by Namco. Traditionally, the user would 
be able to control a yellow dot (named pac-man) and move within the walls of a maze, all while collecting points and avoiding
4 ghosts with varying chasing algorithms. This classic mode will still remain present, with the addition of anti-pacman or
revenge mode. Just as it sounds, the user has the option to control all 4 ghosts instead of a single pac-man. The objective of revenge
mode is to strategically use the ghosts to put a stop to pac-man before he collects all of the pellets in the maze.

Files:
- pac-man_revenge_v1.2.exe (main executable to be run)
- pac-man_revenge_v1.2.py (main file to be run)
- mapGen.py (map generation file)
- graphAndNodes.py (pathfinding algorithm for pacman and ghost AI)
- cmu_112_graphics.py (graphics framework)
Image(s):	pacmanSplash.png, pacman_ghosts.png, anxiousGhost.png

Updates from version 1.1:
High Quality sprites for pacman and the ghosts
- Pac-man chops while running through the maze
- Ghosts are no longer circles, they have eyes that look in the direction of travel
- When ghosts are scared they have their own improved scared sprite as well
- Eaten ghosts turn into eyes that run back to the ghost house

Two ways to run the game:
1. Either run the pac-man_revenge_v1.2.exe directly
2. Or download the "game" folder directory and execute pac-man_revenge_v1.2.py in a python3 interpreter. 
Note: If using option 2, make sure to have all python source code and .png files in the same directory.

This project requires the PIL and requests libraries in order to run the graphics framework and display PIL images.
All other imported libraries are standard python in-built libraries.

In-game short-cuts:
In classic mode, the game checks for when the user has 0 dots remaining in order to advance to the next level.
Pressing the '-' key should reduce the dot count by 100. It reduces more then 100 when the user has < 200 dots, however the functionality 
of cheating to the next level still works.
To reach the game over screen in classic, reduce pac-mans lives by taking damage or pressing 'M'.
Conversely in revenge mode, the next level is triggered by losing lives and the game over screen is triggered by 0 dots remaining.
The same cheatcodes still apply, but in reverse order of course.

Pressing 'r' at the beginning of a round can change the map. Pressing 'c' will change map colors.

Note: I recommend using a computer that is plugged in and is relatively fast. 

Other than that hope you enjoy testing my game!
