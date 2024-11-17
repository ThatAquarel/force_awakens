import importlib.resources
import io
import math
import numpy as np
import importlib

from OpenGL.GL import *
from OpenGL.GLU import *

from force_awakens.mechanics.colors import COLORS
from force_awakens.graphics.render import create_vbo, update_vbo, draw_vbo


# The transformation matrix to transform the camera coordinates into the right-handed coordinates
T = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])


def generate_sphere_vertices(radius, stacks, slices):
    vertices = []

    # Generates all the points of any given spherical object (planets, black holes, etc)
    for i in range(stacks):
        # Gets the latitudinal sections of each vertice
        lat0 = np.pi * (-0.5 + i / stacks)
        lat1 = np.pi * (-0.5 + (i + 1) / stacks)
        sin_lat0, cos_lat0 = np.sin(lat0), np.cos(lat0)
        sin_lat1, cos_lat1 = np.sin(lat1), np.cos(lat1)

        for j in range(slices):
            # Gets the longitudinal sections of each vertice
            lon0 = 2 * np.pi * (j / slices)
            lon1 = 2 * np.pi * ((j + 1) / slices)
            sin_lon0, cos_lon0 = np.sin(lon0), np.cos(lon0)
            sin_lon1, cos_lon1 = np.sin(lon1), np.cos(lon1)

            # Combines the latitudinal and longitudinal components of the sphere to form it's vertices

            v0 = [
                radius * cos_lat0 * cos_lon0,
                radius * sin_lat0,
                radius * cos_lat0 * sin_lon0,
            ]
            v1 = [
                radius * cos_lat1 * cos_lon0,
                radius * sin_lat1,
                radius * cos_lat1 * sin_lon0,
            ]
            v2 = [
                radius * cos_lat1 * cos_lon1,
                radius * sin_lat1,
                radius * cos_lat1 * sin_lon1,
            ]
            v3 = [
                radius * cos_lat0 * cos_lon1,
                radius * sin_lat0,
                radius * cos_lat0 * sin_lon1,
            ]

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
        # Gets the latitudinal sections of each vertice
        lat0 = math.pi * (-0.5 + float(i) / stacks)
        lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
        sin_lat0, cos_lat0 = math.sin(lat0), math.cos(lat0)
        sin_lat1, cos_lat1 = math.sin(lat1), math.cos(lat1)

        for j in range(slices + 1):
            # Gets the longitudinal sections of each vertice
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

            # Appends the vertices and alpha blending for the sphere's vertices
            vertices.append((x0, y0, z0, alpha0))
            vertices.append((x1, y1, z1, alpha1))
    return vertices


def rotation_matrix(rx, ry, rz):
    # The z, y, and x rotation matrices
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

    # Returns the singular translation matrix for the 3
    return z_t @ y_t @ x_t


# TARS!!!
# class Tars:
#     def __init__(self):
#         x, y, z = 36, 72, 9

#         d = 0.01

#         self.vertices = (
#             np.array(
#                 [
#                     [0, 0, 0],
#                     [x, 0, 0],
#                     [0, y, 0],
#                     [0, y, 0],
#                     [x, y, 0],
#                     [x, 0, 0],
#                     [0, 0, z],
#                     [x, 0, z],
#                     [0, y, z],
#                     [0, y, z],
#                     [x, y, z],
#                     [x, 0, z],
#                     [0, 0, 0],
#                     [0, y, 0],
#                     [0, y, z],
#                     [0, y, z],
#                     [0, 0, z],
#                     [0, 0, 0],
#                     [x, 0, 0],
#                     [x, y, 0],
#                     [x, y, z],
#                     [x, y, z],
#                     [x, 0, z],
#                     [x, 0, 0],
#                     #############
#                     [0, x, 0 - d],
#                     [0, 1.35 * x, -d],
#                     [x, 1.35 * x, -d],
#                     [x, 1.35 * x, -d],
#                     [x, x, -d],
#                     [0, x, -d],
#                     [0, x, z + d],
#                     [0, 1.35 * x, z + d],
#                     [x, 1.35 * x, z + d],
#                     [x, 1.35 * x, z + d],
#                     [x, x, z + d],
#                     [0, x, z + d],
#                 ],
#                 dtype=np.float32,
#             )
#             * 0.005
#         )

