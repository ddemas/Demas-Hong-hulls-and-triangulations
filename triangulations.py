from tkinter import *
import math
import random

############################
###      Constants       ###
############################

point_diameter = 6
point_radius = point_diameter / 2

button_width = 120
button_height = 30
button_buffer = 20

canvas_width = 700
canvas_height = 500

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
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return self.x * 1000 + self.y

class Line():
    def __init__(self, point1, point2):
        self.id = id
        self.point1 = point1
        self.point2 = point2

        if point1.x == point2.x:
            self.slope = float('inf')
        else:
            self.slope = (point1.y - point2.y) / (point1.x - point2.x)

    def __str__(self):
        return str(self.point1) + ", " + str(self.point2)

    def __eq__(self, other):
        return (self.point1 == other.point1 and self.point2 == other.point2) or \
               (self.point1 == other.point2 and self.point2 == other.point1)

    def __hash__(self):
        return hash(self.point1) * 1000000 + hash(self.point2)

    def set_id(self, id):
        self.id = id

    def has_any(self, points):
        '''
        Return true if the line touches any of the given points
        '''
        return self.point1 in points or self.point2 in points

    def not_point(self, point):
        '''
        Returns the point on this line that is not the given point
        '''
        if self.point1 == point:
            return self.point2
        else:
            return self.point1

class Circle():
    def __init__(self, center, radius, points):
        self.center = center
        self.radius = radius
        self.points = points
        self.id = None

class Quadrilateral():
    def __init__(self, points):
        self.points = points

############################
###   Utility Methods    ###
############################

hull_points = None

def circle_corners(center, radius):
    return (Point(None, center.x - radius, center.y - radius),
            Point(None, center.x + radius, center.y + radius))

def circumcircle(p_1, p_2, p_3):
    A = math.sqrt((p_1.x - p_2.x) ** 2 + (p_1.y - p_2.y) ** 2)
    B = math.sqrt((p_1.x - p_3.x) ** 2 + (p_1.y - p_3.y) ** 2)
    C = math.sqrt((p_2.x - p_3.x) ** 2 + (p_2.y - p_3.y) ** 2)
    x1 = p_1.x
    y1 = p_1.y
    x2 = p_2.x
    y2 = p_2.y
    x3 = p_3.x
    y3 = p_3.y
    center_x=((y2-y1)*(y3*y3-y1*y1+x3*x3-x1*x1)-(y3-y1)*(y2*y2-y1*y1+x2*x2-x1*x1))/(2.0*((x3-x1)*(y2-y1)-(x2-x1)*(y3-y1)))
    center_y=((x2-x1)*(x3*x3-x1*x1+y3*y3-y1*y1)-(x3-x1)*(x2*x2-x1*x1+y2*y2-y1*y1))/(2.0*((y3-y1)*(x2-x1)-(y2-y1)*(x3-x1)))
    radius = math.sqrt((x1-center_x)**2 + (y1-center_y)**2)
    return Circle(Point(None, center_x, center_y), radius, [p_1, p_2, p_3])

def incremental_triangulation(points):
    global hull_points

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
        if p.x == point.x:
            k = float('inf')
        else:
            k = (p.y-point.y)/(p.x-point.x)

        if k >= max_slope:
            max_slope=k
            max_point=p
        if k <= min_slope:
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

def connected_lines(point, lines):
    connected = []
    for line in lines:
        if point == line.point1 or point == line.point2:
            connected.append(line)
    return connected

def get_triangle_vertices(line1, line2, line3):
    points = [line1.point1, line1.point2]
    if line2.point1 in points:
        points.append(line2.point2)
    else:
        points.append(line2.point1)

    if not (line3.point1 in points and line3.point2 in points):
        raise("These lines do not define a triangle:\n", line1, line2, line3)
    return points

def random_color():
    r = lambda: random.randint(0,255)
    return '#%02X%02X%02X' % (r(),r(),r())

def get_all_circles(points, lines):
    circles = []
    sorted_points = [p for p in sorted(points, key=lambda point: point.x, reverse=True)]
    old_points = set()

    for p in sorted_points:
        visible_points = {}
        connected = connected_lines(p, lines)
        for line in connected:
            if line.point1 == p:
                visible_points[line] = line.point2
            else:
                visible_points[line] = line.point1

        sorted_visible_points = [point for _, point in sorted(visible_points.items(), key=lambda item: item[0].slope)
                                 if point not in old_points]

        for i in range(len(sorted_visible_points) - 1):
            circles.append(circumcircle(p, sorted_visible_points[i], sorted_visible_points[i+1]))

        old_points.add(p)

    return circles

