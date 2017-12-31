import copy

# basic value and expression
class Value(object):
	def __init__(self, value):
		self.value = value
		
	def eval(self, ctx):
		return self
	
	def getValue(self):
		return self.value

class Mul(object):
	def __init__(self, expr1, expr2):
		self.expr1 = expr1
		self.expr2 = expr2
	
	def eval(self, ctx):
		val1 = self.expr1.eval(ctx).getValue()
		val2 = self.expr2.eval(ctx).getValue()
		return Value(val1 * val2)

class Add(object):
	def __init__(self, expr1, expr2):
		self.expr1 = expr1
		self.expr2 = expr2
	
	def eval(self, ctx):
		val1 = self.expr1.eval(ctx).getValue()
		val2 = self.expr2.eval(ctx).getValue()
		return Value(val1 + val2)
	
class Equals(object):
	def __init__(self, expr1, expr2):
		self.expr1 = expr1
		self.expr2 = expr2
	
	def eval(self, ctx):
		val1 = self.expr1.eval(ctx).getValue()
		val2 = self.expr2.eval(ctx).getValue()
		return Value(val1 == val2)
	
class BitwiseAnd(object):
	def __init__(self, expr1, expr2):
		self.expr1 = expr1
		self.expr2 = expr2
	
	def eval(self, ctx):
		val1 = self.expr1.eval(ctx).getValue()
		val2 = self.expr2.eval(ctx).getValue()
		return Value(val1 & val2)
	
class If(object):
	def __init__(self, cond, expr1, expr2):
		self.condExpr = cond
		self.expr1 = expr1
		self.expr2 = expr2
		
	def eval(self, ctx):
		cond = self.condExpr.eval(ctx).getValue()
		if cond:
			return self.expr1.eval(ctx)
		else:
			return self.expr2.eval(ctx)
		
# ------------- value field BEG -------------------

class Field(object):
		
	def getAdvance(self):
		raise NotImplementedError("getAdvance method is not implemented!")
	
	def getSize(self):
		raise NotImplementedError("getSize method is not implemented!")
	
	def read(self, f, ctx):
		raise NotImplementedError("read method is not implemented!")
	
	def copy(self):
		return copy.deepcopy(self)
	
	def pretty_print(self, prefix="", indent="", **options):
		return indent + prefix + str(self)
	
class ValueField(Field):
	def __init__(self):
		self.value = None
		
	def getInternalFormat(self, ctx):
		raise NotImplementedError()
	
	def getAdvance(self, ctx):
		return struct.calcsize(self.getInternalFormat(ctx))
	
	def getSize(self):
		return self.getAdvance()
	
	def getValue(self):
		return self.value
	
	def eval(self, ctx):
		return self
	
	def read(self, f, ctx):
		self.value = f.get(self.getInternalFormat(ctx))
		
	def pretty_print(self, prefix="", indent="", **options):
		return indent + prefix + str(self.getValue())
		
class StringField(ValueField):
	def __init__(self, size):
		self.size = size
		
	def getInternalFormat(self, ctx):
		return "%ds" % (self.size.eval(ctx).getValue())
		
class NullTerminatedStringField(ValueField):
	def read(self, f, ctx):
		self.value = f.get_cstring()
		
	def getAdvance(self):
		return len(self.value) + 1
	
class Uint32Field(ValueField):
	def getInternalFormat(self, ctx):
		return "I"
		
class Int32Field(ValueField):
	def __init__(self):
		super(Int32Field, self).__init__()
		
	def getInternalFormat(self, ctx):
		return "i"
	
class Uint16Field(ValueField):
	def getInternalFormat(self, ctx):
		return "H"
	
class Int16Field(ValueField):
	def getInternalFormat(self, ctx):
		return "h"
	
class Uint8Field(ValueField):
	def getInternalFormat(self, ctx):
		return "B"
	
class FloatField(ValueField):
	def getInternalFormat(self, ctx):
		return "f"

class RawData(ValueField):
	def __init__(self, size):
		self.sizeExpr = size
		self.size = None
		
	def read(self, f, ctx):
		self.size = self.sizeExpr.eval(ctx).getValue()
		self.value = f.get_raw(self.size)
		
	def pretty_print(self, prefix="", indent="", **options):
		return indent + prefix + "###rawdata[%d]###" % self.size
	
# ---------------- value field END ------------------
		
# ---------------- special field BEG ----------------

class NullField(Field):
	def read(self, f, ctx):
		pass
	
	def pretty_print(self, prefix="", indent="", **options):
		return prefix + indent + "NULL"

class IfField(Field):
	def __init__(self, cond, expr1, expr2):
		self.condExpr = cond
		self.field1 = expr1
		self.field2 = expr2
		self.field = None
		
	def read(self, f, ctx):
		cond = self.condExpr.eval(ctx).getValue()
		if cond:
			self.field = self.field1
		else:
			self.field = self.field2
		self.field.read(f, ctx)
		
	def pretty_print(self, prefix="", indent="", **options):
		return self.field.pretty_print(prefix=prefix, indent=indent, **options)
	
