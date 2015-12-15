
def expand(l):
	return "".join([obj.toScript() for obj in l])

class base():
	def __init__(self):
		self.modifier=""
		self.alignmentPoints={}
	
	def getAligned(self,name):
		if name in self.alignmentPoints:
			return translate(*[-p for p in self.alignmentPoints[name]])(self)
		else:
			raise Exception("no alignment point \"{}\" found. Available alignment points: \"{}\"".format(name, "\",\"".join(self.alignmentPoints)))

class obj(base):
	def __init__(self):
		base.__init__(self)
	
	def write(self,writer):
		writer.writeLine(self.toScript())

class cube(obj):
	def __init__(self,x,y,z):
		obj.__init__(self)
		self.x = x
		self.y = y
		self.z = z
	
	def toScript(self):
		return self.modifier+"cube([{},{},{}]);".format(self.x,self.y,self.z)

class cylinder(obj):
	def __init__(self,r,h,fn=None,r2=None):
		obj.__init__(self)
		self.r = r
		self.h = h
		self.fn = fn
		self.r2 = r2
	
	def toScript(self):
		params={
			"r" if self.r2 is None else "r1":self.r,
			"h":self.h
		}
		if self.r2 is not None:
			params["r2"]=self.r2
		return self.modifier+"cylinder({params}{additional});".format(params=",".join(["{}={}".format(k,v) for k,v in params.iteritems()]),additional=",$fn={}".format(self.fn) if self.fn is not None else "")

class sphere(obj):
	def __init__(self,r,fn=None):
		obj.__init__(self)
		self.r = r
		self.fn = fn
	
	def toScript(self):
		return self.modifier+"sphere(r={r}{additional});".format(r=self.r,additional=",$fn={}".format(self.fn) if self.fn is not None else "")

class container(base):
	def __init__(self,**kwargs):
		base.__init__(self,**kwargs)
		self.positive=[]
		self.negative=[]
	
	def __call__(self,*args):
		for arg in args:
			if isinstance(arg,list) or isinstance(arg,tuple):
				self(*arg)
			else:
				assert isinstance(arg,base)
				if isinstance(arg,negative):
					self.negative.append(arg)
				else:
					self.positive.append(arg)
		return self
	
	def writeBody(self,writer):
		if len(self.negative)==0:
			if len(self.positive)==0:
				writer.writeLine("{}")
			else:
				writer.writeLine("union()")
				writer.writeLine("{")
				writer.incDepth()
				for p in self.positive:
					p.write(writer)
				writer.decDepth()
				writer.writeLine("}")
		else:
			if len(self.positive)==0:
				raise Exception("only negative elements in body")
			else:
				writer.writeLine("difference()")
				writer.writeLine("{")
				writer.incDepth()
				
				writer.writeLine("union()")
				writer.writeLine("{")
				writer.incDepth()
				for p in self.positive:
					p.write(writer)
				writer.decDepth()
				writer.writeLine("}")
				
				for p in self.negative:
					p.write(writer)
				
				writer.decDepth()
				writer.writeLine("}")

class mirror(container):
	def __init__(self,x,y,z):
		container.__init__(self)
		self.x = x
		self.y = y
		self.z = z
	
	def write(self,writer):
		writer.writeLine(self.modifier+"mirror([{},{},{}])".format(self.x,self.y,self.z))
		self.writeBody(writer)

class translate(container):
	def __init__(self,x,y,z):
		container.__init__(self)
		self.x = x
		self.y = y
		self.z = z
	
	def write(self,writer):
		writer.writeLine(self.modifier+"translate([{},{},{}])".format(self.x,self.y,self.z))
		self.writeBody(writer)

class rotate(container):
	def __init__(self,x,y,z):
		container.__init__(self)
		self.x = x
		self.y = y
		self.z = z
	
	def write(self,writer):
		writer.writeLine(self.modifier+"rotate([{},{},{}])".format(self.x,self.y,self.z))
		self.writeBody(writer)

class negative(container):
	def __init__(self):
		container.__init__(self)
	
	def write(self,writer):
		writer.writeLine(self.modifier)
		self.writeBody(writer)

class group(container):
	def __init__(self):
		container.__init__(self)
	
	def write(self,writer):
		writer.writeLine(self.modifier)
		self.writeBody(writer)

class module_call(container):
	def __init__(self,module_name,*args,**kwargs):
		container.__init__(self)
		self.module_name = module_name
		self.args = args
		self.kwargs = kwargs
	
	def write(self,writer):
		writer.writeLine(self.modifier+"{}([{},{},{}])".format(self.module_name,self.x,self.y,self.z))
		self.writeBody(writer)