def in_circle(point, circle):
    return math.sqrt((point.x - circle.center.x)**2 + (point.y - circle.center.y)**2) < circle.radius \
           and point not in circle.points

def find_illegal_edges(circle, interior_points, lines):
    interior_lines = set()
    for triangle_point in circle.points:
        connected = connected_lines(triangle_point, lines)
        for l in [line for line in connected if line.has_any(interior_points) or
                            line.point1 == triangle_point and line.point2 in circle.points or
                            line.point2 == triangle_point and line.point1 in circle.points]:
            interior_lines.add(l)

    illegal_edges = {}

    for p in interior_points:
        # If there are exactly two edges between an interior point and the points on
        # the triangle, then the edge between the points connected to those two edges is illegal.

        connected = [l for l in connected_lines(p, interior_lines) if l.has_any(circle.points)]
        if len(connected) == 2:
            point1 = connected[0].not_point(p)
            point2 = connected[1].not_point(p)
            for l in interior_lines:
                if l == Line(point1, point2):
                    illegal_edges[l] = Quadrilateral(circle.points)
                    break

    return illegal_edges

def flip(edge, lines, quad):
    '''
    Just returns the new edge
    '''
    connected1 = connected_lines(edge.point1, lines)
    connected2 = connected_lines(edge.point2, lines)

    common_adjacent_points = [l1.not_point(edge.point1) for l1 in connected1 if
     l1.not_point(edge.point1) in [l2.not_point(edge.point2) for l2 in connected2]]
    in_circle_adjacent = [p for p in common_adjacent_points if
                          in_circle(p, circumcircle(quad.points[0], quad.points[1], quad.points[2]))
                                    or p in quad.points]
    sorted_adjacent_points = sorted(in_circle_adjacent, key=lambda point: dist_to_line_from_point(edge, point), reverse=True)

    if len(sorted_adjacent_points) >= 2:
        return Line(sorted_adjacent_points[0], sorted_adjacent_points[1])
    else:
        print("something went wrong")

def find_line(id, lines):
    for l in lines:
        if id == l.id:
            return l
    return None

def dist_to_line_from_point(line, p):
    A = line.point1.y - line.point2.y
    B = -(line.point1.x - line.point2.x)
    C = line.point2.y * (line.point1.x - line.point2.x) - line.point2.x * (line.point1.y - line.point2.y)
    return (A * p.x + B * p.y + C) / math.sqrt(A**2 + B**2)

############################
###     Window Setup     ###
############################

master = Tk()
master.title("Triangulations: brought to you by Group 3")
msg = Message(master, text = "Put down some points", width = 200)
msg.pack()
button_c = Canvas(master, width=canvas_width, height=button_height)
button_c.pack()
c = Canvas(master, width=canvas_width, height=canvas_height)
c.pack()

done_button = button_c.create_rectangle(0,1,button_width,button_height, fill='#A1D490', activefill='#DEF0D8')
done_message = button_c.create_text(60,17, text="I'm done")

circle_button = button_c.create_rectangle(button_width + button_buffer, 1, button_width*2 + button_buffer, button_height,
                                    fill='#B5B5B5')
circle_message = button_c.create_text(60+button_width + button_buffer, 17, text="Toggle circles")

lines_button = button_c.create_rectangle((button_width + button_buffer) * 2, 1,
                                         (button_width + button_buffer) * 2 + button_width, button_height,
                                    fill='#B5B5B5')
lines_message = button_c.create_text(60+(button_width + button_buffer) * 2, 17, text="Toggle illegal lines")

cursor = c.create_oval(0,0,-10,-10)
points = []
lines = set()
circles = []
illegal_lines = {}

############################
###     Mouse Events     ###
############################

# Phase variable: so mouse events are different when we're doing different things
# Phase 1: Putting down points
# Phase 2: Drawing lines
phase = 1

showing_circles = False
showing_illegal = False

def motion(event):
    if phase == 1:
        if in_canvas(event.x, event.y):
            c.coords(cursor, event.x - point_radius, event.y - point_radius, event.x + point_radius, event.y + point_radius)
    return

