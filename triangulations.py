from tkinter import *

############################
###      Constants       ###
############################

point_diameter = 6
point_radius = point_diameter / 2
done_button_width = 70
done_button_height = 30

############################
###  Class Declarations  ###
############################

class Point():
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

class Line():
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2

############################
###   Utility Methods    ###
############################

def convex_hull(points):
    '''
    :param points: A list of Point objects, which have an id and x and y coordinates
    :return: A list of lines that form the convex hull of the given points
    '''
    lines = []
    for i in range(len(points) - 1):
        lines.append(Line(points[i], points[i+1]))

    for line in lines:
        print("Point 1:", (line.point1.x, line.point1.y), "; Point 2:", (line.point2.x, line.point2.y))

    return lines

############################
###     Window Setup     ###
############################

master = Tk()
master.title("Triangulations: brought to you by Group 4")
msg = Message(master, text = "Put down some points", width = 200)
msg.pack()
c = Canvas(master, width=700, height=500)
c.pack()

done_button = c.create_rectangle(0,0,done_button_width,done_button_height, fill='#A1D490', activefill='#DEF0D8')
done_message = c.create_text(35,17, text="I'm done")
cursor = c.create_oval(0,0,-10,-10)
points = []

############################
###     Mouse Events     ###
############################

# Phase variable: so mouse events are different when we're doing different things
# Phase 1: Putting down points
# Phase 2: Drawing lines
phase = 1

def motion(event):
    if phase == 1:
        if not in_done_button(event.x, event.y):
            c.coords(cursor, event.x - point_radius, event.y - point_radius, event.x + point_radius, event.y + point_radius)
    return

def button_release(event):
    global phase
    if phase == 1:
        if not in_done_button(event.x, event.y):
            # Put down a point
            new_point_id = c.create_oval(event.x - point_radius, event.y - point_radius, event.x + point_radius, event.y + point_radius,
                                         activefill='red')
            points.append(Point(new_point_id, event.x, event.y))
        else:
            # "I'm done" button was pressed
            phase = 2
            c.delete(cursor)
            convex_hull(points)
    return

def in_done_button(x, y):
    return x <= done_button_width and y <= done_button_height

############################
###     Final Setup      ###
############################

master.bind('<Motion>', motion)
master.bind('<ButtonRelease-1>', button_release)
mainloop()
