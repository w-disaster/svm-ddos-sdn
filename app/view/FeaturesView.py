import threading
import numpy as np
from matplotlib import pyplot as plt
from queue import Queue
import time
from app.controllers.MainController import MainController

"""
    FeaturesView class.
    This class plots the charts with the real time features computed by
    the controller. It's implemented by a blocking queue: when there are
    features in it they are plotted.
"""
class FeaturesView:
    def __init__(self):
        # Fields
        self.queue = Queue()
        self.period = 3
        self.t_arr = []
        self.f_arr = [[], [], [], [], []]
        self.fig = plt.figure(1)

        # Start controller thread
        mc = MainController(queue=self.queue, period=self.period)
        c_thread = threading.Thread(target=mc.run, daemon=True)
        c_thread.start()

    def run(self):
        while True:
            # Wait until new data is ready
            features = self.queue.get()

            # Fetch the timestamp
            k, timestamp = features[0]
            self.t_arr.append(timestamp)
            self.t_arr = self.t_arr[-50:]

            # For each pair in features
            i = 0
            for f, v in features:
                if f != "timestamp":
                    # Add subplot
                    ax = self.fig.add_subplot(2, 3, i + 1)
                    ax.title.set_text(f.upper())
                    # Add feature in the features array and limit its size
                    self.f_arr[i].append(v)
                    self.f_arr[i] = self.f_arr[i][-50:]
                    # Update the subplot
                    ax.plot(self.t_arr, self.f_arr[i])
                    i = i + 1

            # Plot in interactive mode
            plt.pause(0.02)
            plt.ion()
            plt.show()


if __name__ == "__main__":
    # Run View with charts
    fw = FeaturesView()
    fw.run()

