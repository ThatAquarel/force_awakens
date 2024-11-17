### Force_Awakens


## Authors : 

Just students trying to make science, especially it's more advanced topics more approachable for everyone.

Tian Yi Xia, Thomas Deleuze-Bisson, Evan Parasol

Dawson College, Montréal

![image](https://github.com/user-attachments/assets/3cb84f17-91aa-46a1-8e5e-d2c0823da192)


## A little bit about us,

Hi, we're three Dawson College Students in the Enriched Science Program. As we share various common passions such as programming, physics, space and math, we've decided to participate in the 2024 Edition of the McGill University Physics Hackaton. Ever since we had figured out that astrophysics was a field that scared most people because of its complexity, we decided to make it our mission to demonstrate it in the simplest way possible and what better way to do so than to make an accessible, fun and diverse sandbox in which the powers of graviationnal fields, forces and accelerations can be observed.

## Our idea

For this hackathon, our idea was to take the wonder of space and the beauty of orbital mechanics, and to make them visible to the eyes of anyone by implementing a program that visualises the orbits of celestial bodies around a black hole. Additionally, we wanted to make it so that the mass and gravitational pull of the black hole increased as it consumes the bodies that are orbiting it, to mirror how that happens in reality. Lastly, we wanted to make this more interactive and engaging for users, and so we decided to implement a mechanism whereby the user can launch planets with masses and velocities into the system, so as to continually have more interactions between celestial bodies, the black hole, and each other.

## Project Structure

- `force_awakens/`:
    - `graphics/`:
        - `draw.py`:
        - `render.py`:
    - `images/`:
    - `mechanics/`:
        - `mechanics.py`:
    - `__main__.py`:
    - `app.py`:
    - `rgb.txt`:
- `elements_in_space.csv`:
- `imgui.ini`:
- `setup.py`:
- `stars_selected_test.py`:

## Requirements

The requirements for running the code are as follows:
- time == version?
- glfw == version?
- numpy == version?
- imgui == version?
- OpenGL.GL == version?
- OpenGL.GLU == version?
- importlib == version?
- io == version?
- math == version?
- jekyll-remote-theme ??????

## How it works

There are many steps to completing this project. First obviously was to gather data of various planets and other celestial bodies across our universe such as exoplanets, stars, etc. We did that by using many tools such as Nasa's Eyes on Exoplanets projects which gives us an accurate representation of what each known star and exoplanet looks like which abled us to draw their visual models. For planets from the Star Wars Universe, we looked trough various fan websites, approximations and even quotes from the movie to get our data (mass,size,etc). Once we had these ressources, we then created many csv and txt files organizing their colors in order to be able to plug them in our actual black hole model. Another step of the process was to code the interface used to select the planets which was done using imgui, a super useful website-building python library, allowing us to design an modern and easy to exchange informations with the user.


## Result

images will go here

<!-- # What our projects consist of...

We've designed, as mentionned earlier, a sandbox where it is possible for users to add all sorts of celestial bodies ranging from black holes to various exoplanets, even including a few ones from you favorite shows in order to observe their graviationnal influence over each other in a neutral spatial environment and create an interesting and visual learning experience for the user. We think that such a project makes science more accessible to everyone as sometimes, just a visual representation of something makes us understand a concept so much better.

# How it works

Now let's get into the interesting part; how the project works ! First, lets deconstruct it into a few steps... 1. Exoplanets scouting, gathering of data and accurate representation of celestial bodies, 2. Development of an 3d gravity neutral envrionment to oberve the behavior of planets using OpenGL, 3. Implementation of matrices to evaluate the "planet throwing" feature of our project using linear algebra.

# 1. Data gathering

We started by looking on various NASA websites for exoplanets and information about them, such as mass, radius, and distance from the earth. Then we began researching the various libraries that we would plan to use in the making of our project, such as openGL, glfw, and imgui. Finally, we researched the information that would be needed to simulate gravity between celestial bodies, as well as attempting to figure out methods of properly displaying black holes.

# 2. Creation of the three dimensionnal environment

# 3. Implementation of linear algebra to solve an interesting problem

<<<<<<< HEAD
 -->
=======
# Contact

- [Tian Yi, Xia](https://github.com/ThatAquarel/space), xtxiatianyi@gmail.com: 
- [Thomas, Deleuze-Bisson](https://github.com/Thomas4534), deleuzethomasbisson@gmail.com: 
- [Evan Parasol](https://github.com/TheBookwyrms), blackdragon6493@gmail.com: 


# References

1. Rohlfs, M., & Pohl, T. (2009). Quantum dots in semiconductor nanostructures: From basic physics to quantum technologies. Proceedings of the National Academy of Sciences, 106(47), 20129-20134. https://doi.org/10.1073/pnas.0910927107
2. Kisa, M. (n.d.). Rotations and rotation matrices. Retrieved from http://pajarito.materials.cmu.edu/documents/Kisa.Papers/Rotations%20and%20rotation%20matrices.pdf
3. X-Engineer. (n.d.). Euler integration. X-Engineer. Retrieved November 16, 2024, from https://x-engineer.org/euler-integration/
4. Takahashi, R., & Uchida, H. (2016). Relativistic MHD simulations of black hole systems. Physics of Fluids, 28(11), 110701. https://doi.org/10.1063/1.4964783
5. Zhang, L., & Wu, H. (2023). "Research on Enhanced Orbit Prediction Techniques Utilizing Multiple Sets of Two-Line Element (TLE)." Journal of Spacecraft and Rockets, 60(5), 1181-1196. DOI: 10.2514/1.A34658
6. National Oceanic and Atmospheric Administration (NOAA) and Joint Center for Satellite Data Assimilation (JCSDA). "Orbit Simulator for Satellite and Near-Space Platforms." NOAA Technical Report, 2021. DOI: 10.1016/j.ejpra.2020.100054
7. NASA Jet Propulsion Laboratory. (2020). Eyes on Exoplanets. NASA. Retrieved November 16, 2024, from https://eyes.nasa.gov


>>>>>>> dcf09b55569601a7284dd3985dd0a1f8fd845286
