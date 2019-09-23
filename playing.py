

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