from openPyCAD import group,translate,rotate
import openPyCAD.libraries.metric_screws as m

class ProfileDefinition():
	def __init__(self, width, screw_metric, num_screws):
		self.num_screws = num_screws
		self.screw_metric = screw_metric
		self.width = float(width)
	
	def make_screws(self, center, length, rotation, **kwargs):
		positions=[-self.width/2+0.5*(2*i+1)/self.num_screws*self.width for i in range(self.num_screws)]
		root=translate(*center)(rotate(0,0,rotation)(
			[self.screw_metric.screw_from_to(positions[i],0,length, positions[i],0,0, **kwargs)
			for i in range(self.num_screws)
			]))
		return root

profile_20			=ProfileDefinition(20, m.m5, 1)
profile_40_single	=ProfileDefinition(40, m.m8, 1)
profile_40_double	=ProfileDefinition(40, m.m5, 2)