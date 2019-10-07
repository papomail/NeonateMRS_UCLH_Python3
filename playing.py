
import numpy as np
import pyqtgraph  as pg
from PyQt5 import QtGui
class rectangle:
    def __init__(self, length, width):
        self.length = length
        self.width = width
    
    def area(self):
        return self.length * self.width

    def perimeter(self):
        return 2 * (self.length + self.width)


class square(rectangle):
    def __init__(self, length):
        super().__init__(length,length)

A = rectangle(20.6,30)

B = square(2.4)



print()
print(f'Area of A is {A.area()} square meters \nType of "length": {type(A.length)} \nType of "width": {type(A.width)}) ')      
print()
print(f'Area of B is {B.area()} square meters and it\'s perimeter {B.perimeter()} meters')
print()  


class cube(square):
    def surface_area(self):
        return 6 * super().area()
    def volume(self):
        return self.length ** 3
    
C= cube(1)
        
print()
print(f'C\'s volume is {C.volume()} cubic meters and it\'s area is {C.surface_area()} square meters')
print()          



# Always start by initializing Qt (only once per application)
app = QtGui.QApplication([])

## Define a top-level widget to hold everything
w = QtGui.QWidget()

## Create some widgets to be placed inside
btn = QtGui.QPushButton('press me')
text = QtGui.QLineEdit('enter text')
listw = QtGui.QListWidget()
plot = pg.PlotWidget()

## Create a grid layout to manage the widgets size and position
layout = QtGui.QGridLayout()
w.setLayout(layout)

## Add widgets to the layout in their proper positions
layout.addWidget(btn, 0, 0)   # button goes in upper-left
layout.addWidget(text, 1, 0)   # text edit goes in middle-left
layout.addWidget(listw, 2, 0)  # list widget goes in bottom-left
layout.addWidget(plot, 0, 1, 3, 1)  # plot goes on right side, spanning 3 rows

## Display the widget as a new window
w.show()



x = np.random.normal(size=1000)
y = np.random.normal(size=1000)
#pg.plot(x, y, pen=None, symbol='o')  ## setting pen=None disables line drawing

plot.plotItem()

## Start the Qt event loop
app.exec_()
