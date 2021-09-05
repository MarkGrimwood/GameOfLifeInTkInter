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
const_pattern_gospers = "Gosper's Glider Gun"
const_pattern_acorn = "Acorn"
const_pattern_static_etc = "Statics, oscillators and spaceships"

startingPatternList = [ \
    const_pattern_random10, \
    const_pattern_random20, \
    const_pattern_random30, \
    const_pattern_gospers, \
    const_pattern_acorn, \
    const_pattern_static_etc \
]
selectedPatternIndex = 0
selectedPatternName = startingPatternList[selectedPatternIndex]

constTimerInterval = 10
constGridSize = 192
constCellSize = 4
constCellSizeGrid = constCellSize # + 1
current_cells = []
display_living = []
update_births = []
update_deaths = []


class GameOfLifeApplication(ttk.Frame):

    def __init__(self, windowparent=None):
        global startingPatternList, selectedPatternName, selectedPatternIndex

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

        self.display_grid()

    def redraw(self):
        update()
        self.display_grid()
        self.timerid = self.after(constTimerInterval, self.redraw)

    def display_grid(self):
        global display_living

        # Display the current grid here
        self.cellcanvas.delete('cell')
        for i in display_living:
            pos_column = i[0] * constCellSizeGrid
            pos_row = i[1] * constCellSizeGrid
            self.cellcanvas.create_rectangle(pos_column, pos_row, pos_column + constCellSize, pos_row + constCellSize, fill='#7777FF', tag='cell')

    def end_it(self):
        try:
            self.after_cancel(self.timerid)
            # print("Timerid cleared")
        except AttributeError:
            # print("No timerid to clear")
            pass

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
                setup_grid()
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

        setup_grid()
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


def setup_grid():
    global current_cells, display_living
    global regenerated
    global const_pattern_random10, const_pattern_random20, const_pattern_random30, \
        const_pattern_gospers, const_pattern_acorn, const_pattern_static_etc

    regenerated = True

    print(f"Setting up grid number {selectedPatternIndex} named {selectedPatternName}")

    # Set up the grid here
    current_cells = []
    display_living = []
    if selectedPatternIndex <= 2:
        for column in range(constGridSize):
            temp_cells = []
            for row in range(constGridSize):
                rc = 0
                if selectedPatternName == const_pattern_random10:
                    rc = random.randint(0, math.floor(100/10))
                elif selectedPatternName == const_pattern_random20:
                    rc = random.randint(0, math.floor(100/20))
                elif selectedPatternName == const_pattern_random30:
                    rc = random.randint(0, math.floor(100/30))

                if rc == 1:
                    temp_cells.append(1)
                    display_living.append([column, row])
                else:
                    temp_cells.append(0)
            current_cells.append(temp_cells)
    else:
        temp_cells = []
        for column in range(constGridSize):
            temp_cells.append(0)
        for row in range(constGridSize):
            current_cells.append(temp_cells.copy())

        if selectedPatternName == const_pattern_gospers:
            setup_glider_gun()
        elif selectedPatternName == const_pattern_acorn:
            setup_acorn()
        elif selectedPatternName == const_pattern_static_etc:
            setup_static_and_oscillator()
        else:
            print("UNKNOWN PATTERN REQUESTED!!!!", selectedPatternIndex)


def setup_glider_gun():
    offset_column, offset_row = 10, 10
    setup_cells(offset_column, offset_row, [0, 4], [1, 4], [0, 5], [1, 5], [10, 4], [10, 5], [10, 6], [11, 3], [11, 7],
                     [12, 2], [13, 2], [12, 8], [13, 8], [14, 5], [15, 3], [15, 7], [16, 4], [16, 5], [16, 6],
                     [17, 5], [20, 2], [20, 3], [20, 4], [21, 2], [21, 3], [21, 4], [22, 1], [22, 5], [24, 0],
                     [24, 1], [24, 5], [24, 6], [34, 2], [34, 3], [35, 2], [35, 3])


def setup_acorn():
    offset_column, offset_row = math.floor(constGridSize/2), math.floor(constGridSize/2)
    setup_cells(offset_column, offset_row, [0, 2], [1, 0], [1, 2], [3, 1], [4, 2], [5, 2], [6, 2])


