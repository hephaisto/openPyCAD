
def expand(l):
	return "".join([obj.toScript() for obj in l])

class base():
	def __init__(self):
		self.modifier=""

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
	def __init__(self,r,h,fn=None):
		obj.__init__(self)
		self.r = r
		self.h = h
		self.fn = fn
	
	def toScript(self):
		return self.modifier+"cylinder(r={r},h={h}{additional});".format(r=self.r,h=self.h,additional=",$fn={}".format(self.fn) if self.fn is not None else "")

class container(base):
	def __init__(self,**kwargs):
		base.__init__(self,**kwargs)
		self.positive=[]
		self.negative=[]
	
	def __call__(self,*args):
		for arg in args:
			if isinstance(arg,list):
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