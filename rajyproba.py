import datetime
import random

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import socket
import threading

insulin = []
bg = []
meal = []
timestamp = []

def read_temperature():
    """Read temperature (stub here of course)
    :return: the temperature
    """
    return random.uniform(10, 30)


def connection():
    global insulin,bg,meal,timestamp
    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind(('127.0.0.1', 34000))  # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(1)
    conn, address = server_socket.accept()  # accept new connection
    print("Connection from: " + str(address))
    while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        data = conn.recv(1024).decode()
        if not data:
            # if data is not received break
            break
        print("from connected user: " + str(data))
        for adat in data.split(" "):
            adatok = adat.split("-")
            if adatok[0]=='in':
                insulin.append(float(adatok[1]))
            if adatok[0]=='bg':
                bg.append(float(adatok[1]))
            if adatok[0]=='me':
                meal.append(float(adatok[1]))
            if adatok[0]=='ti':
                timestamp.append(adatok[1])
        #data = input(' -> ')
        #conn.send(data.encode())  # send data to the client
        print(meal)
        print(insulin)
        print(bg)

    conn.close()


def animate(frame, xs, ys):
    """Function called periodically by the Matplotlib as an animation.
    It reads a new temperature value, add its to the data series and update the plot.
    :param frame: not used
    :param xs: x data
    :param ys: y data
    """

    # Read temperature
    #temperature = read_temperature()

    # Add x and y to lists

    #ys.append(temperature)

    # Limit x and y lists to the more recent items

    if len(xs)>288:
        size_limit = 288
    else:
        size_limit = len(xs)
    xs = xs[-size_limit:]
    ys = ys[-size_limit:]

    # Draw x and y lists
    ax2.clear()
    ax2.plot(xs, ys)

    # (Re)Format plot
    ax2.grid()
    for tick in ax2.get_xticklabels():
        tick.set_rotation(45)
    for s, d in zip(ax2.get_xticks(), ys):
        ax2.annotate("{:.2f}".format(d), xy=(s, d))
    #plt.xticks(rotation=45, ha='right')
    #plt.subplots_adjust(bottom=0.30)
    ax2.set_xlabel("Time")
    ax2.set_ylabel("U/hr")
    ax2.set_title('Insulin')
    # fig.ylabel('Values')
    # fig.xlabel('Time')
    #ax.legend(bbox_to_anchor=(0.75, 1.15), ncol=3)
    #plt.title('Insulin')
    #plt.ylabel('U/hr')
    #plt.xlabel('Time')
    #plt.legend(loc="lower right")

def animate3(frame, xs, ys):
    """Function called periodically by the Matplotlib as an animation.
    It reads a new temperature value, add its to the data series and update the plot.
    :param frame: not used
    :param xs: x data
    :param ys: y data
    """

    # Read temperature
    #temperature = read_temperature()

    # Add x and y to lists

    #ys.append(temperature)

    # Limit x and y lists to the more recent items

    if len(xs)>288:
        size_limit = 288
    else:
        size_limit = len(xs)
    xs = xs[-size_limit:]
    ys = ys[-size_limit:]

    # Draw x and y lists
    ax3.clear()
    ax3.plot(xs, ys)

    # (Re)Format plot
    ax3.grid()
    for tick in ax3.get_xticklabels():
        tick.set_rotation(45)
    for s, d in zip(ax3.get_xticks(), ys):
        ax3.annotate("{:.2f}".format(d), xy=(s, d))
    #plt.xticks(rotation=45, ha='right')
    #plt.subplots_adjust(bottom=0.30)
    ax3.set_xlabel("Time")
    ax3.set_ylabel("mg/dl")
    ax3.set_title('Blodd Glucose')
    # fig.ylabel('Values')
    # fig.xlabel('Time')
    #ax.legend(bbox_to_anchor=(0.75, 1.15), ncol=3)
    #plt.title('Insulin')
    #plt.ylabel('U/hr')
    #plt.xlabel('Time')
    #plt.legend(loc="lower right")