def setup_static_and_oscillator():
    row1 = 10
    row2 = row1 + 20
    row3 = row2 + 20
    row4 = row3 + 10
    row5 = row4 + 10
    # Block
    offset_column, offset_row = 10, row1
    setup_cells(offset_column, offset_row, [0, 0], [1, 0], [1, 1], [0, 1])
    # Beehive
    offset_column, offset_row = 20, row1
    setup_cells(offset_column, offset_row, [0, 1], [1, 0], [1, 2], [2, 0], [2, 2], [3, 1])
    # Loaf
    offset_column, offset_row = 30, row1
    setup_cells(offset_column, offset_row, [0, 1], [1, 0], [2, 0], [3, 1], [3, 2], [2, 3], [1, 2])
    # Boat
    offset_column, offset_row = 40, row1
    setup_cells(offset_column, offset_row, [0, 0], [1, 0], [2, 1], [1, 2], [0, 1])
    # Snake (? only just found it. Might be listed somewhere)
    offset_column, offset_row = 50, row1
    setup_cells(offset_column, offset_row, [3, 1], [3, 0], [4, 0], [5, 1], [5, 2], [4, 3], [3, 3], [2, 3], [1, 3], [0, 4],
                     [0, 5], [1, 6], [2, 6], [2, 5])
    # Blinker
    offset_column, offset_row = 10, row2
    setup_cells(offset_column, offset_row, [1, 0], [2, 0], [3, 0])
    # Toad
    offset_column, offset_row = 20, row2
    setup_cells(offset_column, offset_row, [1, 0], [2, 0], [3, 0], [0, 1], [1, 1], [2, 1])
    # Beacon
    offset_column, offset_row = 30, row2
    setup_cells(offset_column, offset_row, [0, 0], [1, 0], [1, 1], [0, 1], [2, 2], [2, 3], [3, 2], [3, 3])
    # Pulsar
    offset_column, offset_row = 46, row2 + 6
    setup_cells(offset_column, offset_row,
                     [2, 1], [3, 1], [4, 1], [1, 2], [1, 3], [1, 4], [2, 6], [3, 6], [4, 6], [6, 2], [6, 3], [6, 4],
                     [-2, 1], [-3, 1], [-4, 1], [-1, 2], [-1, 3], [-1, 4], [-2, 6], [-3, 6], [-4, 6], [-6, 2],
                     [-6, 3], [-6, 4],
                     [2, -1], [3, -1], [4, -1], [1, -2], [1, -3], [1, -4], [2, -6], [3, -6], [4, -6], [6, -2],
                     [6, -3], [6, -4],
                     [-2, -1], [-3, -1], [-4, -1], [-1, -2], [-1, -3], [-1, -4], [-2, -6], [-3, -6], [-4, -6],
                     [-6, -2], [-6, -3], [-6, -4])
    # Pentadecathlon
    offset_column, offset_row = 60, row2
    setup_cells(offset_column, offset_row, [1, 0], [1, 1], [0, 2], [2, 2], [1, 3], [1, 4], [1, 5], [1, 6], [0, 7], [2, 7],
                     [1, 8], [1, 9])
    # Lightweight spaceship
    offset_column, offset_row = 10, row3
    setup_cells(offset_column, offset_row, [0, 1], [0, 3], [1, 0], [2, 0], [3, 0], [4, 0], [4, 1], [4, 2], [3, 3])
    # Middleweight spaceship
    offset_column, offset_row = 10, row4
    setup_cells(offset_column, offset_row, [0, 1], [0, 3], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [5, 1], [5, 2], [4, 3])
    # Heavyweight spaceship
    offset_column, offset_row = 10, row5
    setup_cells(offset_column, offset_row, [0, 1], [0, 3], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [6, 1], [6, 2],
                     [5, 3])


def setup_cells(offset_column, offset_row, *args):
    global current_cells
    global display_living

    for i in args:
        current_cells[offset_column + i[0]][offset_row + i[1]] = 1
        display_living.append([offset_column + i[0], offset_row + i[1]])


