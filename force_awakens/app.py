import io
import time
import importlib.resources
from queue import Empty

import glfw
import numpy as np
import pandas as pd

import imgui
from imgui.integrations.glfw import GlfwRenderer

from OpenGL.GL import *
from OpenGL.GLU import *

import force_awakens.mechanics
from force_awakens.graphics.draw import Background, BlackHole, Planet
from force_awakens.graphics.render import load_texture_simple
from force_awakens.mechanics.mechanics import add_body
from force_awakens.mechanics.colors import COLORS

# Drawing transformation array to transform OpenGL coordinates to right-handed physics coordinate system
T = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])

# Sets the axes for the simulation
_axes_y = np.mgrid[0:2, 0:1:11j, 0:1].T.reshape((-1, 3)) - [0.5, 0.5, 0.0]
_axes_x = _axes_y[:, [1, 0, 2]]


# main class for the simulation and usage of it
class App:
    def __init__(
        self,
        window_size,
        name,
        web,
        qr=None,
        vec_queue=None,
        zoom_sensitivity=0.1,
        pan_sensitvity=0.001,
        orbit_sensitivity=0.1,
        start_zoom=18,
    ):
        # Setting attributes of the class and starting conditions
        self.zoom_sensitivity = zoom_sensitivity
        self.pan_sensitvity = pan_sensitvity
        self.orbit_sensitivity = orbit_sensitivity

        # Camera movement conditions
        self.angle_x, self.angle_y = 20.0, 125.0
        self.pan_x, self.pan_y = 0.0, 0.0
        self.last_x, self.last_y = 0.0, 0.0
        self.dragging, self.panning = False, False
        self.zoom_level = start_zoom
        self.start_zoom = start_zoom

        # Calls the introductory zoom in from the start time
        self.start_time = time.time()
        self.intro = False

        self.view_left, self.view_right = 0, 0

        # Creates window and buttons
        self.window = self.window_init(window_size, name)
        self.imgui_impl = self.init_imgui(self.window)

        # Renders all items inside the window
        self.web = web
        if web:
            # Generate QR Code for web interactive demo
            # Attach as texture
            self.qr_tex = self._load_qr(qr)
            self.vec_queue = vec_queue

        # Preload buffers and textures of 
        # possible planets to add
        self._load_planets()

        # Start rendering
        self.rendering_loop(self.window, self.imgui_impl)

    def _load_qr(self, qr):
        img_data = qr.convert("RGBA").tobytes()
        width, height = qr.size
        
        # Bind QR as a texture for imgui rendering
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)

        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            width,
            height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            img_data,
        )

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        return texture_id, width, height

    def _load_planets(self):
        self.items = []

        # Imports and analyzes the csv containing information about planets which can be added
        binary = importlib.resources.read_binary(
            force_awakens.mechanics, "elements_in_space.csv"
        )
        df = pd.read_csv(io.BytesIO(binary))
        for _, row in df.iterrows():
            name = row["name_of_the_planet_stars"]
            type_ = row["type_of_celestial_body"]
            mass = row["masses_in_kg"]

            img_file = row["img_file"]

            if not pd.isna(img_file):
                # Buffer as texture of fixed size
                img_id, width, height = load_texture_simple(img_file, size=(140, 160))
            else:
                continue
            width, height = width // 2, height // 2

            # Appends the information from the csv to the items attribute of the app class
            self.items.append([name, type_, mass, (img_id, width, height)])

    def window_init(self, window_size, name):
        # Raises an exception if GLFW couldn't be initiated
        if not glfw.init():
            raise Exception("GLFW could not be initialized.")

        # Creates window
        glfw.window_hint(glfw.SAMPLES, 4)
        window = glfw.create_window(*window_size, name, None, None)
        if not window:
            glfw.terminate()
            raise Exception("GLFW window could not be created.")

        # Gets and uses information needed to maintain and update the window
        glfw.make_context_current(window)

        # Attach functions to callback 
        glfw.set_cursor_pos_callback(window, self.cursor_pos_callback)
        glfw.set_mouse_button_callback(window, self.mouse_button_callback)
        glfw.set_scroll_callback(window, self.scroll_callback)
        glfw.set_framebuffer_size_callback(window, self.resize_callback)

        # Most recent position of cursor
        self.last_x, self.last_y = glfw.get_cursor_pos(window)

        # Resizes window
        self.resize_callback(window, *window_size)

        return window

    def init_imgui(self, window):
        # Creates imgui context and renderer
        imgui.create_context()
        return GlfwRenderer(window, attach_callbacks=False)

    def mouse_button_callback(self, window, button, action, mods):
        # Forward imgui mouse events
        if self.imgui_impl != None and imgui.get_io().want_capture_mouse:
            return

        press = action == glfw.PRESS

        # If a given button is pressed, the screen inside the window is panned or rotated
        if button == glfw.MOUSE_BUTTON_LEFT:
            self.dragging = press
            shift = glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS
            self.panning = shift
        elif button == glfw.MOUSE_BUTTON_MIDDLE:
            self.dragging = press
            self.panning = press

    def cursor_pos_callback(self, window, xpos, ypos):
        # Forward imgui mouse events
        if self.imgui_impl != None and imgui.get_io().want_capture_mouse:
            return

        # If the cursor is dragging, updates the position of the cursor in the program
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
        # Forward imgui mouse events
        if self.imgui_impl != None and imgui.get_io().want_capture_mouse:
            return

        # Zooms in and out
        if yoffset > 0:
            self.zoom_level /= 1 + self.zoom_sensitivity
        elif yoffset < 0:
            self.zoom_level *= 1 + self.zoom_sensitivity

    def resize_callback(self, window, width, height):
        # Properly sizes the viewport window to the correct ratio
        glViewport(0, 0, width, height)

        # Ensure aspect ratio is always the same as window;
        # makes sure rendered objects aren't stretched
        aspect_ratio = width / height if height > 0 else 1.0
        self.view_left = -aspect_ratio
        self.view_right = aspect_ratio

    def draw_axes(self):
        glLineWidth(1.0)
        glBegin(GL_LINES)

        # Makes all the points in the x-axis and y-axis
        glColor3f(1.0, 1.0, 1.0)
        for point in _axes_x:
            glVertex3f(*(point) @ T)
        for point in _axes_y:
            glVertex3f(*point @ T)
        glEnd()

        # Draws the x/y/z axis grid
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

    def window_should_close(self, window):
        # Returns if the window should close
        return glfw.window_should_close(window)

    def terminate(self):
        # Terminates the window
        glfw.terminate()

    def update(self):
        # Clears the color and depth buffers upon update
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.05, 0.05, 0.05, 1.0)

        # Creates the orthogonal projection used by the camera
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(
            self.view_left * self.zoom_level,
            self.view_right * self.zoom_level,
            -self.zoom_level,
            self.zoom_level,
            -1024,
            1024,
        )

        # Governs the rotation and translation of the camera
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(self.pan_x, self.pan_y, 0.0)
        glRotatef(self.angle_x, 1.0, 0.0, 0.0)
        glRotatef(self.angle_y, 0.0, 1.0, 0.0)

    def update_intro(self):
        # Zooms into the window upon program commencing
        dt = time.time() - self.start_time
        if dt > 4.0:
            self.intro = False

        # Update the zoom_level depending on intro progress
        progress = (1 / (dt - 0.1)) ** 2 + 1
        self.zoom_level = progress * self.start_zoom

    def rendering_loop(
        self,
        window,
        imgui_impl,
        n_body=64,
        G=6.6743e-2,
        wanted=16,
        black_hole_r=1,
    ):
        # Initialises the masses, accelerations, velocities, and positions of n_body planets
        m = np.random.randint(10, 30, n_body)
        a = np.zeros((n_body, 3), dtype=np.float32)
        a_sum = np.zeros((n_body, 3), dtype=np.float32)
        v = np.random.randint(-1, 1, (n_body, 3)).astype(float)
        s = np.random.randint(-20, 20, (n_body, 3)).astype(float)

        # Initialises the lack of decay of any initial body
        decaying = np.zeros(n_body, dtype=bool)
        decay = np.ones(n_body, dtype=np.float32)

        # Sets the mass, velocity, and position of the central black hole
        m[0] = 800
        v[0] = 0
        s[0] = 0

        # Creates the size of all planets and black holes
        render_calls = [BlackHole(black_hole_r)]
        for i, r in enumerate(m):
            if i == 0:
                continue
            render_calls.append(Planet(r * 0.01))

        # Creates the mask to hide all non-desired planets
        mask = np.zeros(n_body, dtype=bool)
        for i in range(wanted):
            mask[i] = True

        # enable depth and occlusion
        glEnable(GL_DEPTH_TEST)

        # enable antialiasing (smooth lines)
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_POINT_SMOOTH)

        # enable opacity
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

        # Generates the stars in the background of the window
        background = Background()

        # Starts
        start = time.time()
        dt = 0

        draw_background, draw_dense = True, True

        while not self.window_should_close(window):
            # Updates the introdution
            if self.intro:
                self.update_intro()
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glClearColor(0.05, 0.05, 0.05, 1.0)

            # Updates the window, background, and axes
            self.update()

            # Sets the acceleration that will be added to so that all
            # accelerations, velocities, and positions can be updated simultaneously
            a_sum[:] = a

            for body in range(n_body):
                for j in range(n_body):
                    # skip current body,
                    # and bodies that are masked
                    if j == body:
                        continue
                    if not mask[j]:
                        continue

                    # For every body is being shown, will do the following for every other body:

                    s_a, s_b = s[body], s[j]

                    # Determines the distance between the mass that is being analyzed and each other body
                    ds = s_b - s_a
                    d = np.linalg.norm(ds)

                    # If the distance between the two masses is too small,
                    # will mask the second mass
                    # and add it's properties to the original mass
                    if d < 0.05:
                        m[body] = m[body] + m[j]
                        a[body] += a[j]
                        v[body] += v[j]

                        mask[j] = False
                    else:
                        m_a = m[body]
                        F_a = np.zeros(3, dtype=np.float32)

                        # Calculates the force of gravity
                        # on the body for every other body,
                        # and adds it to the total for that body
                        m_b = m[j]
                        Fg = G * m_a * m_b / d**2

                        F_a += ds / d * Fg
                        a_sum[body] += F_a

                    # If the body is too close to the black hole,
                    # commences it's decay animation
                    if body != 0 and np.linalg.norm(s_a) < black_hole_r:
                        decaying[body] = True

                # Continually decays the trails of all bodies that
                # have entered the black hole until they disappear
                if decaying[body]:
                    decay[body] *= 0.95
                    v[body] = 0
                    if decay[body] < 0.05:
                        decaying[body] = False
                        decay[body] = 1.0
                        mask[body] = False

            # If the body is not masked and is not decaying, 
            # then new accelerations,
            # velocities, and positions are calculated for it
            m_phys = mask & (~decaying)
            a[m_phys] = a_sum[m_phys] / m[m_phys, np.newaxis]
            v[m_phys] = a[m_phys] * dt + v[m_phys]
            s[m_phys] = v[m_phys] * dt + s[m_phys]

            # Resets the position and velocity of the black hole to zero,
            # to ensure it doesn't move, and sets the it's mask to True so that
            #v[0] = 0
            #s[0] = 0
            mask[0] = True

            # Creates a new frame
            imgui.new_frame()
            imgui.begin("The Force Awakens")

            # options to render stars and black hole stars
            _, draw_background = imgui.checkbox(
                "Draw background stars", draw_background
            )
            _, draw_dense = imgui.checkbox("Draw orbiting stars", draw_dense)

            # make appropriate render calls for stars
            if draw_background:
                background.draw()
            render_calls[0].draw_dense = draw_dense

            # Renders every body that is not masked
            for body in range(n_body):
                if not mask[body]:
                    continue
                render_calls[body].draw(s[body], start, decay[body])

            # Shows the fps and number of bodies currently unmasked
            if dt:
                imgui.text(f"{1/dt:.2f} fps")
            imgui.text(f"{np.sum(mask)} bodies")

            def draw_new(color, r):
                draw_i = add_body(
                    render_calls,
                    mask,
                    s,
                    v,
                    self.zoom_level,
                    (self.pan_x, self.pan_y),
                )
                # Render the planet and sizes
                # aka draw new planet, and renable mask
                render_obj = render_calls[draw_i]
                render_obj.set_color(color)
                render_obj.r = r * 0.01
                m[draw_i] = r
                decaying[draw_i] = False
                decay[draw_i] = 1.0

            def imgui_stuff():
                imgui.spacing()
                imgui.spacing()

                # initialize a imgui table to display all of the images and infos
                # of possible planets to add
                w = imgui.get_content_region_available_width()
                if imgui.begin_table("Please chose your celestial body !", 2):
                    imgui.table_setup_column(
                        "Images", imgui.TABLE_COLUMN_WIDTH_FIXED, w // 3
                    )
                    imgui.table_setup_column(
                        "Infos", imgui.TABLE_COLUMN_WIDTH_FIXED, 2 * w // 3
                    )
                    imgui.table_headers_row()

                    selection = np.zeros(len(self.items), dtype=bool)
                    # iterate trough each characteristics of the planets
                    # and display them on the screen (images for this section)
                    for i, item in enumerate(self.items):
                        imgui.table_next_row()
                        imgui.spacing()
                        imgui.table_next_column()
                        name, body_type, mass, (id, width, height) = item
                        imgui.image(id, width, height)

                        imgui.table_next_column()
                        # itterate trough each characteristics of the planets
                        # and display them on the screen (mass, name and type for this section)
                        selection[i] = imgui.button(f"Select {name}")
                        imgui.text(name)
                        imgui.text(f"  Mass: {mass:.4g} kg")
                        imgui.text(f"  Type: {body_type}")
                        imgui.separator()

                    # if any planet is selected in the table
                    if np.any(selection):
                        # Adds selected planet into the simulation
                        i = np.argmax(selection)
                        name, _, mass, _ = self.items[i]
                        print(f"body added {name}")
                        draw_new(COLORS[i], np.log10(float(mass)))

                    # put an end to the table
                    imgui.end_table()
                # render the image and complete its "loop"
                imgui.end()

                # if web is enabled, draw QR code for clients to
                # connect to the flask server
                if self.web:
                    imgui.begin("Web QR")
                    imgui.image(*self.qr_tex)
                    imgui.end()

                    try:
                        # if received new throw vector from user,
                        # add new planet
                        self.vec_queue.get_nowait()
                        r = np.random.uniform(10, 80)
                        draw_new([1, 1, 1], r)
                    except Empty:
                        pass
                    
                # render ui
                imgui.render()
                imgui_impl.process_inputs()
                imgui_impl.render(imgui.get_draw_data())
            imgui_stuff()

            # swap framebuffers and render screen
            glfw.swap_buffers(window)
            glfw.poll_events()

            current = time.time()
            dt = current - start
            start = current

        self.terminate()


# run the app
def run(web, qr=None, vec_queue=None):
    if web:
        App((1920, 1080), "The Force Awakens", web, qr=qr, vec_queue=vec_queue)
    else:
        App((1920, 1080), "The Force Awakens", web, qr=qr)
