import os
import struct
import time
from PIL import Image
import glfw
import numpy as np
import pandas as pd
import imgui
from imgui.integrations.glfw import GlfwRenderer

from OpenGL.GL import *
from OpenGL.GLU import *


def load_texture_simple(image_path):
    image = Image.open(image_path)
    img_data = image.convert("RGBA").tobytes()
    width, height = image.size

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture_id, width, height

angle_x, angle_y = 45.0, 45.0
pan_x, pan_y = 0.0, 0.0
last_x, last_y = 0.0, 0.0
dragging = False
panning = False
zoom_level = 1.0
imgui_impl = None
viewport_left = 0
viewport_right = 0


def mouse_button_callback(window, button, action, mods):
    global dragging, panning, imgui_impl

    if imgui_impl != None and imgui.get_io().want_capture_mouse:
        return

    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            dragging = True
            panning = False
        elif action == glfw.RELEASE:
            dragging = False
    elif button == glfw.MOUSE_BUTTON_MIDDLE:
        if action == glfw.PRESS:
            dragging = True
            panning = True
        elif action == glfw.RELEASE:
            dragging = False
            panning = False


def cursor_pos_callback(window, xpos, ypos):
    global last_x, last_y, angle_x, angle_y, pan_x, pan_y, dragging, panning, imgui_impl

    if imgui_impl != None and imgui.get_io().want_capture_mouse:
        return

    if dragging:
        dx = xpos - last_x
        dy = ypos - last_y
        if panning:
            pan_x += dx * 0.001
            pan_y -= dy * 0.001
        else:
            angle_x += dy * 0.1
            angle_y += dx * 0.1
    last_x, last_y = xpos, ypos


def scroll_callback(window, xoffset, yoffset):
    global zoom_level, imgui_impl

    if imgui_impl != None and imgui.get_io().want_capture_mouse:
        return

    zoom_factor = 0.1
    if yoffset > 0:
        zoom_level /= 1 + zoom_factor  # Zoom in
    elif yoffset < 0:
        zoom_level *= 1 + zoom_factor  # Zoom out


def resize_callback(window, width, height):
    glViewport(0, 0, width, height)

    global viewport_left, viewport_right
    aspect_ratio = width / height if height > 0 else 1.0
    viewport_left = -aspect_ratio
    viewport_right = aspect_ratio


T = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])


_axes_y = np.mgrid[0:2, 0:1:11j, 0:1].T.reshape((-1, 3)) - [0.5, 0.5, 0.0]
_axes_x = _axes_y[:, [1, 0, 2]]


def draw_axes():
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


aruco_point_color = np.array(
    [[0.92, 0.26, 0.21], [0.20, 0.66, 0.33], [0.26, 0.52, 0.96], [0.98, 0.74, 0.02]]
)


def draw_points(points):
    glPointSize(4.0)
    glBegin(GL_POINTS)

    for i, point in enumerate(points):
        glColor3f(*aruco_point_color[i % aruco_point_color.shape[0]])
        glVertex3f(*point @ T)

    glEnd()


def init():
    window_size = (800, 800)

    global last_x, last_y

    if not glfw.init():
        raise Exception("GLFW could not be initialized.")

    window = glfw.create_window(*window_size, "position", None, None)
    if not window:
        glfw.terminate()
        raise Exception("GLFW window could not be created.")

    glfw.make_context_current(window)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_scroll_callback(window, scroll_callback)
    glfw.set_framebuffer_size_callback(window, resize_callback)

    last_x, last_y = glfw.get_cursor_pos(window)

    resize_callback(window, *window_size)

    return window


def init_imgui(window):
    global imgui_impl
    imgui.create_context()
    imgui_impl = GlfwRenderer(window, attach_callbacks=False)
    return imgui_impl


def window_should_close(window):
    return glfw.window_should_close(window)


def terminate():
    glfw.terminate()


def update():
    global viewport_left, viewport_right

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0.86, 0.87, 0.87, 1.0)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(
        viewport_left * zoom_level,
        viewport_right * zoom_level,
        -zoom_level,
        zoom_level,
        -1,
        1,
    )

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(pan_x, pan_y, 0.0)
    glRotatef(angle_x, 1.0, 0.0, 0.0)
    glRotatef(angle_y, 0.0, 1.0, 0.0)

    draw_axes()


def main(buffer_size=2048, sample_dt_buffer_size=128):
    window = init()
    imgui_impl = init_imgui(window)

    sample_total = 0
    n, prev_n = 0, buffer_size - 1
    sample_buffer = np.empty((buffer_size, 6), dtype=np.float64)
    dt_buffer = np.empty(buffer_size, dtype=np.float64)

    dt_i = 0
    sample_dt_buffer = np.zeros(sample_dt_buffer_size, dtype=np.float32)
    prev_time = time.time()



    items = []

    df = pd.read_csv("elements_in_space.csv")
    for index, row in df.iterrows():
        name = row["name_of_the_planet_stars"]
        type_ = row["type_of_celestial_body"]
        mass = row["masses_in_kg"]

        img_file = row["img_file"]

        if not pd.isna(img_file):
            img_id, width, height = load_texture_simple(img_file)
        else:
            continue
        width, height = width // 2, height // 2

        items.append([
            name, type_, mass, (img_id, width, height)
        ])

    while not window_should_close(window):
        planet = None
        update()
        imgui.new_frame()
        imgui.begin("Stars Selector", True)

        imgui.begin_table("Please chose your celestial body !", 3)

        imgui.table_setup_column("Images")
        imgui.table_setup_column("Infos")
        imgui.table_headers_row()


        selection = np.zeros(len(items), dtype=bool)

        for i, item in enumerate(items):
            imgui.table_next_row()
            imgui.table_next_column()
            name, type_, mass, (id,width,height) = item
            imgui.image(id,width,height)

            imgui.table_next_column()

            selection[i] = imgui.button(f"Select {name}")
            imgui.text(name)
            imgui.text(f"mass : {mass} kg")
            imgui.text(f"Type : {type_}")

        if np.any(selection):
            selected_i = np.argmax(selection)
            print(items[selected_i][0])


        imgui.end_table()
        imgui.end()
        imgui.render()
        imgui_impl.process_inputs()
        imgui_impl.render(imgui.get_draw_data())

        glfw.swap_buffers(window)
        glfw.poll_events()
    terminate()


if __name__ == "__main__":
    main()
