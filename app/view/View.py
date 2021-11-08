import threading
from tkinter import Tk, Label

from matplotlib import pyplot as plt
from queue import Queue

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from app.controllers.DDOSController import DDOSController
from app.model.Features import FeatureLabel, Features

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
        self.period = 0.5
        self.t_arr = []
        self.f_arr = [[], [], [], [], []]

        # Start controller thread
        mc = DDOSController(queue=self.queue, period=self.period)
        c_thread = threading.Thread(target=mc.run, daemon=True)
        c_thread.start()

        root = Tk()
        root.config(background='white')
        root.geometry("1300x1000")
        fig = Figure()

        labels = [fb.name for fb in list(FeatureLabel)]
        self.ax = []
        for i, l in enumerate(labels):
            self.ax.append(fig.add_subplot(2, 3, i + 1))
            self.ax[i].title.set_text(l)
            self.ax[i].grid()

        self.graph = FigureCanvasTkAgg(fig, master=root)
        self.graph.get_tk_widget().pack(side="top", fill='both', expand=True)

        threading.Thread(target=self.plot_data).start()

        root.mainloop()

    def plot_data(self):
        while True:
            chart_data = self.queue.get()
            timestamp = chart_data.get_timestamp()
            self.t_arr.append(timestamp)
            self.t_arr = self.t_arr[-50:]

            for i, (label, value) in enumerate(chart_data.get_features().get_features_as_array()):
                self.ax[i].cla()
                self.ax[i].grid()

                self.f_arr[i].append(value)
                self.f_arr[i] = self.f_arr[i][-50:]

                self.ax[i].title.set_text(label.value)
                self.ax[i].plot(self.t_arr, self.f_arr[i], marker='o', color='orange')
                self.graph.draw()


if __name__ == "__main__":
    # Run View with charts
    fw = FeaturesView()
    #fw.run()

