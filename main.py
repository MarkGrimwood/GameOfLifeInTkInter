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
constGridSize = 256
constCellSizeGridMaximum = 8
cellSizeGrid = constCellSizeGridMaximum
constDisplaySize = 512
constScrollBarSize = 17
current_cells = []
display_living = []
update_births = []
update_deaths = []
next_recompute_area = []
current_recompute_area = []
generationNumber = 0
livingCells = 0
recomputeCount = 0

class GameOfLifeApplication(ttk.Frame):

    def __init__(self, windowparent=None):
        global startingPatternList, selectedPatternName, selectedPatternIndex
        global constDisplaySize, constScrollBarSize

        self.lifeFrame = ttk.Frame.__init__(self, windowparent, padding=(12, 3))
        self.buttonFrame = ttk.Frame(self, relief='ridge', padding=10)
        self.canvasFrame = ttk.Frame(self,
                                     width=constDisplaySize + constScrollBarSize + 5,
                                     height=constDisplaySize + constScrollBarSize + 5,
                                     relief='ridge', padding=3)

        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        self.define_variables_for_widgets()
        self.create_buttons(self.buttonFrame)
        self.create_labels(self.buttonFrame)
        self.create_canvas(self.canvasFrame)
        self.create_lists(self.buttonFrame)

        self.add_widgets()

        self.update_labels()
        self.display_grid()

    def create_lists(self, frame):
        self.patternChooser = ttk.Combobox(frame, values=startingPatternList, width=16, state='readonly')
        self.patternChooser.set(startingPatternList[selectedPatternIndex])
        selectedPatternName = startingPatternList[selectedPatternIndex]

    def create_buttons(self, frame):
        self.buttonStartStop = ttk.Button(frame, textvariable=self.runningText, command=self.start_stop)#, width=16)
        self.buttonStartStop.focus()
        self.buttonWrapOnOff = ttk.Checkbutton(frame, text='Wraparound', command=self.wrap, var=self.wrapButtonValue)#, width=16)
        self.buttonQuit = ttk.Button(frame, text='Quit', command=self.end_it)#, width=16)
        self.buttonPause = ttk.Button(frame, text='Pause', state="disabled", command=self.pause)#, width=16)
        self.buttonZoomIn = ttk.Button(frame, text='Zoom In', state="enabled", command=self.zoom_in)#, width=16)
        self.buttonZoomOut = ttk.Button(frame, text='Zoom Out', state="enabled", command=self.zoom_out)#, width=16)

    def create_labels(self, frame):
        self.infoLabel = ttk.Label(frame, textvariable=self.infoText, anchor='w')

    def create_canvas(self, frame):
        global cellSizeGrid

        self.cellcanvas = tk.Canvas(frame,
                                    width=constDisplaySize, height=constDisplaySize,
                                    # scrollregion=(0, 0, constGridSize * cellSizeGrid, constGridSize * cellSizeGrid),
                                    scrollregion=(0, 0, constDisplaySize*2, constDisplaySize*2),
                                    background='black')

        self.cellcanvashorizontalbar = tk.Scrollbar(self.cellcanvas, orient=tk.HORIZONTAL, command=self.cellcanvas.xview)
        self.cellcanvasverticalbar = tk.Scrollbar(self.cellcanvas, orient=tk.VERTICAL, command=self.cellcanvas.yview)

        self.cellcanvas.configure(xscrollcommand=self.cellcanvashorizontalbar.set, yscrollcommand=self.cellcanvasverticalbar.set)

    def define_variables_for_widgets(self):
        self.runningText = tk.StringVar()
        self.runningText.set("Start")

        self.infoText = tk.StringVar()

        self.wrapButtonValue = tk.IntVar()
        self.wrapButtonValue.set(1)

    def add_widgets(self):
        global constDisplaySize, constScrollBarSize

        # Add everything to the frame
        self.infoLabel.grid(column=1, row=1, columnspan=7)

        self.patternChooser.grid(column=1, row=2)
        self.buttonWrapOnOff.grid(column=2, row=2)
        self.buttonStartStop.grid(column=3, row=2)
        self.buttonPause.grid(column=4, row=2)
        self.buttonQuit.grid(column=5, row=2)
        self.buttonZoomIn.grid(column=6, row=2)
        self.buttonZoomOut.grid(column=7, row=2)

        self.grid(column=0, row=0, sticky='nw')
        self.buttonFrame.grid(column=1, row=1, sticky='nw')
        self.canvasFrame.grid(column=1, row=2, sticky='nwse')

        self.cellcanvas.place(x=0,y=0, width=constDisplaySize + constScrollBarSize, height=constDisplaySize + constScrollBarSize)
        self.cellcanvashorizontalbar.place(x=0, y=constDisplaySize, width=constDisplaySize)
        self.cellcanvasverticalbar.place(x=constDisplaySize, y=0, height=constDisplaySize)

        for c in range(1, self.grid_size()[0]+1):
            self.columnconfigure(c, weight=1)
        for r in range(1, self.grid_size()[1]+1):
            self.rowconfigure(r, weight=1)

        self.patternChooser.bind('<<ComboboxSelected>>', func=self.pattern_selection, add='')

    def redraw(self):
        global running

        if running and not paused:
            update()

        self.display_grid()
        self.update_labels()

        if running and not paused:
            self.timerid = self.after(constTimerInterval, self.redraw)

    def update_labels(self):
        global livingCells, recomputeCount

        self.infoText.set(f"Generation={generationNumber:>5}, Living cells={livingCells:>5}, Recomputes={recomputeCount:>5}")

    def display_grid(self):
        global display_living
        global cellSizeGrid, constCellSizeGridMaximum

        cellDisplaySizeBeforeScale = constCellSizeGridMaximum * 2

        # Display the current grid here
        self.cellcanvas.delete(tk.ALL)

        for row in next_recompute_area:
            pos_row = row[0] * cellDisplaySizeBeforeScale
            for column in row[1]:
                pos_column = column * cellDisplaySizeBeforeScale
                self.cellcanvas.create_rectangle(pos_column, pos_row,
                                                 pos_column + cellDisplaySizeBeforeScale,
                                                 pos_row + cellDisplaySizeBeforeScale,
                                                 fill='#773333', tag='cell')

        for row in display_living:
            pos_row = row[0] * cellDisplaySizeBeforeScale
            for column in row[1]:
                pos_column = column * cellDisplaySizeBeforeScale
                self.cellcanvas.create_rectangle(pos_column, pos_row,
                                                 pos_column + cellDisplaySizeBeforeScale,
                                                 pos_row + cellDisplaySizeBeforeScale,
                                                 fill='#CCCCFF', tag='cell')

        self.cellcanvas.scale('cell', 0, 0, 1/cellSizeGrid, 1/cellSizeGrid)

    def end_it(self):
        try:
            self.after_cancel(self.timerid)
        except AttributeError:
            pass

        self.destroy()
        quit(self)

    def start_stop(self):
        global running
        global paused
        global selectedPatternName
        global selectedPatternIndex
        global regenerated
        global generationNumber

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
            generationNumber = 0
            self.update_labels()
            self.runningText.set("Stop")
            self.buttonPause.configure(state="normal")
            paused = False
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
        self.update_labels()
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

    def zoom_out(self):
        global cellSizeGrid, constCellSizeGridMaximum

        if cellSizeGrid < constCellSizeGridMaximum:
            cellSizeGrid *= 2
            self.buttonZoomIn.configure(state="normal")
            if not running:
                self.redraw()
        if cellSizeGrid >= constCellSizeGridMaximum:
            self.buttonZoomOut.configure(state="disabled")

    def zoom_in(self):
        global cellSizeGrid

        if cellSizeGrid > 1:
            cellSizeGrid /= 2
            self.buttonZoomOut.configure(state="normal")
            if not running:
                self.redraw()
        if cellSizeGrid <= 1:
            self.buttonZoomIn.configure(state="disabled")


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

    temp_cells = []
    for column in range(constGridSize):
        temp_cells.append(0)
    for row in range(constGridSize):
        current_cells.append(temp_cells.copy())

    if selectedPatternIndex <= 2:
        for column in range(constGridSize):
            for row in range(constGridSize):
                rc = 0
                if selectedPatternName == const_pattern_random10:
                    rc = random.randint(0, math.floor(100/10))
                elif selectedPatternName == const_pattern_random20:
                    rc = random.randint(0, math.floor(100/20))
                elif selectedPatternName == const_pattern_random30:
                    rc = random.randint(0, math.floor(100/30))

                if rc == 1:
                    setup_cells(0, 0, [column, row])
    else:
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

    for iter_add in args:
        column, row = offset_column + iter_add[0], offset_row + iter_add[1]
        current_cells[column][row] = 1
        set_living_cells(offset_column, offset_row, *args)


