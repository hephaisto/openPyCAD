from openPyCAD.wrapper import *
import math
VISIBLE_HOLES=True

def save(filename,obj):
	with open(filename,"w") as f:
		if isinstance(obj,list):
			for o in obj:
				f.write(o.toScript())
		else:
			f.write(obj.toScript())


def visibleHole(*something):
	result=[negative()(*something)]
	if VISIBLE_HOLES:
		inlay=group()(*something)
		inlay.modifier="%"
		result.append(inlay)
	return result

class Template(container):
	def __init__(self,**kwargs):
		container.__init__(self,**kwargs)
		self.leafNode=None
	
	def __call__(self,*args,**kwargs):
		if self.leafNode is None:
			return container.__call__(self,*args,**kwargs)
		else:
			self.leafNode.__call__(*args,**kwargs)
			return self
	
	def write(self,writer):
		writer.writeLine(self.modifier+"union()")
		writer.incDepth()
		self.writeBody(writer)
		writer.decDepth()

class from_to(Template):
	def __init__(self,x,y,z,tx,ty,tz,**kwargs):
		Template.__init__(self,**kwargs)
		
		phi=math.atan2(ty-y,tx-x)*180/math.pi
		theta=math.atan2(math.sqrt((tx-x)**2+(ty-y)**2),tz-z)*180/math.pi
		
		self.leafNode=rotate(0,theta,0)
		
		self.positive.append(
			translate(x,y,z)
			(
				rotate(0,0,phi)
				(
					self.leafNode
				)
			)
		)

def cylinder_from_to(x,y,z,tx,ty,tz,r,**kwargs):
	return from_to(x,y,z,tx,ty,tz)(cylinder(r=r,h=math.sqrt((tx-x)**2+(ty-y)**2+(tz-z)**2),**kwargs))
