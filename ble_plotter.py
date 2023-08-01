from multiprocessing import Process

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D

from config import Config
from rssi_conv import RSSIConv
from ble_uuid import BLE_UUID
import matplotlib.cm as cm
import numpy as np

class Plotter(Process):
    def __init__(self, queue, rssi_val, maxt=Config().get_settings()['max_t_default'], dt=Config().get_settings()['dt_default']):
        Process.__init__(self)
        settings = Config().get_settings()
        self.dt = dt
        self.maxt = maxt
        self.tdata = [0]
        self.queue = queue
        self.rssi_v = rssi_val
        self.start_t = 0
        self.end_t = 0
        self.axis_limits = {
            "rssi_min": settings['axis']['rssi_min_def'],
            "rssi_max": settings['axis']['rssi_max_def'],
            "rssi_step": settings['axis']['rssi_y_step'],
            "dist_min": settings['axis']['dist_min_def'],
            "dist_max": settings['axis']['dist_max_def'],
            "dist_step": settings['axis']['dist_y_step']
        }

    def update(self, frame):
        lastt = self.tdata[-1]
        if lastt > self.tdata[0] + self.maxt:
            self.tdata = [self.tdata[-1]]
            for k in self.rssi_v.keys():
                self.ydat_rssi[k] = [self.ydat_rssi[k][-1]]
                self.ydat_dist[k] = [self.ydat_dist[k][-1]]
            
            self.init_axes_def()
            self.update_axis_ylim()
            for i in range(2):
                self.ax[i].set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
                # self.ax[i].figure.canvas.draw()
                self.ax[i].figure.canvas.draw_idle()


        t = frame * self.dt
        self.tdata.append(t)
        for i, k in enumerate(self.rssi_v.keys()):
            self.ydat_rssi[k].append(self.rssi_v[k])
            self.ydat_dist[k].append(RSSIConv.get_dist(self.rssi_v[k]))
            self.update_axis_ylim()
            self.lines_rssi[i].set_data(self.tdata, self.ydat_rssi[k])
            self.lines_dist[i].set_data(self.tdata, self.ydat_dist[k])
        self.queue.put([t] + [self.rssi_v[k] for k in self.rssi_v.keys()])
        # self.end_t = time.time()
        # self.queue.put([self.end_t - self.start_t])
        # self.start_t = time.time()
        return self.ax[0].get_lines() + self.ax[1].get_lines()

    def init_axes(self):
        
        self.axis_num = len(self.rssi_v)
        self.ydat_rssi = {k:[0] for k in self.rssi_v.keys()}
        self.ydat_dist = {k:[0] for k in self.rssi_v.keys()}

        self.lines_rssi = [Line2D(self.tdata, self.ydat_rssi[k]) for k in self.rssi_v.keys()]
        
        self.init_axes_def()
        self.init_lines(self.ax[0], self.lines_rssi)
        self.lines_dist = [Line2D(self.tdata, self.ydat_dist[k]) for k in self.rssi_v.keys()]
        self.init_lines(self.ax[1], self.lines_dist)
        self.init_line_colors()

    def init_axes_def(self):
        self.init_axis(self.ax[0], "RSSI (dBm)", self.axis_limits['rssi_min'],
                    self.axis_limits['rssi_max'], self.axis_limits['rssi_step'])
        self.init_axis(self.ax[1], "Distance (m)", self.axis_limits['dist_min'],
                    self.axis_limits['dist_max'], self.axis_limits['dist_step'])
    
    def init_axis(self, axis, name, y_lim_min, y_lim_max, y_ticks):
        axis.set_ylim(y_lim_min, y_lim_max)
        axis.set_xlim(0, self.maxt)
        axis.set_ylabel(name)
        axis.set_yticks(np.arange(y_lim_min, y_lim_max+1, y_ticks))
        axis.set_yticks(np.arange(y_lim_min, y_lim_max+1, y_ticks/2), minor=True)
    
    def update_axis_ylim(self):
        rssi_min, rssi_max = self.ax[0].get_ylim()
        dist_min, dist_max = self.ax[1].get_ylim()
        need_update = False
        for k in self.rssi_v.keys():
            while self.rssi_v[k] < rssi_min:
                rssi_min -= self.axis_limits['rssi_step']
                need_update = True
            while self.rssi_v[k] > rssi_max:
                rssi_max += self.axis_limits['rssi_step']
                need_update = True
            while RSSIConv.get_dist(self.rssi_v[k]) < dist_min:
                dist_min -= self.axis_limits['dist_step']
            while RSSIConv.get_dist(self.rssi_v[k]) > dist_max:
                dist_max += self.axis_limits['dist_step']
                need_update = True
        
        if need_update == True:
            self.ax[0].set_ylim(rssi_min, rssi_max)
            self.ax[0].set_yticks(np.arange(rssi_min, rssi_max+1, self.axis_limits['rssi_step']))
            self.ax[0].set_yticks(np.arange(rssi_min, rssi_max+1, self.axis_limits['rssi_step']/2), minor=True)
            self.ax[1].set_ylim(dist_min, dist_max)
            self.ax[1].set_yticks(np.arange(dist_min, dist_max+1, self.axis_limits['dist_step']))
            self.ax[1].set_yticks(np.arange(dist_min, dist_max+1, self.axis_limits['dist_step']/2), minor=True)
            for i in range(2):
                self.ax[i].figure.canvas.draw_idle()

    
    def init_line_colors(self):
        colors = cm.get_cmap('Paired', self.axis_num)

        for i, rssi_line, dist_line in zip(range(self.axis_num), self.ax[0].get_lines(), self.ax[1].get_lines()):
            rssi_line.set_color(colors(i))
            dist_line.set_color(colors(i))
            self.ax[0].get_legend().legendHandles[i].set_color(colors(i))
            self.ax[1].get_legend().legendHandles[i].set_color(colors(i))
            

    def init_lines(self, axis, lines):
        filters = Config().get_settings()['BLE_FILTERS']
        devices = {**filters['MAC'], **{BLE_UUID(k):v for k,v in filters['UUID'].items()}}
        names = [devices[i] for i in devices.keys()]
        for line, name in zip(lines, names):
            line.set_label(name)
            axis.add_line(line)

        # Shrink current axis by 20%
        box = axis.get_position()
        axis.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        axis.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        axis.grid()

    def run(self):
        self.fig, self.ax = plt.subplots(2, 1, num="RSSI/Distance plot")
        self.init_axes()
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=self.dt*1000, blit=True, cache_frame_data=False)
        plt.show()