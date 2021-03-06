#!/usr/bin/env python

from __future__ import division, print_function

import math
import random

import entity
import character
import function
import mask

class Shot(entity.MovingObject):
    shot_hitmasks = {}

    fade_time = 0.8 # seconds of fading when max_flight_time is being reached
    max_flight_time = 1.5

    def __init__(self, game, state, sourceweapon, damage, direction, speed):
        super(Shot, self).__init__(game, state)

        self.direction = 0.0
        self.flight_time = 0.0
        self.sourceweapon = sourceweapon
        self.damage = damage

        srcwep = state.entities[sourceweapon]
        srcchar = state.entities[srcwep.owner]

        self.x = srcchar.x
        self.y = srcchar.y+8

        self.direction = direction

        self.hspeed = math.cos(math.radians(self.direction)) * speed
        self.vspeed = math.sin(math.radians(self.direction)) * -speed

    def step(self, game, state, frametime):
        # gravitational force
        self.vspeed += 4.5 * frametime

        # calculate direction
        self.direction = function.point_direction(self.x - self.hspeed, self.y - self.vspeed, self.x, self.y)

    def endstep(self, game, state, frametime):
        super(Shot, self).endstep(game, state, frametime)

        self.flight_time += frametime

        angle = int(self.direction) % 360
        if angle in self.shot_hitmasks:
            mask = self.shot_hitmasks[angle]
        else:
            mask = function.load_mask("projectiles/shots/0").rotate(angle)
            self.shot_hitmasks[angle] = mask

        if game.map.collision_mask.overlap(mask, (int(self.x), int(self.y))) or self.flight_time > self.max_flight_time:
            # calculate unit speeds (speeds normalized into the range 0-1)
            h_unit_speed = math.cos(math.radians(self.direction))
            v_unit_speed = -math.sin(math.radians(self.direction))

            x, y = self.x, self.y

            # move back until we're not colliding anymore - this is the colliding point
            while game.map.collision_mask.overlap(mask, (int(x), int(y))):
                x -= h_unit_speed
                y -= v_unit_speed

            self.destroy(state)

    def interpolate(self, prev_obj, next_obj, alpha):
        super(Shot, self).interpolate(prev_obj, next_obj, alpha)
        self.direction = function.interpolate_angle(prev_obj.direction, next_obj.direction, alpha)

        self.flight_time = prev_obj.flight_time + (next_obj.flight_time - prev_obj.flight_time) * alpha

class Rocket(entity.MovingObject):
    rocket_hitmasks = {}

    fade_time = .3 # seconds of fading when max_flight_time is being reached
    max_flight_time = 20

    damage = 35
    blastradius = 65
    knockback = 240

    def __init__(self, game, state, sourceweapon):
        super(Rocket, self).__init__(game, state)

        self.direction = 0.0
        self.flight_time = 0.0
        self.sourceweapon = sourceweapon

        srcwep = state.entities[sourceweapon]
        srcchar = state.entities[srcwep.owner]

        self.x = srcchar.x
        self.y = srcchar.y

        self.direction = srcwep.direction

        self.speed = 500
        self.hspeed = math.cos(math.radians(self.direction)) * self.speed
        self.vspeed = math.sin(math.radians(self.direction)) * -self.speed

    def destroy(self, game, state, frametime):
        if not self.max_flight_time - self.flight_time < self.fade_time:
            for obj in state.entities.values():
                if isinstance(obj, character.Character) and math.hypot(self.x - obj.x, self.y - obj.y) < self.blastradius:
                    force = (1-(math.hypot(self.x - obj.x, self.y - obj.y)/self.blastradius)) * self.knockback # TODO: Fix this to be correct. I think the problem is that it checks distance to the center of the character, and a rocketmans feet are too far.
                    obj.hspeed += force*((obj.x-self.x)/math.hypot(self.x - obj.x, self.y - obj.y))
                    obj.vspeed += force*((obj.y-self.y)/math.hypot(self.x - obj.x, self.y - obj.y))/3

        super(Rocket, self).destroy(state)

    def step(self, game, state, frametime):
        self.speed += 30 # Copied from GMK-GG2; should simulate some very basic acceleration+air resistance.
        self.speed *= 0.92

        self.hspeed = math.cos(math.radians(self.direction)) * self.speed
        self.vspeed = math.sin(math.radians(self.direction)) * -self.speed

        # calculate direction
        self.direction = function.point_direction(self.x - self.hspeed, self.y - self.vspeed, self.x, self.y)

    def endstep(self, game, state, frametime):
        super(Rocket, self).endstep(game, state, frametime)

        self.flight_time += frametime

        angle = int(self.direction) % 360
        if angle in self.rocket_hitmasks:
            mask = self.rocket_hitmasks[angle]
        else:
            mask = function.load_mask("projectiles/rockets/0").rotate(angle)
            self.rocket_hitmasks[angle] = mask

        if game.map.collision_mask.overlap(mask, (int(self.x), int(self.y))) or self.flight_time > self.max_flight_time:
            self.destroy(game, state, frametime)

    def interpolate(self, prev_obj, next_obj, alpha):
        super(Rocket, self).interpolate(prev_obj, next_obj, alpha)
        self.direction = function.interpolate_angle(prev_obj.direction, next_obj.direction, alpha)

        self.flight_time = prev_obj.flight_time + (next_obj.flight_time - prev_obj.flight_time) * alpha

class Flame(entity.MovingObject):
    flame_hitmasks = {}
    max_flight_time = 1/2
    damage = 3.3

    def __init__(self, game, state, sourceweapon):
        super(Flame, self).__init__(game, state)

        self.direction = 0.0
        self.flight_time = 0.0
        self.sourceweapon = sourceweapon

        srcwep = state.entities[sourceweapon]
        srcchar = state.entities[srcwep.owner]

        self.x = srcchar.x
        self.y = srcchar.y

        self.direction = (srcwep.direction + (10-random.randint(0, 20))) % 360

        self.speed = 150 + random.randint(0, 150)
        self.hspeed = math.cos(math.radians(self.direction)) * self.speed + srcchar.hspeed
        self.vspeed = math.sin(math.radians(self.direction)) * -self.speed + srcchar.vspeed


    def step(self, game, state, frametime):
        #Gravitational force
        self.vspeed += 4.5*frametime

    def endstep(self, game, state, frametime):
        super(Flame, self).endstep(game, state, frametime)

        self.flight_time += frametime

        angle = int(self.direction)

        if angle in self.flame_hitmasks:
            mask = self.flame_hitmasks[angle]
        else:
            mask = function.load_mask("projectiles/flames/0").rotate(angle)
            self.flame_hitmasks[angle] = mask

        if game.map.collision_mask.overlap(mask, (int(self.x), int(self.y))) or self.flight_time > self.max_flight_time:
            self.destroy(state)


    def interpolate(self, prev_obj, next_obj, alpha):
        super(Flame, self).interpolate(prev_obj, next_obj, alpha)
        self.direction = function.interpolate_angle(prev_obj.direction, next_obj.direction, alpha)

        self.flight_time = prev_obj.flight_time + (next_obj.flight_time - prev_obj.flight_time) * alpha
