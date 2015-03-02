from openPyCAD.libraries import EPSILON,FN_MANY
from openPyCAD.wrapper import *
from openPyCAD.tools import from_to
import math

TOLERANCE=0.5
INNER_TOLERANCE=0.25

class HeadHex():
	def __init__(self, height, ac):
		self.height = height
		self.ac = ac
	def make(self, head_overlength):
		result=translate(0,0,-head_overlength-self.height-EPSILON)(cylinder(r=self.ac/2+TOLERANCE, h=self.height+head_overlength+EPSILON, fn=6))
		return result
	def getHeight(self):
		return self.height

class HeadHexKey():
	def __init__(self, height, ac):
		self.height = height
		self.ac = ac
	def make(self, head_overlength):
		result=translate(0,0,-head_overlength-self.height-EPSILON)(cylinder(r=self.ac/2+TOLERANCE, h=self.height+head_overlength+EPSILON, fn=FN_MANY))
		return result
	def getHeight(self):
		return self.height

class HeadCountersunk():
	def __init__(self, ac):
		self.ac = ac
		self.height=ac/2
	def make(self, head_overlength):
		result=translate(0,0,0)(translate(0,0,-EPSILON)(cylinder(r=self.ac/2+TOLERANCE, r2=0.0, h=self.height+EPSILON, fn=FN_MANY)))
		if head_overlength!=0.0:
			result(translate(0,0,-head_overlength-EPSILON)((cylinder(r=self.ac/2+TOLERANCE, h=head_overlength+EPSILON, fn=FN_MANY))))
		return result
	def getHeight(self):
		return self.ac/2

nominal_lengths=[10.0, 25.0, 40.0]
def get_next_nominal(length):
	for nl in nominal_lengths:
		if length<=nl:
			return nl
	else:
		raise Exception("no nominal length for length {} found!".format(length))

class Metric():
	def __init__(self,diameter,heads, nuts):
		"""
		diameter: hole diameter (nominal diameter, e.g. 4 for M4 screws)
		headHeight: height of the hole for the head
		ac: outer diameter (Acc/Corn)
		nutHeight: height of the hole for the nut
		"""
		self.diameter=diameter
		self.heads = heads
		self.nuts = nuts
		#self.ac=ac
		#self.headHeight=headHeight
		#self.nutHeight=nutHeight
	
	#def screwHead(self,isNut,isHex, head_overlength):
		#root=cylinder(r=self.ac/2+TOLERANCE,h=(self.nutHeight if isNut else self.headHeight)+head_overlength+EPSILON,fn=6 if isHex else 100)
		#if head_overlength!=0.0:
			#root=translate(0,0,head_overlength*(1 if isNut else -1))(root)
		#return root
	
	def screw(self, nominal_length, head=None, nut=None, nut_begin=None, nut_end=None,rot=0.0, head_overlength=0.0, nut_overlength=0.0, push_head_in=False):
		#assert not (outer_length is None and inner_length is None), "must supply either outer_length or inner_length"
		#assert outer_length is not None or inner_length is not None, "must supply either outer_length or inner_length"
		#if outer_length is None:
			#outer_length=inner_length+self.headHeight+self.nutHeight
		assert nominal_length in nominal_lengths
		assert nut_begin is None or nut_end is None
		
		print("screw (d={}) with nominal length of {}".format(self.diameter, nominal_length))
		
		g=rotate(0,0,rot)
		g(translate(0,0,-EPSILON)(cylinder(r=self.diameter/2+INNER_TOLERANCE,h=nominal_length+2*EPSILON,fn=100)))
		if head is not None:
			#g(translate(0,0,-EPSILON)(self.screwHead(False,head=="hex",head_overlength)))
			g(translate(0,0,-EPSILON)(self.heads[head].make(head_overlength)))
		if nut is not None:
			#g(translate(0,0,outer_length-self.headHeight)(self.screwHead(False,nut=="hex",nut_overlength)))
			if nut_end is not None:
				np=nut_end
			elif nut_begin is not None:
				np=nut_begin+self.nuts[nut].height
				if np>nominal_length:
					print("warning: nut not fully on screw!")
			else:
				np=nominal_length#+self.nuts[nut].height
			g(translate(0,0,np-self.nuts[nut].height)(rotate(180,0,0)((self.nuts[nut].make(nut_overlength)))))
		if push_head_in:
			g=translate(0,0,self.heads[head].height)(g)
		return g
	
	def screw_from_to(self, x,y,z, tx,ty,tz, **kwargs):
		length=math.sqrt((tx-x)**2+(ty-y)**2+(tz-z)**2)
		nominal_length=get_next_nominal(length)
		g=(
			from_to(x,y,z,tx,ty,tz)
			(
				self.screw(nominal_length=nominal_length, **kwargs)
			)
		)
		return g
	

# hex values based on http://www.roymech.co.uk/Useful_Tables/Screws/Hex_Screws.htm
# other values based on http://www.roymech.co.uk/Useful_Tables/Screws/cap_screws.htm

def make_metric(diameter, hex_height, hex_ac, hexkey_ac, nut_height):
	heads={"hex":HeadHex(hex_height, hex_ac), "sunk":HeadCountersunk(2.0*diameter)}
	if hexkey_ac is not None:
		heads["hexkey"]=HeadHexKey(diameter, hexkey_ac)
	return Metric(diameter, heads, {"hex":HeadHex(nut_height, hex_ac)})

m3 =make_metric( 3.0,  2.125, 06.40,  5.50,  2.40)
m4 =make_metric( 4.0,  2.925, 08.10,  7.00,  3.20)
m5 =make_metric( 5.0,  3.650, 09.20,  8.50,  4.00)
m6 =make_metric( 6.0,  4.150, 11.50, 10.00,  5.00)

m8 =make_metric( 8.0,  5.650, 15.00, 13.00,  6.50)
m10=make_metric(10.0,  7.180, 19.60, 16.00,  8.00)
m12=make_metric(12.0,  8.180, 22.10, 18.00, 10.00)
m16=make_metric(16.0, 10.180, 27.70, 24.00, 13.00)

m20=make_metric(20.0, 13.215, 34.60, 30.00, 16.00)
m24=make_metric(24.0, 15.215, 41.60, 36.00, 19.00)
m30=make_metric(30.0, 19.260, 53.10, None , 24.00)
m36=make_metric(36.0, 23.260, 63.50, None , 29.00)


metrics={
	3:m3,
	4:m4,
	5:m5,
	6:m6,
	8:m8,
	10:m10,
	12:m12,
	16:m16,
	20:m20,
	24:m24,
	30:m30,
	36:m36
}