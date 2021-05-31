import vmraid
from vmraid import _, flt

from vmraid.model.document import Document


# ruleid: vmraid-modifying-but-not-comitting
def on_submit(self):
	if self.value_of_goods == 0:
		vmraid.throw(_('Value of goods cannot be 0'))
	self.status = 'Submitted'


# ok: vmraid-modifying-but-not-comitting
def on_submit(self):
	if self.value_of_goods == 0:
		vmraid.throw(_('Value of goods cannot be 0'))
	self.status = 'Submitted'
	self.db_set('status', 'Submitted')

# ok: vmraid-modifying-but-not-comitting
def on_submit(self):
	if self.value_of_goods == 0:
		vmraid.throw(_('Value of goods cannot be 0'))
	x = "y"
	self.status = x
	self.db_set('status', x)


# ok: vmraid-modifying-but-not-comitting
def on_submit(self):
	x = "y"
	self.status = x
	self.save()

# ruleid: vmraid-modifying-but-not-comitting-other-method
class DoctypeClass(Document):
	def on_submit(self):
		self.good_method()
		self.tainted_method()

	def tainted_method(self):
		self.status = "uptate"


# ok: vmraid-modifying-but-not-comitting-other-method
class DoctypeClass(Document):
	def on_submit(self):
		self.good_method()
		self.tainted_method()

	def tainted_method(self):
		self.status = "update"
		self.db_set("status", "update")

# ok: vmraid-modifying-but-not-comitting-other-method
class DoctypeClass(Document):
	def on_submit(self):
		self.good_method()
		self.tainted_method()
		self.save()

	def tainted_method(self):
		self.status = "uptate"