def set_living_cells(offset_column, offset_row, *args):
    global display_living

    for iter_add in args:
        column, row = offset_column + iter_add[0], offset_row + iter_add[1]

        found = False
        for iter_living in display_living:
            if iter_living[0] == row:
                iter_living[1].append(column)
                found = True
                break
        if not found:
            display_living.append([row, [column]])
        set_recompute_areas(column, row)


def set_recompute_areas(column, row):
    column_m1 = adjusted_position(column - 1)
    column_p1 = adjusted_position(column + 1)
    row_m1 = adjusted_position(row - 1)
    row_p1 = adjusted_position(row + 1)

    set_recompute_areas_sub(column_m1, row_m1)
    set_recompute_areas_sub(column, row_m1)
    set_recompute_areas_sub(column_p1, row_m1)

    set_recompute_areas_sub(column_m1, row)
    set_recompute_areas_sub(column, row)
    set_recompute_areas_sub(column_p1, row)

    set_recompute_areas_sub(column_m1, row_p1)
    set_recompute_areas_sub(column, row_p1)
    set_recompute_areas_sub(column_p1, row_p1)


def set_recompute_areas_sub(column, row):
    global next_recompute_area
    global recomputeCount

    found = False
    for iter_recompute in next_recompute_area:
        if iter_recompute[0] == row:
            try:
                if iter_recompute[1].index(column):
                    pass
            except ValueError:
                iter_recompute[1].append(column)
                recomputeCount += 1
            found = True
            break
    if not found:
        next_recompute_area.append([row, [column]])
        recomputeCount += 1


def update():
    global current_cells, display_living, update_births, update_deaths, next_recompute_area
    global constGridSize
    global running
    global wrapAroundFlag
    global livingCells
    global generationNumber
    global recomputeCount

    # Update the grid here
    display_living = []
    update_births = []
    update_deaths = []
    current_recompute_area = next_recompute_area
    next_recompute_area = []
    recomputeCount = 0
    livingCells = 0
    generationNumber += 1

    for iter_row in current_recompute_area:
        row = iter_row[0]
        row_m1 = adjusted_position(row - 1)
        row_p1 = adjusted_position(row + 1)

        for column in iter_row[1]:
            column_m1 = adjusted_position(column - 1)
            column_p1 = adjusted_position(column + 1)

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
                    set_living_cells(0, 0, [column, row])
                    update_births.append([column, row])
                    livingCells += 1
            else:
                if count == 2 or count == 3:
                    # A living cell with two or three neighbours stays alive
                    set_living_cells(0, 0, [column, row])
                    livingCells += 1
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
