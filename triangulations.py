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

    def __str__(self):
        string = str(self.id) + ": (" + str(self.x) + "," + str(self.y) + ")"
        return string

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id

class Line():
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2

    def __str__(self):
        return str(self.point1) + ", " + str(self.point2)

    def __eq__(self, other):
        return (self.point1 == other.point1 and self.point2 == other.point2) or \
               (self.point1 == other.point2 and self.point2 == other.point1)

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

def incremental_triangulation(points):
    sorted_points = [p for p in sorted(points, key=lambda point: point.x)]
    lines = []
    # Make the first triangle
    lines.append(Line(sorted_points[0], sorted_points[1]))
    lines.append(Line(sorted_points[0], sorted_points[2]))
    lines.append(Line(sorted_points[1], sorted_points[2]))

    hull_points = set()
    hull_points.add(sorted_points[0])
    hull_points.add(sorted_points[1])
    hull_points.add(sorted_points[2])

    for j in range(3,len(sorted_points)):
        next_point = sorted_points[j]
        hull1, hull2 = visible_extreme_points(hull_points, next_point)
        lines.append(Line(hull1, next_point))
        lines.append(Line(hull2, next_point))

        points_to_remove = []
        for p in hull_points:
            if visible_line(Line(hull1, hull2), p):
                points_to_remove.append(p)

        for p in points_to_remove:
            lines.append(Line(p, next_point))
            hull_points.remove(p)

        hull_points.add(next_point)

    return lines

def visible_extreme_points(pointlist, point):
    max_slope = float('-inf')
    max_point = None
    min_slope = float('inf')
    min_point = None
    for p in pointlist:

       k = (p.y-point.y)/(p.x-point.x)
       if k > max_slope:
           max_slope=k
           max_point=p
       if k < min_slope:
           min_slope=k
           min_point=p

    return (min_point, max_point)

def visible_line(line, point):
    if line.point1.y==line.point2.y:
        return True
    x0 = line.point1.x + (line.point2.x-line.point1.x)*(point.y-line.point1.y)/((line.point2.y-line.point1.y))
    if x0 < point.x:
        return True
    else:
        return False

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
            if len(points) >= 3:
                phase = 2
                c.delete(cursor)
                for line in incremental_triangulation(points):
                    c.create_line(line.point1.x, line.point1.y, line.point2.x, line.point2.y)

    return

def in_done_button(x, y):
    return x <= done_button_width and y <= done_button_height

############################
###     Final Setup      ###
############################

master.bind('<Motion>', motion)
master.bind('<ButtonRelease-1>', button_release)
mainloop()
