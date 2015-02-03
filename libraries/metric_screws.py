from openPyCAD.libraries import EPSILON
from openPyCAD.wrapper import *
from openPyCAD.tools import from_to
import math

TOLERANCE=0.0

class Metric():
	def __init__(self,diameter,headHeight,ac,nutHeight):
		"""
		diameter: hole diameter (nominal diameter, e.g. 4 for M4 screws)
		headHeight: height of the hole for the head
		ac: outer diameter (Acc/Corn)
		nutHeight: height of the hole for the nut
		"""
		self.diameter=diameter
		self.ac=ac
		self.headHeight=headHeight
		self.nutHeight=nutHeight
	
	def screwHead(self,isNut,isHex):
		return cylinder(r=self.ac/2+TOLERANCE,h=(self.nutHeight if isNut else self.headHeight)+EPSILON,fn=6 if isHex else 100)
	
	def screw(self, outer_length=None, inner_length=None, head=None, nut=None, overlength=0.0,rot=0.0):
		assert not (outer_length is None and inner_length is None), "must supply either outer_length or inner_length"
		assert outer_length is not None or inner_length is not None, "must supply either outer_length or inner_length"
		if outer_length is None:
			outer_length=inner_length+self.headHeight+self.nutHeight
		
		g=rotate(0,0,rot)
		g(translate(0,0,-EPSILON)(cylinder(r=self.diameter/2+TOLERANCE,h=outer_length+overlength+2*EPSILON,fn=100)))
		if head is not None:
			g(translate(0,0,-EPSILON)(self.screwHead(False,head=="hex")))
		if nut is not None:
			g(translate(0,0,outer_length-self.headHeight)(self.screwHead(False,nut=="hex")))
		return g
	
	def screw_from_to(self, x,y,z, tx,ty,tz, head=None, nut=None, rot=0.0):
		length=math.sqrt((tx-x)**2+(ty-y)**2+(tz-z)**2)
		g=(
			from_to(x,y,z,tx,ty,tz)
			(
				self.screw(outer_length=length, head=head, nut=nut, rot=rot)
			)
		)
		return g
	

# values based on http://www.roymech.co.uk/Useful_Tables/Screws/Hex_Screws.htm
m3 =Metric( 3,  2.125, 06.40,  2.40)
m4 =Metric( 4,  2.925, 08.10,  3.20)
m5 =Metric( 5,  3.650, 09.20,  4.00)
m6 =Metric( 6,  4.150, 11.50,  5.00)
m8 =Metric( 8,  5.650, 15.00,  6.50)
m10=Metric(10,  7.180, 19.60,  8.00)
m12=Metric(12,  8.180, 22.10, 10.00)
m16=Metric(16, 10.180, 27.70, 13.00)
m20=Metric(20, 13.215, 34.60, 16.00)
m24=Metric(24, 15.215, 41.60, 19.00)
m30=Metric(30, 19.260, 53.10, 24.00)
m36=Metric(36, 23.260, 63.50, 29.00)
