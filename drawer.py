import os
import sys

import matplotlib.pyplot as plt

from zarth_utils.general_utils import get_random_time_stamp, makedir_if_not_exist

dir_figures = os.path.join(sys.path[0], "figures")
makedir_if_not_exist(dir_figures)


class Drawer:
    def __init__(self):
        self.figure = plt.figure()

    def draw_one_axes(self, x, y, labels=None, *, nrows=1, ncols=1, index=1, title="", xlabel="", ylabel=""):
        ax = self.figure.add_subplot(nrows, ncols, index)

        format_generator = self.get_format()
        for i, yi in enumerate(y):
            fmt = next(format_generator)
            print(fmt)
            if labels is not None:
                ax.plot(x, yi, fmt, labels=labels[i])
            else:
                ax.plot(x, yi, fmt)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        if labels is not None:
            ax.legend()

    def show(self):
        self.figure.show()

    def save(self, fname=get_random_time_stamp()):
        fname = "%s.jpeg" % fname if not fname.endswith(".config") else fname
        self.figure.savefig(os.path.join(dir_figures, fname))

    def clear(self):
        self.figure.clf()

    @staticmethod
    def get_format():
        p_color, p_style, p_marker = 0, 0, 0
        colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']
        styles = ['-', '--', '-.', ':']
        markers = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', 'P', '*', 'h', 'H', '+', 'x',
                   'X', 'D', 'd', '|', '_', ]

        while True:
            yield colors[p_color] + styles[p_style] + markers[p_marker]
            p_color += 1
            p_style += 1
            p_marker += 1
            p_color %= len(colors)
            p_style %= len(styles)
            p_marker %= len(markers)
