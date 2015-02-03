from openPyCAD import *
from openPyCAD.writer import Writer

# set epsilon for zero-width planes
#import openPyCAD.libraries as libs
#libs.EPSILON=0.00001

# show holes?
import openPyCAD.tools
#openPyCAD.tools.VISIBLE_HOLES=False


from openPyCAD.libraries.metric_screws import *

import sys
if not len(sys.argv)==2:
	print("usage: testOpenPyCAD.py <metric>")
	print("available metrics: {}".format(",".join([str(m) for m in metrics.keys()])))
	sys.exit()

def testCube(m):
	side_size=max(m.ac+2*5.0,m.headHeight+m.nutHeight+5.0)
	return (group()
		(
			cube(3*m.ac+4*5.0,side_size,side_size)
			,visibleHole
			(
				m.screw_from_to(
					side_size/2+0*(m.ac+5.0) ,side_size/2, 0,
					side_size/2+0*(m.ac+5.0), side_size/2, side_size,
					head="hex",nut="round")
			)
			
			,visibleHole
			(
				m.screw_from_to(side_size/2+1*(m.ac+5.0) ,0, side_size/2,
					 side_size/2+1*(m.ac+5.0), side_size, side_size/2,
					 head="hex",nut="round")
			)
			
			,visibleHole
			(
				m.screw_from_to(side_size/2+2*(m.ac+5.0) ,side_size/2, side_size,
					 side_size/2+2*(m.ac+5.0), side_size/2, 0,
					 head="hex",nut="round")
			)
		)
	)

metric=metrics[int(sys.argv[1])]

root=group()
root(testCube(metric))

writer=Writer()
root.write(writer)
writer.saveTo("test.scad")