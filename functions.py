from __future__ import division

import math, pygame
from pygame.locals import *

def sign(x):
    # Returns the sign of the number given
    return cmp(x, 0)

def point_direction(x1, y1, x2, y2):
    angle = -math.degrees(math.atan2(y2 - y1, x2 - x1))
    if angle < 0: angle += 360
    return angle

def rotate_surface_point(surface, angle, point = (0, 0)):
    # takes a pygame surface, an angle (in degrees) to rotate the surface with (increasing counter clockwise)
    # and a point to rotate around
    
    # save original surface's width and height
    width, height = surface.get_size()
    
    rotated_surface = pygame.transform.rotate(surface, angle)
    
    # compensate for rotation - http://math.stackexchange.com/questions/75478/trivial-trigonometry-problem/75700#75700
    # the solution at the link is clockwise increasing angles, we'll use those from now on
    angle = 360 - angle
    px, py = point
    
    # TODO: remove nested function
    def F(x, y, h, a):
        return ((h - y) * math.sin(a) + x * math.cos(a), y * math.cos(a) + x * math.sin(a))
    
    offset = (0, 0)
    
    if angle < 90:
        offset = F(px, py, height, math.radians(angle))
    elif angle < 180:
        offset = F(height - py, px, width, math.radians(angle - 90))
    elif angle < 270:
        offset = F(width - px, height - py, height, math.radians(angle - 180))
    else:
        offset = F(py, width - px, width, math.radians(angle - 270))
    
    return rotated_surface, offset


    
# prevent double-loading, only load a filename once
images = {}
def load_image(filename):
    if filename in images:
        return images[filename].copy()
    
    image = pygame.image.load(filename).convert()
    image.set_colorkey((255, 0, 255), RLEACCEL)
    images[filename] = image
    
    return image
    
