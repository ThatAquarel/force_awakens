import math
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *


T = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])


def generate_sphere_vertices(radius, stacks, slices):
    vertices = []
    
    for i in range(stacks):
        lat0 = np.pi * (-0.5 + i / stacks)
        lat1 = np.pi * (-0.5 + (i + 1) / stacks)
        sin_lat0, cos_lat0 = np.sin(lat0), np.cos(lat0)
        sin_lat1, cos_lat1 = np.sin(lat1), np.cos(lat1)

        for j in range(slices):
            lon0 = 2 * np.pi * (j / slices)
            lon1 = 2 * np.pi * ((j + 1) / slices)
            sin_lon0, cos_lon0 = np.sin(lon0), np.cos(lon0)
            sin_lon1, cos_lon1 = np.sin(lon1), np.cos(lon1)

            v0 = [radius * cos_lat0 * cos_lon0, radius * sin_lat0, radius * cos_lat0 * sin_lon0]
            v1 = [radius * cos_lat1 * cos_lon0, radius * sin_lat1, radius * cos_lat1 * sin_lon0]
            v2 = [radius * cos_lat1 * cos_lon1, radius * sin_lat1, radius * cos_lat1 * sin_lon1]
            v3 = [radius * cos_lat0 * cos_lon1, radius * sin_lat0, radius * cos_lat0 * sin_lon1]

            vertices.extend(v0)
            vertices.extend(v1)
            vertices.extend(v2)

            vertices.extend(v0)
            vertices.extend(v2)
            vertices.extend(v3)

    return np.array(vertices, dtype=np.float32)


def generate_sphere(radius, stacks, slices, alpha_func=None):
    vertices = []
    for i in range(stacks):
        lat0 = math.pi * (-0.5 + float(i) / stacks)
        lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
        sin_lat0, cos_lat0 = math.sin(lat0), math.cos(lat0)
        sin_lat1, cos_lat1 = math.sin(lat1), math.cos(lat1)

        for j in range(slices + 1):
            lon = 2 * math.pi * float(j) / slices
            sin_lon, cos_lon = math.sin(lon), math.cos(lon)

            x0 = cos_lon * cos_lat0 * radius
            y0 = sin_lat0 * radius
            z0 = sin_lon * cos_lat0 * radius

            x1 = cos_lon * cos_lat1 * radius
            y1 = sin_lat1 * radius
            z1 = sin_lon * cos_lat1 * radius

            # Alpha blending for fog
            alpha0 = alpha_func(lat0) if alpha_func else 1.0
            alpha1 = alpha_func(lat1) if alpha_func else 1.0

            vertices.append((x0, y0, z0, alpha0))
            vertices.append((x1, y1, z1, alpha1))
    return vertices


def rotation_matrix(rx, ry, rz):
    z_t = np.array(
        [
            [np.cos(rz), np.sin(rz), 0],
            [-np.sin(rz), np.cos(rz), 0],
            [0, 0, 1],
        ]
    )
    y_t = np.array(
        [
            [np.cos(ry), 0, -np.sin(ry)],
            [0, 1, 0],
            [np.sin(ry), 0, np.cos(ry)],
        ]
    )
    x_t = np.array(
        [
            [1, 0, 0],
            [0, np.cos(rx), np.sin(rx)],
            [0, -np.sin(rx), np.cos(rx)],
        ]
    )

    return z_t @ y_t @ x_t


class Tars:
    def __init__(self):
        x, y, z = 36, 72, 9

        d = 0.01

        self.vertices = np.array([
            [0,0,0],
            [x,0,0],
            [0,y,0],
            
            [0,y,0],
            [x,y,0],
            [x,0,0],

            [0,0,z],
            [x,0,z],
            [0,y,z],
            
            [0,y,z],
            [x,y,z],
            [x,0,z],

            [0,0,0],
            [0,y,0],
            [0,y,z],

            [0,y,z],
            [0,0,z],
            [0,0,0],
            
            [x,0,0],
            [x,y,0],
            [x,y,z],

            [x,y,z],
            [x,0,z],
            [x,0,0],
#############
            [0,x,0 -d],
            [0,1.35*x, -d],
            [x,1.35*x, -d],

            [x,1.35*x, -d],
            [x,x, -d],
            [0,x, -d],

            [0,x,z + d],
            [0,1.35*x,z + d],
            [x,1.35*x,z + d],

            [x,1.35*x,z + d],
            [x,x,z + d],
            [0,x,z + d],
        ], dtype=np.float32) * 0.005

        self.color = np.array([
            *[
                [0.55, 0.55, 0.55],
            ] * 8 * 3,
            *[
                [0.10, 0.10, 0.10]
            ] * 4 * 3
        ])

    def draw(self, s, t):
        mat = rotation_matrix(t, t*0.1, t*0.5)

        glBegin(GL_TRIANGLES)
        
        pos = (self.vertices @ mat + s) @ T

        for c, v in zip(self.color, pos):
            glColor3f(*c)
            glVertex3f(*v)

        glEnd()


class Planet:
    def __init__(self, r, atm_scale=0.8,res=30, s_cache=64):
        self.planet = generate_sphere_vertices(r, res, res)
        self.planet = self.planet.reshape((-1, 3))

        self.atm_scale = atm_scale

        self.prev_s = np.empty((s_cache))
        self.prev_n = 0
        self.s_cache = s_cache

    def _draw_sphere(self, r, s, alpha):
        glBegin(GL_TRIANGLES)
        glColor4f(1,1,1, alpha)
        pos = (self.planet * r + s) @ T
        for v in pos:
            glVertex3f(*v)

        glEnd()

    def draw(self, s):
        self._draw_sphere(1, s, 1.0)

        for i, prev_s in enumerate(self.prev_s[:self.prev_n]):
            scalar = 1 / i
            self._draw_sphere(scalar, prev_s, scalar)

        self.prev_n[1:] = self.prev_n[:-1]
        self.prev_n[0] = s
        self.prev_n = np.min(self.s_cache, self.prev_n + 1)


class BlackHole:
    def __init__(self):
        pass


    def draw(self, s):
        ...

