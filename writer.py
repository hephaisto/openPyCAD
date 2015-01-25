
class Writer():
	def __init__(self):
		self.depth=0
		self.content=""
		self.includes=[]
	
	def writeLine(self,text):
		self.content+="\t"*self.depth+text+"\n"
	
	def incDepth(self):
		self.depth+=1
	
	def decDepth(self):
		self.depth-=1
		assert self.depth>=0
	
	def __str__(self):
		return "\n".join(["include <{}>".format(i) for i in self.includes])+"\n\n"+self.content
	
	def saveTo(self,filename):
		with open(filename,"w") as f:
			f.write(str(self))