import time

import glm
import glfw
import numpy as np
import imgui
from imgui.integrations.glfw import GlfwRenderer
from OpenGL.GL import *
from OpenGL.GLU import *

from force_awakens.graphics.shader import get_shader_program


_axes_y = np.mgrid[0:2, 0:1:11j, 0:1].T.reshape((-1, 3)) - [0.5, 0.5, 0.0]
_axes_x = _axes_y[:, [1, 0, 2]]


class App:
    def __init__(
        self,
        window_size,
        name,
        zoom_sensitivity=0.1,
        pan_sensitvity=0.0025,
        orbit_sensitivity=0.004,
    ):
        self.zoom_sensitivity = zoom_sensitivity
        self.pan_sensitvity = pan_sensitvity
        self.orbit_sensitivity = orbit_sensitivity

        self.angle_x, self.angle_y = 45.0, 45.0
        self.pan_x, self.pan_y = 0.0, 0.0
        self.last_x, self.last_y = 0.0, 0.0
        self.dragging, self.panning = False, False
        self.zoom_level = 1.0
        self.view_left, self.view_right = 0, 0

        self.window = self.window_init(window_size, name)
        self.imgui_impl = self.init_imgui(self.window)

        self.rendering_loop(self.window, self.imgui_impl)

    def window_init(self, window_size, name):
        if not glfw.init():
            raise Exception("GLFW could not be initialized.")

        glfw.window_hint(glfw.SAMPLES, 4)
        window = glfw.create_window(*window_size, name, None, None)
        if not window:
            glfw.terminate()
            raise Exception("GLFW window could not be created.")

        glfw.make_context_current(window)
        glfw.set_cursor_pos_callback(window, self.cursor_pos_callback)
        glfw.set_mouse_button_callback(window, self.mouse_button_callback)
        glfw.set_scroll_callback(window, self.scroll_callback)
        glfw.set_framebuffer_size_callback(window, self.resize_callback)

        self.last_x, self.last_y = glfw.get_cursor_pos(window)

        self.resize_callback(window, *window_size)

        return window

    def init_imgui(self, window):
        imgui.create_context()
        return GlfwRenderer(window, attach_callbacks=False)

    def mouse_button_callback(self, window, button, action, mods):
        if self.imgui_impl != None and imgui.get_io().want_capture_mouse:
            return

        press = action == glfw.PRESS

        if button == glfw.MOUSE_BUTTON_LEFT:
            self.dragging = press
            shift = glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS
            self.panning = shift
        elif button == glfw.MOUSE_BUTTON_MIDDLE:
            self.dragging = press
            self.panning = press

    def cursor_pos_callback(self, window, xpos, ypos):
        if self.imgui_impl != None and imgui.get_io().want_capture_mouse:
            return

        if self.dragging:
            dx = xpos - self.last_x
            dy = ypos - self.last_y
            if self.panning:
                self.pan_x += dx * self.pan_sensitvity * self.zoom_level
                self.pan_y -= dy * self.pan_sensitvity * self.zoom_level
            else:
                self.angle_x += dy * self.orbit_sensitivity
                self.angle_y += dx * self.orbit_sensitivity

        self.last_x, self.last_y = xpos, ypos

    def scroll_callback(self, window, xoffset, yoffset):
        if self.imgui_impl != None and imgui.get_io().want_capture_mouse:
            return

        if yoffset > 0:
            self.zoom_level /= 1 + self.zoom_sensitivity
        elif yoffset < 0:
            self.zoom_level *= 1 + self.zoom_sensitivity

    def resize_callback(self, window, width, height):
        glViewport(0, 0, width, height)

        aspect_ratio = width / height if height > 0 else 1.0
        self.view_left = -aspect_ratio
        self.view_right = aspect_ratio

    def draw_axes(self):
        glLineWidth(1.0)
        glBegin(GL_LINES)

        glColor3f(1.0, 1.0, 1.0)
        for point in _axes_x:
            glVertex3f(*(point))
        for point in _axes_y:
            glVertex3f(*point)
        glEnd()

        glLineWidth(2.0)
        glBegin(GL_LINES)

        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(*[-0.5, 0.0, 0.0])
        glVertex3f(*[0.5, 0.0, 0.0])

        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(*[0.0, -0.5, 0.0])
        glVertex3f(*[0.0, 0.5, 0.0])

        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(*[0.0, 0.0, -0.5])
        glVertex3f(*[0.0, 0.0, 0.5])

        glEnd()

    def draw_points(self, points):
        glPointSize(4.0)
        glBegin(GL_LINE_STRIP)
        glColor3f(1.0, 1.0, 1.0)

        for i, point in enumerate(points):
            # glColor3f(*aruco_point_color[i % aruco_point_color.shape[0]])
            glVertex3f(*point @ self.T)

        glEnd()

    def window_should_close(self, window):
        return glfw.window_should_close(window)

    def terminate(self):
        glfw.terminate()

    def update(self, shader_program):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.86, 0.87, 0.87, 1.0)

        glUseProgram(shader_program)

        proj = glm.ortho(
            self.view_left * self.zoom_level,
            self.view_right * self.zoom_level,
            -self.zoom_level,
            self.zoom_level,
            -32,
            32,
        )

        proj_loc = glGetUniformLocation(shader_program, "camera_projection")
        glUniformMatrix4fv(proj_loc, 1, GL_TRUE, glm.value_ptr(proj))

        pos = glm.translate(glm.vec3(self.pan_x, self.pan_y, 0.0))
        pos @= glm.rotate(self.angle_x, (1.0, 0.0, 0.0))
        pos @= glm.rotate(self.angle_y, (0.0, 1.0, 0.0))

        pos_loc = glGetUniformLocation(shader_program, "camera_position")
        glUniformMatrix4fv(pos_loc, 1, GL_TRUE, glm.value_ptr(pos))

        self.draw_axes()

    def rendering_loop(self, window, imgui_impl):
        shader_program = get_shader_program()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)

        vertices = np.array(
            [
                0.0,
                1.0,
                1.0,  # Top vertex
                -1.0,
                -1.0,
                1.0,  # Bottom-left vertex
                1.0,
                -1.0,
                1.0,  # Bottom-right vertex
            ],
            dtype=np.float32,
        )

        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)

        VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Define the vertex position attribute (location 0)
        glVertexAttribPointer(
            0, 3, GL_FLOAT, GL_FALSE, 3 * vertices.itemsize, ctypes.c_void_p(0)
        )
        glEnableVertexAttribArray(0)

        # Unbind VAO
        glBindVertexArray(0)

        while not self.window_should_close(window):
            self.update(shader_program)

            glBindVertexArray(VAO)
            glDrawArrays(GL_TRIANGLES, 0, 3)

            imgui.new_frame()
            imgui.begin("Sampling")

            imgui.end()

            imgui.render()
            self.imgui_impl.process_inputs()
            self.imgui_impl.render(imgui.get_draw_data())

            glfw.swap_buffers(window)
            glfw.poll_events()

        self.terminate()


def run():
    App((1280, 720), "The Force Awakens")
