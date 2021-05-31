from __future__ import print_function, unicode_literals
'''
Check for unused CSS Classes

sUpdate source and target apps below and run from CLI

	bench --site [sitename] execute vmraid.website.purifycss.purify.css

'''

import vmraid, re, os

source = vmraid.get_app_path('vmraid_theme', 'public', 'less', 'vmraid_theme.less')
target_apps = ['erpadda_com', 'vmraid_io', 'translator', 'chart_of_accounts_builder', 'vmraid_theme']

def purifycss():
	with open(source, 'r') as f:
		src = f.read()

	classes = []
	for line in src.splitlines():
		line = line.strip()
		if not line:
			continue
		if line[0]=='@':
			continue
		classes.extend(re.findall('\.([^0-9][^ :&.{,(]*)', line))

	classes = list(set(classes))

	for app in target_apps:
		for basepath, folders, files in os.walk(vmraid.get_app_path(app)):
			for fname in files:
				if fname.endswith('.html') or fname.endswith('.md'):
					#print 'checking {0}...'.format(fname)
					with open(os.path.join(basepath, fname), 'r') as f:
						src = f.read()
					for c in classes:
						if c in src:
							classes.remove(c)

	for c in sorted(classes):
		print(c)
