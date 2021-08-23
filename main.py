import math
import random
import tkinter as tk
from tkinter import ttk

running = False
paused = False
wrapAroundFlag = True
regenerated = False
selectedPatternName = ""
selectedPatternIndex = 0

constTimerInterval = 10
constGridSize = 128
constCellSize = 4
constCellSizeGrid = constCellSize + 1
current_cells = []
display_living = []


class GameOfLifeApplication(ttk.Frame):

    def __init__(self, windowparent=None):
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

        self.startingPatternList = ["Random 10%", "Random 20%", "Random 30%", "Glider"]
        self.patternChooser = ttk.Combobox(self, values=self.startingPatternList, width=16, state='readonly')
        self.patternChooser.set(self.startingPatternList[selectedPatternIndex])
        selectedPatternName = self.startingPatternList[selectedPatternIndex]

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
        global current_cells
        global display_living
        global regenerated

        regenerated = True

        # Set up the grid here
        current_cells = []
        display_living = []
        if selectedPatternIndex <= 2:
            for x in range(constGridSize):
                temp_cells = []
                for y in range(constGridSize):
                    if selectedPatternIndex == 0:
                        rc = random.randint(0, math.floor(100/10))
                    if selectedPatternIndex == 1:
                        rc = random.randint(0, math.floor(100/20))
                    if selectedPatternIndex == 2:
                        rc = random.randint(0, math.floor(100/30))
                    if rc == 1:
                        temp_cells.append(1)
                        display_living.append([x, y])
                    else:
                        temp_cells.append(0)
                current_cells.append(temp_cells)
        else:
            for x in range(constGridSize):
                temp_cells = []
                for y in range(constGridSize):
                    temp_cells.append(0)
                current_cells.append(temp_cells)

            if selectedPatternIndex == 3:
                self.setup_glider()

    def setup_glider(self):
        offX, offY = math.floor(constGridSize/2), math.floor(constGridSize/2)
        self.setup_cells(offX + 0, offY + 0)
        self.setup_cells(offX + 1, offY + 0)
        self.setup_cells(offX + 2, offY + 0)
        self.setup_cells(offX + 2, offY + 1)
        self.setup_cells(offX + 1, offY + 2)

    def setup_cells(self, x, y):
        global current_cells
        global display_living

        current_cells[x][y] = 1
        display_living.append([x, y])

    def update(self):
        global current_cells
        global constGridSize
        global display_living
        global running
        global wrapAroundFlag

        if running:
            # Update the grid here
            next_cells = []
            display_living = []

            if wrapAroundFlag:
                pass

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
                            next_cell_row.append(1)
                            display_living.append([x, y])
                        else:
                            next_cell_row.append(0)
                    else:
                        if count == 2 or count == 3:
                            # A living cell with two or three neighbours stays alive
                            next_cell_row.append(1)
                            display_living.append([x, y])
                        else:
                            # A living cell with too many or too few neighbours dies
                            next_cell_row.append(0)
                next_cells.append(next_cell_row)
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
        global selectedPatternName
        global selectedPatternIndex
        global regenerated

        selectedPatternName = self.patternChooser.get()
        selectedPatternIndex = self.startingPatternList.index(selectedPatternName)
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


def print_hierarchy(w, depth=0):
    print('  ' * depth + w.winfo_class() + ' w=' + str(w.winfo_width()) + ' h=' + str(w.winfo_height()) + ' x=' + str(
        w.winfo_x()) + ' y=' + str(w.winfo_y()))
    for i in w.winfo_children():
        print_hierarchy(i, depth + 1)


rootWindow = tk.Tk()
rootWindow.title("Game of Life")

app = GameOfLifeApplication(rootWindow)
# print_hierarchy(rootWindow)
app.mainloop()
