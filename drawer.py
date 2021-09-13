import os
import numpy as np

from matplotlib.figure import Figure

from zarth_utils.general_utils import get_random_time_stamp, makedir_if_not_exist

dir_figures = os.path.join(os.getcwd(), "figures")
makedir_if_not_exist(dir_figures)


class Drawer:
    def __init__(self, figsize=(6.4, 4.8)):
        """
        Init the drawer with the given figsize.
        :param figsize: (width, height)
        :type figsize: (float, float)
        """
        self.figure = Figure(figsize=figsize)

    def draw_one_axes(self, x, y, labels=None, *, nrows=1, ncols=1, index=1, title="", xlabel="", ylabel="",
                      use_marker=False):
        """
        Draw one axes, which can be understood as a sub-figure.
        :param x: the data for x axis
        :type x: list
        :param y: the data for y axis
        :type y: ``list'' for single ``line of list'' of list for multiple lines
        :param labels: the list of labels of each line
        :type labels: list
        :param nrows: the number of rows in the figure
        :type nrows: int
        :param ncols: the number of columns in the figure
        :type ncols: int
        :param index: The subplot will take the index position on a grid with nrows rows and ncols columns.
        :type index: int
        :param title: the title of the axes
        :type title: str
        :param xlabel: the label for x axis
        :type xlabel: str
        :param ylabel: the label for x axis
        :type ylabel: str
        :param use_marker: whether use markers to mark the points, default=False
        :type use_marker: bool
        :return:
        :rtype:
        """
        ax = self.figure.add_subplot(nrows, ncols, index)

        format_generator = self.get_format(use_marker)
        for i, yi in enumerate(y):
            len_no_nan = 0
            while len_no_nan < len(yi) and not (np.isnan(yi[len_no_nan]) or np.isinf(yi[len_no_nan])):
                len_no_nan += 1
            if len_no_nan == 0:
                continue

            fmt = next(format_generator)

            if labels is not None:
                ax.plot(x[:len_no_nan], yi[:len_no_nan], fmt, label=labels[i])
            else:
                ax.plot(x[:len_no_nan], yi[:len_no_nan], fmt)

        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        if labels is not None:
            ax.legend()

    def show(self):
        """
        To show the figure.
        """
        self.figure.show()

    def save(self, fname=None):
        """
        To save the figure as fname.
        :param fname: the filename
        :type fname: str
        """
        if fname is None:
            fname = get_random_time_stamp()
        fname = "%s.jpeg" % fname if not fname.endswith(".config") else fname
        self.figure.savefig(os.path.join(dir_figures, fname))

    def clear(self):
        """
        Clear the figure.
        """
        self.figure.clf()

    @staticmethod
    def get_format(use_marker=False):
        """
        Get the format of a line.
        :param use_marker: whether use markers for points or not.
        :type use_marker: bool
        """
        p_color, p_style, p_marker = 0, 0, 0
        colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
        styles = ['-', '--', '-.', ':']
        markers = [""]
        if use_marker:
            markers = ['o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', 'P', '*', 'h', 'H', '+',
                       'x', 'X', 'D', 'd', '|', '_', ]

        while True:
            yield colors[p_color] + styles[p_style] + markers[p_marker]
            p_color += 1
            p_style += 1
            p_marker += 1
            p_color %= len(colors)
            p_style %= len(styles)
            p_marker %= len(markers)