def button_release(event):
    global phase
    global lines
    global circles
    global illegal_lines
    global showing_circles
    global showing_illegal

    if phase == 1:
        if not in_done_button(event.x, event.y) and in_canvas(event.x, event.y):
            # Put down a point
            new_point_id = c.create_oval(event.x - point_radius, event.y - point_radius, event.x + point_radius, event.y + point_radius,
                                         fill='black')
            points.append(Point(new_point_id, event.x, event.y))
        elif in_done_button(event.x, event.y):
            # "I'm done" button was pressed
            if len(points) >= 3:
                phase = 2
                c.delete(cursor)
                lines = set(incremental_triangulation(points))
                for line in lines:
                    line.set_id(c.create_line(line.point1.x, line.point1.y, line.point2.x, line.point2.y,
                                              width=2, activewidth=4, activefill='#145F78'))

                circles = get_all_circles(points, lines)

                # Look for illegal lines
                for circle in circles:
                    for edge, quad in find_illegal_edges(circle, [p for p in points if in_circle(p, circle)], lines).items():
                        illegal_lines[edge] = quad

                msg.configure(text="")
                button_c.itemconfigure(done_button, fill='#b5b5b5', activefill='#b5b5b5')
                button_c.itemconfigure(circle_button, fill='#F4FF24', activefill='#FCFFCC')
                button_c.itemconfigure(lines_button, fill='#F4FF24', activefill='#FCFFCC')
            else:
                msg.configure(text="Not enough points.")

    if phase == 2:
        if not showing_circles:
            if in_circle_button(event.x, event.y):
                display_circles()
                showing_circles = True
        else:
            if in_circle_button(event.x, event.y):
                for circle in circles:
                    c.delete(circle.id)
                showing_circles = False

        if not showing_illegal:
            if in_lines_button(event.x, event.y):
                legal_lines = [l for l in lines if l not in illegal_lines]
                for illegal in illegal_lines:
                    c.itemconfigure(illegal.id, fill='red')
                for legal in legal_lines:
                    c.itemconfigure(legal.id, fill='green')

                showing_illegal = True
        else:
            if in_lines_button(event.x, event.y):
                for line in lines:
                    c.itemconfigure(line.id, fill='black')
                showing_illegal = False

        if len(on_line(event.x, event.y)) > 0:
            line_to_flip_id = on_line(event.x, event.y)[0]
            if line_to_flip_id in [l.id for l in illegal_lines]:
                line_to_flip = find_line(line_to_flip_id, illegal_lines)

                new_line = flip(line_to_flip, lines, illegal_lines[line_to_flip])

                lines.remove(line_to_flip)
                c.delete(line_to_flip_id)
                new_line.set_id(c.create_line(new_line.point1.x, new_line.point1.y, new_line.point2.x, new_line.point2.y,
                                        width=2, activewidth=4, activefill='#145F78'))
                lines.add(new_line)

                if showing_circles:
                    for circle in circles:
                        c.delete(circle.id)
                    circles = get_all_circles(points, lines)
                    display_circles()

                    for circle in circles:
                        for edge, quad in find_illegal_edges(circle, [p for p in points if in_circle(p, circle)], lines).items():
                            illegal_lines[edge] = quad
                else:
                    circles = get_all_circles(points, lines)
                    for circle in circles:
                        for edge, quad in find_illegal_edges(circle, [p for p in points if in_circle(p, circle)], lines).items():
                            illegal_lines[edge] = quad

                if showing_illegal:
                    set_illegal_legal_colors()

    return

def in_done_button(x, y):
    overlapping = button_c.find_overlapping(x,y,x+1,y+1)
    if len(overlapping) > 0:
        return done_button in overlapping
    else:
        return False

def in_circle_button(x, y):
    overlapping = button_c.find_overlapping(x,y,x+1,y+1)
    if len(overlapping) > 0:
        return circle_button in overlapping
    else:
        return False

def in_lines_button(x, y):
    overlapping = button_c.find_overlapping(x,y,x+1,y+1)
    if len(overlapping) > 0:
        return lines_button in overlapping
    else:
        return False

def on_line(x, y):
    overlapping = c.find_overlapping(x,y,x+1,y+1)
    if len(overlapping) > 0:
        return [id for id in overlapping if id in [l.id for l in lines]]
    else:
        return []

def display_circles():
    for circle in circles:
        corner1, corner2 = circle_corners(circle.center, circle.radius)
        circle.id = c.create_oval(corner1.x, corner1.y, corner2.x, corner2.y,
                                  outline='green', width=2, activewidth=5)

    for circle in circles:
        for p in points:
            if in_circle(p, circle):
                c.itemconfigure(circle.id, outline='red')

def set_illegal_legal_colors():
    legal_lines = [l for l in lines if l not in illegal_lines]
    for illegal in illegal_lines:
        c.itemconfigure(illegal.id, fill='red')
    for legal in legal_lines:
        c.itemconfigure(legal.id, fill='green')

def in_canvas(x, y):
    return x < canvas_width and x >= 0 and y < canvas_height and y >= button_height + 10

############################
###     Final Setup      ###
############################

master.bind('<Motion>', motion)
master.bind('<ButtonRelease-1>', button_release)
mainloop()
