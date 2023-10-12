import pygame as pg
import numpy as np
import sys
import time


class Simulation:
    def __init__(self, system_y, system_x):
        pg.init()
        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode(screen_size)
        self.background = pg.Surface(self.screen.get_size())
        self.background.fill(pg.Color('black'))
        self.system_y = system_y
        self.system_x = system_x
        time.sleep(5)

    def update(self):
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            self.logic()
            self.screen.fill(pg.Color('black'))
            self.screen.blit(self.background, (0, 0))
            self.draw()
            pg.display.flip()
            self.clock.tick(60)

    def draw(self):
        self.system_y[0].draw(self.screen, self.background)
        self.system_y[-1].draw_y(self.screen)

        self.system_x[0].draw(self.screen, self.background)
        self.system_x[-1].draw_x(self.screen)

        pg.draw.circle(self.background, pg.Color('red'),
                       np.array([self.system_x[-1].end[0], self.system_y[-1].end[1]]), 1)
        pg.draw.line(self.background, pg.Color('red'),
                     np.array([self.system_x[-1].end[0], self.system_y[-1].end[1]]),
                     np.array([self.system_x[-1].previous_end[0], self.system_y[-1].previous_end[1]]), 3)

    def logic(self):
        self.system_y[0].rotate()
        self.system_x[0].rotate()


def dft(signal):
    n = len(signal)
    x = np.zeros([n, 2])
    y = np.zeros([n, 3])  # Amplitude, frequency, phase
    for k in range(n):
        for index in range(n):
            phi = -np.pi * 2 * k * index / n
            x[k, 0] += signal[index] * np.cos(phi)
            x[k, 1] += signal[index] * np.sin(phi)
        x[k, 0] /= n
        x[k, 1] /= n
        y[k] = np.array([np.linalg.norm(x[k]), k, np.arctan2(x[k, 1], x[k, 0])])
    return y


class EpiCycle:
    def __init__(self, start, amplitude, frequency, phase):
        self.start = start
        self.amp = amplitude
        self.freq = frequency
        self.angle = phase
        self.end = self.start + self.amp * np.array([np.cos(self.angle), np.sin(self.angle)])
        self.connection = None
        self.draw_tip = False
        self.previous_end = self.end

    def rotate(self):
        self.angle += self.freq * dt
        self.previous_end = self.end
        self.end = self.start + self.amp * np.array([np.cos(self.angle), np.sin(self.angle)])
        if self.connection:
            self.connection.start = self.end
            self.connection.rotate()

    def connect(self, other):
        other.start = self.end
        self.connection = other

    def draw(self, screen, background):
        pg.draw.line(screen, pg.Color('white'), self.start, self.end, 1)
        pg.draw.circle(screen, pg.Color('gray'), self.start, self.amp, 1)
        if self.connection:
            self.connection.draw(screen, background)

    def draw_x(self, screen):
        pg.draw.line(screen, pg.Color('gray'), self.end, np.array([self.end[0], screen_size[1]]))

    def draw_y(self, screen):
        pg.draw.line(screen, pg.Color('gray'), self.end, np.array([screen_size[0], self.end[1]]))


def generate_system(values, start, phase_diff):
    system = [EpiCycle(start, values[0, 0], values[0, 1], values[0, 2])]
    for i in range(1, len(values)):
        new_epicycle = EpiCycle(system[i-1].end, values[i, 0], values[i, 1], values[i, 2] + phase_diff)
        system[i-1].connect(new_epicycle)
        system.append(new_epicycle)
    system[-1].draw_tip = True
    return system


if __name__ == '__main__':
    screen_size = np.array([2000, 1000])
    txt_file = np.loadtxt('signal.txt', delimiter=',', dtype=int)
    # You may need to modify x and y signals
    x_signal = txt_file[:, 0] - 200
    y_signal = txt_file[:, 1]
    vals_x = dft(x_signal)
    vals_y = dft(y_signal)
    dt = 2 * np.pi / len(x_signal)
    system_of_fourier_x = generate_system(vals_y, np.array([200, 600]), np.pi/2)
    system_of_fourier_y = generate_system(vals_x, np.array([1100, 200]), 0)

    simulation = Simulation(system_of_fourier_x, system_of_fourier_y)
    simulation.update()
