import time

import glfw
import numpy as np

import imgui
from imgui.integrations.glfw import GlfwRenderer

from OpenGL.GL import *
from OpenGL.GLU import *

from force_awakens.graphics.draw import Planet


T = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])


_axes_y = np.mgrid[0:2, 0:1:11j, 0:1].T.reshape((-1, 3)) - [0.5, 0.5, 0.0]
_axes_x = _axes_y[:, [1, 0, 2]]

class App:
    def __init__(
        self,
        window_size,
        name,
        zoom_sensitivity=0.1,
        pan_sensitvity=0.001,
        orbit_sensitivity=0.1,
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
            glVertex3f(*(point) @ T)
        for point in _axes_y:
            glVertex3f(*point @ T)
        glEnd()

        glLineWidth(2.0)
        glBegin(GL_LINES)

        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(*[-0.5, 0.0, 0.0] @ T)
        glVertex3f(*[0.5, 0.0, 0.0] @ T)

        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(*[0.0, -0.5, 0.0] @ T)
        glVertex3f(*[0.0, 0.5, 0.0] @ T)

        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(*[0.0, 0.0, -0.5] @ T)
        glVertex3f(*[0.0, 0.0, 0.5] @ T)

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

    def update(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.05, 0.05, 0.05, 1.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(
            self.view_left * self.zoom_level,
            self.view_right * self.zoom_level,
            -self.zoom_level,
            self.zoom_level,
            -128,
            128,
        )

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(self.pan_x, self.pan_y, 0.0)
        glRotatef(self.angle_x, 1.0, 0.0, 0.0)
        glRotatef(self.angle_y, 0.0, 1.0, 0.0)

        self.draw_axes()
    


    def rendering_loop(self, window, imgui_impl, max_bodies=64, G=6.6743e-2):

        m = np.random.randint(1, 10, max_bodies)
        a = np.zeros((max_bodies, 3), dtype=np.float32)
        a_cumulative = np.zeros((max_bodies, 3), dtype=np.float32)
        v = ((np.random.random([max_bodies, 3]))*1)*((np.random.randint(0, 1, 3) *2)-1)
        s = np.random.randint(-3, 3, (max_bodies, 3)).astype(float)

        n_body = 15

        radius = [1,2,3,4,5,6,7]
        radius = np.random.randint(1, 5, max_bodies)
        # render_calls = [Planet(r * 0.01) for r in radius]
        render_calls = [Planet(r * 0.01) for r in m]
        render_mask = np.zeros(max_bodies, dtype=bool)
        render_mask[0:n_body] = True

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)

        start = time.time()
        dt = 0

        while not self.window_should_close(window):
            self.update()

            # accelerations = {}
            # for body in range(max_bodies):
            #     if not render_mask[body]:
            #         accelerations[body] = a[body]

            a_cumulative[:] = a

            for body in range(max_bodies):
                if not render_mask[body]:
                    for j in range(n_body):
                        if j == body:
                            continue

                        s_a, s_b = s[body], s[j]
                        ds = s_b - s_a
                        d = np.linalg.norm(ds)
                        
                        if d < 0.05:
                            m[body] = m[body] + m[j]
                            a[body] += a[j]
                            v[body] += v[j]
                            m[j] = 0
                            a[j] = np.zeros(3, dtype=np.float32)
                            v[j] = np.zeros(3, dtype=np.float32)
                            s[j] = np.zeros(3, dtype=np.float32)

                            render_mask[j] = False
                        else:
                            F_a = np.zeros(3, dtype=np.float32)

                            Fg = G * m[body] * m[j] / d**2

                            F_a += ds / d * Fg
                            a_cumulative[body] += F_a

            for body in range(max_bodies):
                if not render_mask[body]:
                    continue

                a[body] = a_cumulative[body] / m[body]
                v[body] = a[body] * dt + v[body]
                s[body] = v[body] * dt + s[body]

                render_calls[body].draw(s[body])

                # glPointSize(m[body] * 10)
                # glBegin(GL_POINTS)
                # glColor3f(1, 1, 1)
                # glVertex3f(*s[body] @ T)
                # glEnd()

            glfw.swap_buffers(window)
            glfw.poll_events()

            current = time.time()
            dt = current - start
            start = current

        self.terminate()


def run():
    App((1280, 720), "The Force Awakens")