def animate4(frame, xs, ys):
    """Function called periodically by the Matplotlib as an animation.
    It reads a new temperature value, add its to the data series and update the plot.
    :param frame: not used
    :param xs: x data
    :param ys: y data
    """

    # Read temperature
    #temperature = read_temperature()

    # Add x and y to lists

    #ys.append(temperature)

    # Limit x and y lists to the more recent items

    if len(xs)>288:
        size_limit = 288
    else:
        size_limit = len(xs)
    xs = xs[-size_limit:]
    ys = ys[-size_limit:]

    # Draw x and y lists
    ax4.clear()
    ax4.plot(xs, ys)

    # (Re)Format plot
    ax4.grid()
    for tick in ax4.get_xticklabels():
        tick.set_rotation(45)
    for s, d in zip(ax4.get_xticks(), ys):
        ax4.annotate("{:.2f}".format(d), xy=(s, d))
    #plt.xticks(rotation=45, ha='right')
    #plt.subplots_adjust(bottom=0.30)
    ax4.set_xlabel("Time")
    ax4.set_ylabel("gramm")
    ax4.set_title('Meal Intake')
    # fig.ylabel('Values')
    # fig.xlabel('Time')
    #ax.legend(bbox_to_anchor=(0.75, 1.15), ncol=3)
    #plt.title('Insulin')
    #plt.ylabel('U/hr')
    #plt.xlabel('Time')
    #plt.legend(loc="lower right")




def animate2(frame, xs, ys,ys1,ys2,fig):
    """Function called periodically by the Matplotlib as an animation.
    It reads a new temperature value, add its to the data series and update the plot.
    :param frame: not used
    :param xs: x data
    :param ys: y data
    """

    # Read temperature
    #temperature = read_temperature()

    # Add x and y to lists

    #ys.append(temperature)

    # Limit x and y lists to the more recent items
    if len(xs)>288:
        size_limit = 288
    else:
        size_limit = len(xs)
    xs = xs[-size_limit:]
    ys = ys[-size_limit:]

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, ys,label="Insulin")
    ax.plot(xs, ys1,label="Blood Glucose Level")
    ax.plot(xs, ys2,label="Meal Intake")
    #print(list(range(len(xs))))
    #print(len(xs))
    #print(ax.get_xticks())
    for s, d in zip(ax.get_xticks(), ys):
        ax.annotate("{:.2f}".format(d), xy=(s, d))
    for s, d in zip(ax.get_xticks(), ys1):
        ax.annotate("{:.2f}".format(d), xy=(s, d))
    for s, d in zip(ax.get_xticks(), ys2):
        ax.annotate("{:.2f}".format(d), xy=(s, d))
    ax.grid()

    # (Re)Format plot
    #plt.grid()
    #ax.xticks(rotation=45, ha='right')
    for tick in ax.get_xticklabels():
        tick.set_rotation(45)
    #plt.subplots_adjust(bottom=0.30)
    ax.set_xlabel("Time")
    ax.set_ylabel("Values")
    ax.set_title('Sensors Data')
    #fig.ylabel('Values')
    #fig.xlabel('Time')
    ax.legend(bbox_to_anchor=(0.75, 1.15), ncol=3)


if __name__ == '__main__':
    # Create figure

    my_thread = threading.Thread(target=connection)

    my_thread.start()
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    # Create empty data series
    x_data = []
    y_data = []

    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, animate2, fargs=(timestamp, insulin,bg,meal,fig), interval=200)
    # NOTE: it is mandatory keep a reference to the animation otherwise it is stopped
    # See: https://matplotlib.org/api/animation_api.html

    # Show
    #plt.show()

    fig2 = plt.figure()
    ax2 = fig2.add_subplot(1, 1, 1)

    # Create empty data series
    x_data = []
    y_data = []

    # Set up plot to call animate() function periodically
    ani2 = animation.FuncAnimation(fig2, animate, fargs=(timestamp, insulin), interval=200)
    # NOTE: it is mandatory keep a reference to the animation otherwise it is stopped
    # See: https://matplotlib.org/api/animation_api.html


    fig3 = plt.figure()
    ax3 = fig3.add_subplot(1, 1, 1)

    # Create empty data series
    x_data = []
    y_data = []

    # Set up plot to call animate() function periodically
    ani3 = animation.FuncAnimation(fig3, animate3, fargs=(timestamp, bg), interval=200)

    fig4 = plt.figure()
    ax4 = fig4.add_subplot(1, 1, 1)

    # Create empty data series
    x_data = []
    y_data = []

    # Set up plot to call animate() function periodically
    ani4 = animation.FuncAnimation(fig4, animate4, fargs=(timestamp, meal), interval=200)

    # Show
    plt.show()