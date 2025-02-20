import matplotlib
import matplotlib.pyplot as plt
import numpy

matplotlib.use('Qt5Agg')

hl, = plt.plot([], [])
plt.show()


def update_line(new_data):
    global hl
    hl.set_xdata(numpy.append(hl.get_xdata(), new_data))
    hl.set_ydata(numpy.append(hl.get_ydata(), new_data))
    plt.draw()