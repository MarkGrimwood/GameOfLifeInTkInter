# Game Of Life In Python and TkInter

I first heard of John Conway's Game of Life in the first programming book I bought, Mastering Machine Code On Your ZX81 by Toni Baker (p116 of https://archive.org/details/masteringmachinecodeonyourzx81/mode/2up or p114 in the book) and seeing complex patterns arise from simple rules in a 16x16 grid. Computers since then have got much faster and the grids can be much bigger, but the fascination remains

I'm now using Life to learn Python with TkInter. If you've not seen Life before there's plenty of information on Wikipedia https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life

My implementation currently has a grid of 256x256 cells, which can be increased if you don't mind it slowing down, and allows a choice of three randomised starting positions; 10%, 20% or 30%, or a small selection of predefined pattens. The intention is to add some more, and add a drawing facility probably with a load/save own pattern option. 

I've done my best to speed it up, but Python may not be the fastest of languages. The technique I've used is to only recompute living cells, and those empty spaces next to them. On sparse patterns it's 20-25% faster than computing every cell, but on the dense patterns, like those from the random grids, it does seem to be slower. There is a bottleneck in drawing the grid too, where more living cells means a slower display. I have an idea for a fix for this
