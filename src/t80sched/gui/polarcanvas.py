
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import logging

class PolarCanvas(FigureCanvas):
	
	def __init__(self, parent=None):
		
		fig = plt.figure()
		super(PolarCanvas, self).__init__(fig)
		
		self.axes = fig.add_subplot(111,polar=True)
		# We want the axes cleared every time plot() is called
		self.axes.hold(False)
		
		#self.compute_initial_figure()
		
		#
		FigureCanvas.__init__(self, fig)
		
		self.setParent(parent)
		
		FigureCanvas.updateGeometry(self)
	
		fig.canvas.mpl_connect('axes_enter_event', self.enter_axes)
		fig.canvas.mpl_connect('axes_leave_event', self.leave_axes)
		self.fig = fig

	def compute_initial_figure(self):
		import random
		data = [random.random() for i in range(10)]
		
		ax = self.figure.add_subplot(111)
		
		# discards the old graph
		#ax.hold(False)
		
		# plot data
		ax.plot(data, '*-')
		
		# refresh canvas
		self.draw()


	def enter_axes(self,event):

		logging.debug('enter_axes')#, event.inaxes)
		event.inaxes.patch.set_facecolor('yellow')
		event.canvas.draw()
		#self.track = self.fig.canvas.mpl_connect('motion_notify_event',self.trackPointer)

	def leave_axes(self,event):
		logging.debug('leave_axes')
		event.inaxes.patch.set_facecolor('white')
		event.canvas.draw()
		#self.fig.canvas.mpl_disconnect(self.track)

	def trackPointer(self,event):
		#logging.debug('%f %f'%(event.xdata,event.ydata))
		#self.rect.set_x(event.xdata,event.ydata)
		self.axes.hold(True)
		self.axes.plot(event.xdata,event.ydata,'ro')
		self.draw()
