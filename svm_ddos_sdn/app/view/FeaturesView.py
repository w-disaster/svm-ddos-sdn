import threading
import numpy as np
from matplotlib import pyplot as plt
from queue import Queue
import time
from app.controllers.MainController import MainController


class FeaturesView:
    def __init__(self):
        self.queue = Queue()
        self.period = 3

        # Start controller thread
        mc = MainController(queue=self.queue, period=self.period)
        c_thread = threading.Thread(target=mc.run, daemon=True)
        c_thread.start()

        self.t_arr = []
        self.f_arr = [[], [], [], [], []]
       
        #self.ax = []
        #for i in range(0, 5):
        #    self.ax.append(fig.add_subplot(5, 1, i + 1))
        #plt.show()

    def run(self):
        fig = plt.figure(1)
        while True:
            i = 0
            # Wait until new data is ready
            features = self.queue.get()
            print(features)
            # Get the timestamp
            k, timestamp = features[0]
            self.t_arr.append(timestamp)
            self.t_arr = self.t_arr[-50:]

            for f, v in features:
                if f != "timestamp":
                    # Add subplot
                    ax = fig.add_subplot(5, 1, i + 1)
                    # Add feature in the features array and limit its size
                    print(self.f_arr[i])
                    self.f_arr[i].append(v)
                    self.f_arr[i] = self.f_arr[i][-50:]
                    # Plot
                    ax.plot(self.t_arr, self.f_arr[i])
                    i = i + 1

            print("ciao")
            plt.ion()
            plt.show()


if __name__ == "__main__":
    fw = FeaturesView()
    fw.run()

