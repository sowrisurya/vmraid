from __future__ import unicode_literals

def execute():
	from vmraid.geo.country_info import get_all
	import vmraid.utils.install

	countries = get_all()
	vmraid.utils.install.add_country_and_currency("Ghana", vmraid._dict(countries["Ghana"]))
