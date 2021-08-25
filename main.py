import math
import random
import tkinter as tk
from tkinter import ttk

running = False
paused = False
wrapAroundFlag = True
regenerated = False

const_pattern_random10 = "Random 10%"
const_pattern_random20 = "Random 20%"
const_pattern_random30 = "Random 30%"
const_pattern_glider = "Glider"
const_pattern_gospers = "Gosper's Glider Gun"
const_pattern_acorn = "Acorn"
const_pattern_static_etc = "Statics, oscillators and spaceships"
const_pattern_diehard = "Die Hard"

startingPatternList = [ \
    const_pattern_random10, \
    const_pattern_random20, \
    const_pattern_random30, \
    const_pattern_gospers, \
    const_pattern_acorn, \
    const_pattern_static_etc \
]
selectedPatternName = ""
selectedPatternIndex = 0

constTimerInterval = 10
constGridSize = 192
constCellSize = 4
constCellSizeGrid = constCellSize # + 1
current_cells = []
display_living = []


class GameOfLifeApplication(ttk.Frame):

    def __init__(self, windowparent=None):
        global startingPatternList
        global selectedPatternName
        global selectedPatternIndex

        self.lifeFrame = ttk.Frame.__init__(self, windowparent, padding=(12, 3, 12, 3))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        self.runningText = tk.StringVar()
        self.runningText.set("Start")
        self.buttonStartStop = ttk.Button(self, textvariable=self.runningText, command=self.start_stop, width=16)

        self.wrapButtonValue = tk.IntVar()
        self.wrapButtonValue.set(1)
        self.buttonWrapOnOff = ttk.Checkbutton(self, text='Wraparound', command=self.wrap, var=self.wrapButtonValue,
                                               width=16)

        self.mondialLabel = ttk.Label(self, text="Conway's Game Of Life")
        self.buttonQuit = ttk.Button(self, text='Quit', command=self.end_it, width=16)
        self.buttonPause = ttk.Button(self, text='Pause', state="disabled", command=self.pause, width=16)

        self.patternChooser = ttk.Combobox(self, values=startingPatternList, width=16, state='readonly')
        self.patternChooser.set(startingPatternList[selectedPatternIndex])
        selectedPatternName = startingPatternList[selectedPatternIndex]

        self.cellcanvas = tk.Canvas(self, width=constGridSize * constCellSizeGrid,
                                    height=constGridSize * constCellSizeGrid, background='black')

        self.grid(column=0, row=0, sticky='N, W, E, S')
        for c in range(1, 6):
            self.columnconfigure(c, weight=1)
        for r in range(1, 4):
            self.rowconfigure(r, weight=1)

        # Add everything to the frame
        self.mondialLabel.grid(column=1, row=1, columnspan=5)
        self.patternChooser.grid(column=1, row=2, columnspan=1)
        self.buttonWrapOnOff.grid(column=2, row=2, columnspan=1)
        self.buttonStartStop.grid(column=3, row=2, columnspan=1)
        self.buttonPause.grid(column=4, row=2, columnspan=1)
        self.buttonQuit.grid(column=5, row=2, columnspan=1)
        self.cellcanvas.grid(column=1, row=3, columnspan=5)

        self.patternChooser.bind('<<ComboboxSelected>>', func=self.pattern_selection, add='')

        self.setup_grid()
        self.display_grid()

    def redraw(self):
        self.update()
        self.display_grid()
        self.timerid = self.after(constTimerInterval, self.redraw)

    def display_grid(self):
        global display_living

        # Display the current grid here
        self.cellcanvas.delete('cell')
        for i in display_living:
            x = i[0] * constCellSizeGrid
            y = i[1] * constCellSizeGrid
            self.cellcanvas.create_rectangle(x, y, x + constCellSize, y + constCellSize, fill='#77FF77', tag='cell')

    def setup_grid(self):
        global current_cells, display_living
        global regenerated
        global const_pattern_random10, const_pattern_random20, const_pattern_random30, const_pattern_glider, \
            const_pattern_gospers, const_pattern_acorn, const_pattern_static_etc, const_pattern_diehard

        regenerated = True

        # Set up the grid here
        current_cells = []
        display_living = []
        if selectedPatternIndex <= 2:
            for x in range(constGridSize):
                temp_cells = []
                for y in range(constGridSize):
                    if selectedPatternName == const_pattern_random10:
                        rc = random.randint(0, math.floor(100/10))
                    elif selectedPatternName == const_pattern_random20:
                        rc = random.randint(0, math.floor(100/20))
                    elif selectedPatternName == const_pattern_random30:
                        rc = random.randint(0, math.floor(100/30))

                    if rc == 1:
                        temp_cells.append(1)
                        display_living.append([x, y])
                    else:
                        temp_cells.append(0)
                current_cells.append(temp_cells)
        else:
            temp_cells = []
            for x in range(constGridSize):
                temp_cells.append(0)
            for y in range(constGridSize):
                current_cells.append(temp_cells.copy())

            if selectedPatternName == const_pattern_gospers:
                self.setup_glider_gun()
            elif selectedPatternName == const_pattern_acorn:
                self.setup_acorn()
            elif selectedPatternName == const_pattern_static_etc:
                self.setup_static_and_oscillator()
            else:
                print("UNKNOWN PATTERN REQUESTED!!!!", selectedPatternIndex)

    def setup_glider_gun(self):
        offX, offY = 10, 10
        self.setup_cells(offX, offY, [0, 4], [1, 4], [0, 5], [1, 5], [10, 4], [10, 5], [10, 6], [11, 3], [11, 7],
                         [12, 2], [13, 2], [12, 8], [13, 8], [14, 5], [15, 3], [15, 7], [16, 4], [16, 5], [16, 6],
                         [17, 5], [20, 2], [20, 3], [20, 4], [21, 2], [21, 3], [21, 4], [22, 1], [22, 5], [24, 0],
                         [24, 1], [24, 5], [24, 6], [34, 2], [34, 3], [35, 2], [35, 3])

    def setup_acorn(self):
        offX, offY = math.floor(constGridSize/2), math.floor(constGridSize/2)
        self.setup_cells(offX, offY, [0, 2], [1, 0], [1, 2], [3, 1], [4, 2], [5, 2], [6, 2])

    def setup_static_and_oscillator(self):
        row1 = 10
        row2 = row1 + 20
        row3 = row2 + 20
        row4 = row3 + 10
        row5 = row4 + 10
        # Block
        offX, offY = 10, row1
        self.setup_cells(offX, offY, [0, 0], [1, 0], [1, 1], [0, 1])
        # Beehive
        offX, offY = 20, row1
        self.setup_cells(offX, offY, [0, 1], [1, 0], [1, 2], [2, 0], [2, 2], [3, 1])
        # Loaf
        offX, offY = 30, row1
        self.setup_cells(offX, offY, [0, 1], [1, 0], [2, 0], [3, 1], [3, 2], [2, 3], [1, 2])
        # Boat
        offX, offY = 40, row1
        self.setup_cells(offX, offY, [0, 0], [1, 0], [2, 1], [1, 2], [0, 1])
        # Snake (? only just found it. Might be listed somewhere)
        offX, offY = 50, row1
        self.setup_cells(offX, offY, [3, 1], [3, 0], [4, 0], [5, 1], [5, 2], [4, 3], [3, 3], [2, 3], [1, 3], [0, 4],
                         [0, 5], [1, 6], [2, 6], [2, 5])
        # Blinker
        offX, offY = 10, row2
        self.setup_cells(offX, offY, [1, 0], [2, 0], [3, 0])
        # Toad
        offX, offY = 20, row2
        self.setup_cells(offX, offY, [1, 0], [2, 0], [3, 0], [0, 1], [1, 1], [2, 1])
        # Beacon
        offX, offY = 30, row2
        self.setup_cells(offX, offY, [0, 0], [1, 0], [1, 1], [0, 1], [2, 2], [2, 3], [3, 2], [3, 3])
        # Pulsar
        offX, offY = 46, row2 + 6
        self.setup_cells(offX, offY,
                         [2, 1], [3, 1], [4, 1], [1, 2], [1, 3], [1, 4], [2, 6], [3, 6], [4, 6], [6, 2], [6, 3], [6, 4],
                         [-2, 1], [-3, 1], [-4, 1], [-1, 2], [-1, 3], [-1, 4], [-2, 6], [-3, 6], [-4, 6], [-6, 2],
                         [-6, 3], [-6, 4],
                         [2, -1], [3, -1], [4, -1], [1, -2], [1, -3], [1, -4], [2, -6], [3, -6], [4, -6], [6, -2],
                         [6, -3], [6, -4],
                         [-2, -1], [-3, -1], [-4, -1], [-1, -2], [-1, -3], [-1, -4], [-2, -6], [-3, -6], [-4, -6],
                         [-6, -2], [-6, -3], [-6, -4])
        # Pentadecathlon
        offX, offY = 60, row2
        self.setup_cells(offX, offY, [1, 0], [1, 1], [0, 2], [2, 2], [1, 3], [1, 4], [1, 5], [1, 6], [0, 7], [2, 7],
                         [1, 8], [1, 9])
        # Lightweight spaceship
        offX, offY = 10, row3
        self.setup_cells(offX, offY, [0, 1], [0, 3], [1, 0], [2, 0], [3, 0], [4, 0], [4, 1], [4, 2], [3, 3])
        # Middleweight spaceship
        offX, offY = 10, row4
        self.setup_cells(offX, offY, [0, 1], [0, 3], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [5, 1], [5, 2], [4, 3])
        # Heavyweight spaceship
        offX, offY = 10, row5
        self.setup_cells(offX, offY, [0, 1], [0, 3], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [6, 1], [6, 2],
                         [5, 3])

    def setup_cells(self, offX, offY, *args):
        global current_cells
        global display_living

        for i in args:
            current_cells[offX + i[0]][offY + i[1]] = 1
            display_living.append([offX + i[0], offY + i[1]])

    def update(self):
        global current_cells, display_living
        global constGridSize
        global running
        global wrapAroundFlag

        if running:
            # Update the grid here
            next_cells = []
            display_living = []

            temp_cells = []
            for x in range(constGridSize):
                temp_cells.append(0)
            for y in range(constGridSize):
                next_cells.append(temp_cells.copy())

            for x in range(constGridSize):
                next_cell_row = []
                xm1 = adjusted_position(x - 1)
                xp1 = adjusted_position(x + 1)

                for y in range(constGridSize):
                    ym1 = adjusted_position(y - 1)
                    yp1 = adjusted_position(y + 1)

                    # Count number of live cells around the current cell (live = 1, dead = 0)
                    if wrapAroundFlag:
                        count = current_cells[xm1][ym1] + \
                                current_cells[x][ym1] + \
                                current_cells[xp1][ym1] + \
                                current_cells[xm1][y] + \
                                current_cells[xp1][y] + \
                                current_cells[xm1][yp1] + \
                                current_cells[x][yp1] + \
                                current_cells[xp1][yp1]
                    else:
                        if x == 0:
                            if y == 0:
                                count = current_cells[xp1][y] + \
                                        current_cells[x][yp1] + \
                                        current_cells[xp1][yp1]
                            elif y >= constGridSize - 1:
                                count = current_cells[x][ym1] + \
                                        current_cells[xp1][ym1] + \
                                        current_cells[xp1][y]
                            else:
                                count = current_cells[x][ym1] + \
                                        current_cells[xp1][ym1] + \
                                        current_cells[xp1][y] + \
                                        current_cells[x][yp1] + \
                                        current_cells[xp1][yp1]
                        elif x >= constGridSize - 1:
                            if y == 0:
                                count = current_cells[xm1][y] + \
                                        current_cells[x][yp1] + \
                                        current_cells[xm1][yp1]
                            elif y >= constGridSize - 1:
                                count = current_cells[x][ym1] + \
                                        current_cells[xm1][ym1] + \
                                        current_cells[xm1][y]
                            else:
                                count = current_cells[x][ym1] + \
                                        current_cells[xm1][ym1] + \
                                        current_cells[xm1][y] + \
                                        current_cells[x][yp1] + \
                                        current_cells[xm1][yp1]
                        else:
                            if y == 0:
                                count = current_cells[xm1][y] + \
                                        current_cells[xp1][y] + \
                                        current_cells[xm1][yp1] + \
                                        current_cells[x][yp1] + \
                                        current_cells[xp1][yp1]
                            elif y >= constGridSize - 1:
                                count = current_cells[xm1][ym1] + \
                                        current_cells[x][ym1] + \
                                        current_cells[xp1][ym1] + \
                                        current_cells[xm1][y] + \
                                        current_cells[xp1][y]
                            else:
                                count = current_cells[xm1][ym1] + \
                                        current_cells[x][ym1] + \
                                        current_cells[xp1][ym1] + \
                                        current_cells[xm1][y] + \
                                        current_cells[xp1][y] + \
                                        current_cells[xm1][yp1] + \
                                        current_cells[x][yp1] + \
                                        current_cells[xp1][yp1]

                    # Who lives, who dies?
                    if current_cells[x][y] == 0:
                        if count == 3:
                            # An empty cell with exactly three neighbours comes to life
                            next_cells[x][y] = 1
                            display_living.append([x, y])
                    else:
                        if count == 2 or count == 3:
                            # A living cell with two or three neighbours stays alive
                            next_cells[x][y] = 1
                            display_living.append([x, y])
            current_cells = next_cells

    def end_it(self):
        try:
            self.after_cancel(self.timerid)
            print("Timerid cleared")
        except AttributeError:
            print("No timerid to clear")

        self.destroy()
        quit(self)

    def start_stop(self):
        global running
        global paused
        global selectedPatternName
        global selectedPatternIndex
        global regenerated

        if running:
            running = False
            self.after_cancel(self.timerid)
            self.runningText.set("Start")
            self.buttonPause.configure(state="disabled")
            self.buttonPause.configure(text="Pause")
            paused = False
            self.buttonWrapOnOff.configure(state="normal")
            self.patternChooser.configure(state='readonly')
        else:
            running = True
            self.runningText.set("Stop")
            self.buttonPause.configure(state="normal")
            self.buttonWrapOnOff.configure(state="disabled")
            self.patternChooser.configure(state='disabled')

            if not regenerated:
                self.setup_grid()
                self.display_grid()

            regenerated = False

            self.timerid = self.after(constTimerInterval, self.redraw)

    def pattern_selection(self, event):
        global startingPatternList
        global selectedPatternName
        global selectedPatternIndex
        global regenerated

        selectedPatternName = self.patternChooser.get()
        selectedPatternIndex = startingPatternList.index(selectedPatternName)
        print(selectedPatternName, selectedPatternIndex)

        self.setup_grid()
        self.display_grid()
        regenerated = True

    def pause(self):
        global paused

        if running:
            if paused:
                paused = False
                self.buttonPause.configure(text="Pause")
                self.timerid = self.after(constTimerInterval, self.redraw)
            else:
                paused = True
                self.buttonPause.configure(text="Continue")
                self.after_cancel(self.timerid)

    def wrap(self):
        global wrapAroundFlag

        if self.wrapButtonValue.get() == 1:
            wrapAroundFlag = True
        else:
            wrapAroundFlag = False


def adjusted_position(pos):
    new_pos = pos
    if pos < 0:
        new_pos = constGridSize - 1
    elif pos >= constGridSize:
        new_pos = 0
    return new_pos


rootWindow = tk.Tk()
rootWindow.title("Game of Life")

app = GameOfLifeApplication(rootWindow)
app.mainloop()