def update():
    global current_cells, display_living, update_births, update_deaths
    global constGridSize
    global running
    global wrapAroundFlag

    if running:
        # Update the grid here
        display_living = []
        update_births = []
        update_deaths = []

        for column in range(constGridSize):
            column_m1 = adjusted_position(column - 1)
            column_p1 = adjusted_position(column + 1)

            for row in range(constGridSize):
                row_m1 = adjusted_position(row - 1)
                row_p1 = adjusted_position(row + 1)

                # Count number of live cells around the current cell (live = 1, dead = 0)
                if wrapAroundFlag:
                    count = current_cells[column_m1][row_m1] + \
                            current_cells[column][row_m1] + \
                            current_cells[column_p1][row_m1] + \
                            current_cells[column_m1][row] + \
                            current_cells[column_p1][row] + \
                            current_cells[column_m1][row_p1] + \
                            current_cells[column][row_p1] + \
                            current_cells[column_p1][row_p1]
                else:
                    if column == 0:
                        if row == 0:
                            count = current_cells[column_p1][row] + \
                                    current_cells[column][row_p1] + \
                                    current_cells[column_p1][row_p1]
                        elif row >= constGridSize - 1:
                            count = current_cells[column][row_m1] + \
                                    current_cells[column_p1][row_m1] + \
                                    current_cells[column_p1][row]
                        else:
                            count = current_cells[column][row_m1] + \
                                    current_cells[column_p1][row_m1] + \
                                    current_cells[column_p1][row] + \
                                    current_cells[column][row_p1] + \
                                    current_cells[column_p1][row_p1]
                    elif column >= constGridSize - 1:
                        if row == 0:
                            count = current_cells[column_m1][row] + \
                                    current_cells[column][row_p1] + \
                                    current_cells[column_m1][row_p1]
                        elif row >= constGridSize - 1:
                            count = current_cells[column][row_m1] + \
                                    current_cells[column_m1][row_m1] + \
                                    current_cells[column_m1][row]
                        else:
                            count = current_cells[column][row_m1] + \
                                    current_cells[column_m1][row_m1] + \
                                    current_cells[column_m1][row] + \
                                    current_cells[column][row_p1] + \
                                    current_cells[column_m1][row_p1]
                    else:
                        if row == 0:
                            count = current_cells[column_m1][row] + \
                                    current_cells[column_p1][row] + \
                                    current_cells[column_m1][row_p1] + \
                                    current_cells[column][row_p1] + \
                                    current_cells[column_p1][row_p1]
                        elif row >= constGridSize - 1:
                            count = current_cells[column_m1][row_m1] + \
                                    current_cells[column][row_m1] + \
                                    current_cells[column_p1][row_m1] + \
                                    current_cells[column_m1][row] + \
                                    current_cells[column_p1][row]
                        else:
                            count = current_cells[column_m1][row_m1] + \
                                    current_cells[column][row_m1] + \
                                    current_cells[column_p1][row_m1] + \
                                    current_cells[column_m1][row] + \
                                    current_cells[column_p1][row] + \
                                    current_cells[column_m1][row_p1] + \
                                    current_cells[column][row_p1] + \
                                    current_cells[column_p1][row_p1]

                # Who lives, who dies?
                if current_cells[column][row] == 0:
                    if count == 3:
                        # An empty cell with exactly three neighbours comes to life
                        display_living.append([column, row])
                        update_births.append([column, row])
                else:
                    if count == 2 or count == 3:
                        # A living cell with two or three neighbours stays alive
                        display_living.append([column, row])
                    else:
                        update_deaths.append([column, row])

        for i in update_births:
            current_cells[i[0]][i[1]] = 1
        for i in update_deaths:
            current_cells[i[0]][i[1]] = 0


def adjusted_position(pos):
    new_pos = pos
    if pos < 0:
        new_pos = constGridSize - 1
    elif pos >= constGridSize:
        new_pos = 0
    return new_pos


# --- The starting code ---
setup_grid()

rootWindow = tk.Tk()
rootWindow.title("Game of Life")

app = GameOfLifeApplication(rootWindow)
app.mainloop()