#         self.color = np.array(
#             [
#                 *[
#                     [0.55, 0.55, 0.55],
#                 ]
#                 * 8
#                 * 3,
#                 *[[0.10, 0.10, 0.10]] * 4 * 3,
#             ]
#         )

#     def draw(self, s, t):
#         mat = rotation_matrix(t, t * 0.1, t * 0.5)

#         glBegin(GL_TRIANGLES)

#         pos = (self.vertices @ mat + s) @ T

#         for c, v in zip(self.color, pos):
#             glColor3f(*c)
#             glVertex3f(*v)

#         glEnd()


class Planet:
    def __init__(self, r, res=15, s_cache=256):
        # Generates a planet with vertices from generate_sphere_vertices
        self.planet = generate_sphere_vertices(1, res, res)
        self.planet = self.planet.reshape((-1, 3))

        self.prev_s = np.empty((s_cache, 3))
        self.prev_n = 0
        self.s_cache = s_cache

        self.r = r

        self.intro = False

        # Sets the initial color to rgb 1,1,1
        self.def_color = np.ones(4, dtype=np.float32)

        self.sphere_point = generate_sphere_vertices(1, res, res).reshape((-1, 3))
        self.sphere_color = np.ones((len(self.sphere_point), 4), dtype=np.float32)
        self.sphere_vbo = create_vbo(self._get_s_vbo_data(r, [0, 0, 0], self.def_color))
        self.sphere_stride = self.sphere_point.itemsize * 7
        self.sphere_n = self.sphere_point.shape[0]

        self.trail_point = np.zeros((s_cache, 3), dtype=np.float32)
        self.trail_color = np.ones((s_cache, 3), dtype=np.float32)
        self.trail_vbo = create_vbo(self._get_t_vbo_data(self.def_color[:3]))
        self.trail_stride = self.trail_point.itemsize * 6

    def _get_s_vbo_data(self, r, s, col):
        points = (self.sphere_point * r + s) @ T
        colors = self.sphere_color * col
        return np.hstack((points, colors)).astype(np.float32)

    def _get_t_vbo_data(self, col):
        points = self.trail_point @ T
        colors = self.trail_color * col
        return np.hstack((points, colors)).astype(np.float32)

    def _draw_sphere(self, scalar, r, s, alpha):
        # Draws a sphere using triangles to build it

        col = self.def_color * [1, scalar, 1, 1]
        update_vbo(self.sphere_vbo, self._get_s_vbo_data(r, s, col))
        draw_vbo(
            self.sphere_vbo, self.sphere_stride, GL_TRIANGLES, self.sphere_n, c_ptr=4
        )

    def _draw_trail(self, s, scalar):
        self.trail_point[1:] = self.trail_point[:-1]
        self.trail_point[0] = s
        self.prev_n = min(self.s_cache - 1, self.prev_n + 1)

        col = self.def_color[:3] * [0.5, 0.5 * scalar, 0.5]
        update_vbo(self.trail_vbo, self._get_t_vbo_data(col))
        glLineWidth(2.0)
        draw_vbo(self.trail_vbo, self.trail_stride, GL_LINE_STRIP, self.prev_n)

    # TODO DRAW SECTION

    def set_color(self, col):
        self.def_color[:3] = col

    def draw(self, s, _, decay):
        # Draws the introductory sequence for any given newly added planet
        if self.intro:
            scalar = (self.prev_n / (self.s_cache - 1)) ** 3
        else:
            scalar = decay
        if decay == 1:
            self._draw_sphere(scalar, self.r * scalar, s, 1.0)

        # Creates the cloud of points surrounding newly created planets
        if self.prev_n < (self.s_cache - 1) and self.intro:
            uniform_points = np.random.uniform(-1, 1, (100, 3))
            uniform_points = np.tan(uniform_points)
            glPointSize(2 * (1 - scalar))
            glBegin(GL_POINTS)

            col = self.def_color[:3] * [1, scalar, 1]
            glColor4f(*col, decay * -2.5 * (scalar + 0.25) * (scalar - 1))
            for point in uniform_points:
                glVertex3f(*(point + s) @ T)
            glEnd()
        else:
            self.intro = False

        self._draw_trail(s, scalar)


