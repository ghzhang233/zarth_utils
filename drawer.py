import os
import sys

from matplotlib.figure import Figure

from zarth_utils.general_utils import get_random_time_stamp, makedir_if_not_exist

dir_figures = os.path.join(sys.path[0], "figures")
makedir_if_not_exist(dir_figures)


class Drawer:
    def __init__(self, figsize=(6.4, 4.8)):
        self.figure = Figure(figsize=figsize)

    def draw_one_axes(self, x, y, labels=None, *, nrows=1, ncols=1, index=1, title="", xlabel="", ylabel="",
                      use_marker=False):
        ax = self.figure.add_subplot(nrows, ncols, index)

        format_generator = self.get_format(use_marker)
        for i, yi in enumerate(y):
            fmt = next(format_generator)
            if labels is not None:
                ax.plot(x, yi, fmt, label=labels[i])
            else:
                ax.plot(x, yi, fmt)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        if labels is not None:
            ax.legend()

    def show(self):
        self.figure.show()

    def save(self, fname=None):
        if fname is None:
            fname = get_random_time_stamp()
        fname = "%s.jpeg" % fname if not fname.endswith(".config") else fname
        self.figure.savefig(os.path.join(dir_figures, fname))

    def clear(self):
        self.figure.clf()

    @staticmethod
    def get_format(use_marker=False):
        p_color, p_style, p_marker = 0, 0, 0
        colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k', 'w']
        styles = ['-', '--', '-.', ':']
        markers = [""]
        if use_marker:
            markers += ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', 'P', '*', 'h', 'H', '+',
                        'x', 'X', 'D', 'd', '|', '_', ]

        while True:
            yield colors[p_color] + styles[p_style] + markers[p_marker]
            p_color += 1
            p_style += 1
            p_marker += 1
            p_color %= len(colors)
            p_style %= len(styles)
            p_marker %= len(markers)
