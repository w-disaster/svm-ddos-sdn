import threading
import tkinter
from tkinter import Tk
from matplotlib import pyplot as plt
from queue import Queue
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from app.controllers.DDoSControllerThread import DDoSControllerThread
from app.model.Features import Feature
from app.model.TrafficState import TrafficState
import matplotlib.dates as mdates

"""
    View class.
    This class starts the controller thread and plots its calculated features
    in different charts. It's implemented by a blocking queue: whenever 
    new features are computed, they're popped from the queue and plotted.
"""


class View:
    def __init__(self):
        # Blocking queue
        self.queue = Queue()
        # Init arrays
        self.timestamps = []
        self.features = [[], [], [], [], []]

    """
    Start controller thread
    """
    def start_controller(self):
        controller = DDoSControllerThread(queue=self.queue)
        c_thread = threading.Thread(target=controller.run, daemon=True)
        c_thread.start()

    """
    Start view by creating a Tkinter window and running the receiving thread
    """
    def init_GUI(self):
        # Tkinter
        root = Tk()
        root.title('DDoS protect')
        root.config(background='white')
        root.geometry("1700x1000")

        # Add traffic state label on top
        label = tkinter.Label(root, text="", bg="grey", fg="white", font=("monospace", 16), width=20, height=3)
        label.pack(pady=(30, 0))

        # Add figure with plots
        fig = Figure()
        ax = []
        k = 0

        # Subplots
        for i, v in enumerate(list(Feature)):
            if i < 3:
                # Place first three plots on the first line
                ax.append(plt.subplot2grid(shape=(2, 6), loc=(0, i * 2), colspan=2, fig=fig))
            else:
                # Place the last two in the 2nd line
                ax.append(plt.subplot2grid(shape=(2, 6), loc=(1, k * 2 + 1), colspan=2, fig=fig))
                k += 1
            ax[i].title.set_text(v.value)
            ax[i].grid()

            ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            plt.setp(ax[i].get_xticklabels(), rotation=15)
            plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=1))

        # Pack the figure
        graph = FigureCanvasTkAgg(fig, master=root)
        graph.get_tk_widget().pack(fill=tkinter.BOTH, expand=True)

        # Start the thread to update the charts while maintaining Tkinter up
        threading.Thread(target=self.__run, args=(label, ax, graph)).start()
        root.mainloop()

    """ 
    This method plots the features taken from the blocking queue whenever the 
    controller computes one. Furthermore, the label text and colour are updated
    according to the traffic state 
    """
    def __run(self, label, ax, graph):
        while True:
            # Blocking queue: wait until new data is ready
            data = self.queue.get()

            # Update label text and colour
            traffic_state = data.get_traffic_state()
            label.config(text=traffic_state.name, bg="green" if traffic_state == TrafficState.NORMAL else "red")

            # Get the timestamp and append it into the array
            timestamp = data.get_timestamp()
            self.timestamps.append(timestamp)
            self.timestamps = self.timestamps[-50:]

            # Get the features and plot them into the corresponding chart
            for i, (l, value) in enumerate(data.get_features().get_features_as_array()):
                ax[i].cla()
                ax[i].grid()
                # Append features data
                self.features[i].append(value)
                self.features[i] = self.features[i][-50:]
                ax[i].title.set_text(l.value)

                # Plot data
                ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                plt.setp(ax[i].get_xticklabels(), rotation=15)
                ax[i].plot(self.timestamps, self.features[i], marker='o', color='orange')
                graph.draw()


if __name__ == "__main__":
    view = View()
    # Start controller thread
    view.start_controller()
    # Start view
    view.init_GUI()