class BlackHole:
    def __init__(self, r, res=25, n_stars=32768):
        # Initialises the black hole's sphere
        self.draw_dense = True

        self.r = r
        self.vertices = generate_sphere_vertices(r, res, res)
        self.vertices = self.vertices.reshape((-1, 3))

        sphere_point = generate_sphere_vertices(r, res, res).reshape((-1, 3))
        sphere_vbo_data = np.zeros((len(sphere_point), 6), dtype=np.float32)
        sphere_vbo_data[:, :3] = sphere_point

        self.sphere_vbo = create_vbo(sphere_vbo_data)
        self.sphere_stride = sphere_point.itemsize * 6
        self.sphere_n = sphere_point.shape[0]

        # Creates the stars surrounding the black hole
        self.n_stars = n_stars
        stars = np.random.random((n_stars, 3)) * 5 - 2.5
        stars = (np.sin(stars) - 1.1) * np.tan(stars)

        # Gives the stars colors
        colors = np.random.random((n_stars, 3))
        colors = colors + 0.5 * (1 - colors)

        self.data = np.empty((n_stars, 6), dtype=np.float32)
        self.data[:, :3] = stars
        self.data[:, 3:] = colors

        self.stride = self.data.itemsize * 6

        # Rotates the stars around the black hole at a speed dependant upon their proximity to it
        self.dist = np.linalg.norm(stars, axis=1)
        self.rot_mat = self._build_rot()

        self.point_vbo = create_vbo(self._get_vbo_data(0))

    def _draw_center(self, *_):
        draw_vbo(self.sphere_vbo, self.sphere_stride, GL_TRIANGLES, self.sphere_n)

    def _build_rot(self):
        # Creates the rotation matrix for the stars around the black hole
        rx = 1 / self.dist**2 * (1 / 30)

        rot_mat = np.zeros((self.n_stars, 3, 3), dtype=np.float32)
        rot_mat[:, 0, 0] = 1
        rot_mat[:, 1, 1] = np.cos(rx)
        rot_mat[:, 1, 2] = np.sin(rx)
        rot_mat[:, 2, 1] = -np.sin(rx)
        rot_mat[:, 2, 2] = np.cos(rx)

        return rot_mat

    def _get_vbo_data(self, t):
        # Gets information on the buffer of of the stars
        stars = self.rot_mat @ self.data[:, :3, np.newaxis]
        self.data[:, :3] = stars.squeeze(-1)

        return self.data

    def draw(self, s, t, _):
        if self.draw_dense:
            glDepthMask(GL_FALSE)
            glPointSize(1.0)
            draw_vbo(self.point_vbo, self.stride, GL_POINTS, self.n_stars)
            glDepthMask(GL_TRUE)

        update_vbo(self.point_vbo, self._get_vbo_data(t))

        glClear(GL_DEPTH_BUFFER_BIT)
        self._draw_center(self.r, s)


class Background:
    def __init__(self, n_stars=32768):
        # Creates the stars that are in the background, and their rotations and colors
        self.n_stars = n_stars

        stars = self._radial()

        colors = np.random.random((n_stars, 3))

        self.data = np.empty((n_stars, 6), dtype=np.float32)
        self.data[:, :3] = stars
        self.data[:, 3:] = colors

        # Creates buffer for the stars
        self.stride = self.data.itemsize * 6
        self.point_vbo = create_vbo(self.data)

    def _radial(self):
        stars = np.empty((self.n_stars, 3))

        theta = np.random.uniform(0, np.pi, self.n_stars)
        phi = np.random.uniform(0, np.pi, self.n_stars)
        r = np.random.uniform(0, 0.5, self.n_stars)
        r = np.tan(r * 100 - 50) * 1024

        # Creates the rotation matri of the stars
        stars[:, 0] = r * np.sin(theta) * np.cos(phi)
        stars[:, 1] = r * np.sin(theta) * np.sin(phi)
        stars[:, 2] = r * np.cos(theta)

        return stars

    def draw(self):
        glDepthMask(GL_FALSE)

        glPointSize(1.0)
        draw_vbo(self.point_vbo, self.stride, GL_POINTS, self.n_stars)

        glDepthMask(GL_TRUE)
        glClear(GL_DEPTH_BUFFER_BIT)
