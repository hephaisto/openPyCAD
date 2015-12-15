from openPyCAD.wrapper import group,translate,rotate,cube,mirror
from openPyCAD.tools import visibleHole
import openPyCAD.libraries.metric_screws as m
from openPyCAD.libraries import EPSILON

class ProfileDefinition():
	def __init__(self,
			width, # full width of profile. usually multiple of 20mm
			screw_metric, # metric of mounting screws. instance of libraries.metric_screws
			num_screws, # number of grooves/screws (usually 1 or 2)
			groove_width, # width for everything that protrudes from the groove
			groove_inner_width, # width for stones that should not be able to pass
			groove_depth, # height for rectangular stones. this is *not* the total depth of the groove, but rather some value smaller than the depth groove_inner_width away from the center. measured from the *inside* of the wall
			groove_wall_thickness, # thickness of the material that makes up the outer frame of the profile
			stone_size_short, # short side of asymmetrical stones. from center of hole to end
			stone_size_long # long side of asymmetrical stones.
			):
	
		self.num_screws = num_screws
		self.screw_metric = screw_metric
		self.width = float(width)

		self.groove_width=groove_width
		self.groove_inner_width=groove_inner_width
		self.groove_depth=groove_depth
		self.groove_wall_thickness=groove_wall_thickness
		self.stone_size_short=stone_size_short
		self.stone_size_long=stone_size_long
	
	def make_screws(self, center, length, rotation, rotation2=0.0, **kwargs):
		positions=[-self.width/2+0.5*(2*i+1)/self.num_screws*self.width for i in range(self.num_screws)]
		root=translate(*center)(rotate(0,0,rotation)(rotate(0,rotation2,0)(
			[self.screw_metric.screw_from_to(positions[i],0,length, positions[i],0,0, **kwargs)
			for i in range(self.num_screws)
			])))
		return root

	def make_plate_alignment(self, hole_modes, shape, plate_length, printable=False):
		# hole distance not needed (can be calculated from profile data)
		"""hole_modes: list of stone alignments:
			left: long side of stone left
			right: long side of stone right
			pin: printed alignment pin without stone
		shape:
			corner: holes on top, connection on side
			top: holes on first rail, connection on second rail (only possible with 2+ rails)
			far_corner: holes on first rail, connection on opposing side (only possible with 2+ rails)
		"""
		groove_width=6.0
		groove_depth=2.0
		groove_inner_width=8.0
		groove_wall_thickness=1.0
		stone_size_short=3.0
		stone_size_long=5.0
		side_length=2*groove_width
		half_width=self.width/self.num_screws/2

		def make_alignment():
			root=translate(-groove_width/2,plate_length/2,0)(
				cube(groove_width,side_length,groove_depth+groove_wall_thickness),
				translate(0,0,-groove_width)(
					cube(half_width+groove_width*1.5,side_length,groove_width)
				)
			)
			return root
		def make_connection():
			root=translate(0,0,0)(
				translate(-groove_width-half_width,plate_length/2,-groove_width)(
					cube(half_width+groove_width,side_length,groove_width)
				),
				translate(-groove_width,0,-groove_width)(
					cube(side_length,plate_length/2+side_length,groove_width)
				),
				visibleHole(
					self.screw_metric.screw_from_to(0, 0, -groove_width, 0, 0, 0, head="hexkey")
				)
			)
			return root

		def stone(length):
			return group()(
				translate(-groove_inner_width/2,0,groove_wall_thickness)(
					cube(groove_inner_width,length,groove_depth)),
				translate(-groove_width/2,0,0)(
					cube(groove_width,length,groove_wall_thickness))
			)

		def make_inner():
			y_positions=[half_width*(2*i-len(hole_modes)+1) for i in range(len(hole_modes))]
			root=group()
			for i in range(len(hole_modes)):
				if hole_modes[i] in ("left","right"):
					root(visibleHole(self.screw_metric.screw_from_to(0,y_positions[i],-10, 0,y_positions[i], 0)))
					stone_left,stone_right=(stone_size_long,stone_size_short) if hole_modes[i]=="left" else (stone_size_short,stone_size_long)
					root(visibleHole(translate(-groove_width/2,y_positions[i]-stone_left+EPSILON,0)(cube(groove_width,stone_size_long+stone_size_short-2*EPSILON,groove_depth))))
				elif hole_modes[i]=="pin":
					root(self.screw_metric.screw_from_to(0,y_positions[i],0, 0,y_positions[i], -groove_width)),
					root(translate(0,y_positions[i]-stone_size_long,0)(
						stone(2*stone_size_long)
					))
                                

			# make inner spacers
			for i in range(len(hole_modes)-1):
				padding_left =stone_size_short if hole_modes[i  ]=="left"  else stone_size_long
				padding_right=stone_size_short if hole_modes[i+1]=="right" else stone_size_long
				length=half_width*2-padding_left-padding_right
				begin=y_positions[i]+padding_left
				root(translate(0,begin,0)(
					stone(length)
					))
			padding=(stone_size_short if hole_modes[0]=="right" else stone_size_long)
			root(translate(0,-plate_length/2,0)(stone(plate_length/2+y_positions[0]-padding)))
			padding=(stone_size_short if hole_modes[-1]=="left" else stone_size_long)
			root(translate(0,y_positions[-1]+padding,0)(stone(plate_length/2-y_positions[-1]-padding)))
			return root

		con=group()(make_connection(),mirror(0,1,0)(make_connection()))
		align=group()(make_alignment(),mirror(0,1,0)(make_alignment()))
		inner=make_inner()
		if shape=="corner":
			alignment=group(align,inner)
			connection=translate(half_width,0,half_width)(rotate(0,-90,0)(con))
		elif shape=="top":
			if self.num_screws<2:
				raise Exception("plate alignment with shape=top only possible for profiles with num_screws >= 2")
			alignment=translate(-self.width/self.num_screws/2,0,0)(align)
			if not printable: alignment(inner)
			connection=translate(+self.width/self.num_screws/2,0,0)(con)
		elif shape=="far_corner":
			raise NotImplementedError("far_corner not implemented yet")
		else:
			raise Exception("unknown shape: {}".format(shape))


		root=group()(
			alignment,
			connection
		)
		if printable:
			root(translate(self.width,0,0)(rotate(0,180,0)(inner)))
		return root



groove_20mm = (5.0, 7.0, 2.0, 1.5, 1.5+2.5, 5.5+2.5)

profile_20       =ProfileDefinition(20, m.m5, 1, *groove_20mm)
#profile_40_single=ProfileDefinition(40, m.m8, 1)
profile_40_double=ProfileDefinition(40, m.m5, 2, *groove_20mm)

if __name__=="__main__":
	from openPyCAD.writer import Writer
	writer=Writer()
	root=group()
	profile=profile_40_double
	root(profile.make_plate_alignment(["left","left","pin","right","left"],"top",100.0))
	root.write(writer)
	writer.saveTo("profiles.scad")