class VarField(Field):
	def __init__(self, expr):
		self.expr = expr
		self.value = None
		
	def read(self, f, ctx):
		self.value = self.expr.eval(ctx).getValue()
	
	def eval(self, ctx):
		return self.expr.eval(ctx)
	
	def getAdvance(self):
		return 0
	
	def pretty_print(self, prefix="", indent="", **options):
		return indent + prefix + str(type(self.value)) + " = " + str(self.value)
		
class ArrayField(Field):
	def __init__(self, size, field):
		self.size = size
		self.fieldProto = field
		self.array = []
		
	def read(self, f, ctx):
		size = self.size.eval(ctx).getValue()
		
		env = ctx.getEnv()
		env.push()
		self.array = []		
		for i in xrange(size):
			env.set("I", Value(i))
			field = self.fieldProto.copy()
			field.read(f, ctx)
			self.array.append(field)
		env.pop()
		
	def pretty_print(self, prefix="", indent="", **options):
		lines = []
		lines.append(indent + prefix + "{")
		maxArraySize = options.get("maxArraySize", len(self.array))
		for i, field in enumerate(self.array[0: maxArraySize]):
			lines.append(field.pretty_print("[%d] = " % i, indent + "  ", **options))
		if maxArraySize < len(self.array):
			lines.append(indent + "  " + "... %d more elements" % (len(self.array) - maxArraySize))
		lines.append(indent + "}")
		return "\n".join(lines)
	
	def getChild(self, index):
		return self.array[int(index)]
	
class FieldGroup(Field):
	def __init__(self, fieldList):
		self.fieldList = fieldList
		
	def read(self, f, ctx):
		env = ctx.getEnv()
		env.push()
		for name, field in self.fieldList:
			env.set(name, field)
			field.read(f, ctx)
		env.pop()
			
	def getAdvance(self):
		advance = 0
		for name, field in self.fieldList:
			advance += field.getAdvance()
		return advance
	
	def getChild(self, name):
		for _name, _field in self.fieldList:
			if _name == name:
				return _field
		raise Exception("no such field as %s" % name)
	
	def pretty_print(self, prefix="", indent="", **options):
		lines = []
		lines.append(indent + prefix + "{")
		for name, field in self.fieldList:
			lines.append(field.pretty_print("%s = " % name, indent + "  ", **options))
		lines.append(indent + "}")
		return "\n".join(lines)
			
class FarBlock(Field):
	def __init__(self, offset, field):
		self.offsetExpr = offset
		self.field = field
	
	def getAdvance(self):
		return 0
	
	def read(self, f, ctx):
		oldOffset = f.offset
		offset = self.offsetExpr.eval(ctx).getValue()
		f.seek(offset)
		self.field.read(f, ctx)
		f.seek(oldOffset)
		
	def pretty_print(self, prefix="", indent="", **options):
		return self.field.pretty_print(prefix, indent, **options)
	
	def getChild(self, name):
		return self.field.getChild(name)
	
	def getValue(self):
		return self.field.getValue() 
		
class GetField(object):
	def __init__(self, fieldPath):
		self.fieldPath = fieldPath
	
	def eval(self, ctx):
		return ctx.getEnv().find(self.fieldPath).eval(ctx)
		
# ---------------- special field END -------------------
	
def Vector3Field():
	return FieldGroup([
		["x", FloatField()],
		["y", FloatField()],
		["z", FloatField()],
	])
	
def Vector2Field():
	return FieldGroup([
		["x", FloatField()],
		["y", FloatField()],
	])
		
# context
class ReadContext(object):
	def __init__(self, offset, endian):
		self.envStack = EnvStack()
	
	def getEnv(self):
		return self.envStack
	
class EnvStack(object):
	def __init__(self):
		self.envStack = []
		
	def push(self):
		self.envStack.append({})
		
	def pop(self):
		return self.envStack.pop()
	
	def get(self, key):
		for i in xrange(len(self.envStack) - 1, -1, -1):
			env = self.envStack[i]
			if key in env:
				return env[key]
		return None
	
	def set(self, key, value):
		self.envStack[-1][key] = value

	def find(self, path):
		nodes = self._preprocessPath(path)
		# find root var
		rootNode = self.get(nodes[0])
		if rootNode is None:
			raise Exception("can't find rootNode of %s" % path)
		# follow along node separated by /
		node = rootNode
		for j in xrange(1, len(nodes)):
			node = node.getChild(nodes[j])
			if node is None:
				raise Exception("can't find rootNode of %s" % path)
		return node
	
	def _preprocessPath(self, path):
		# replace content embraced by {}
		while True:
			hasReplaced, path = self._replace_embrace(path)
			if not hasReplaced:
				break
		# splitting nodes
		splits = path.replace("[", "/").replace("]", "/").rstrip("/").split("/")
		return splits
	
	def _replace_embrace(self, path):
		level = 0
		start, end = None, None
		for i, ch in enumerate(path):
			if ch == "{":
				if level == 0:
					start = i
				level += 1
			elif ch == "}":
				level -= 1
				if level == 0:
					end = i
					break
		if level != 0:
			raise Exception("embrace not matching!")
		if start is not None:
			assert end is not None, "embrace not matching!"
			field = self.find(path[start + 1: end])
			path = path[: start] + str(field.getValue()) + path[end + 1:]
			return True, path
		else:
			return False, path