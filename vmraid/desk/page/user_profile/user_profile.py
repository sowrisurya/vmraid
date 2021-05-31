import vmraid
from datetime import datetime
from vmraid.utils import getdate

@vmraid.whitelist()
def get_energy_points_heatmap_data(user, date):
	try:
		date = getdate(date)
	except Exception:
		date = getdate()

	return dict(vmraid.db.sql("""select unix_timestamp(date(creation)), sum(points)
		from `tabEnergy Point Log`
		where
			date(creation) > subdate('{date}', interval 1 year) and
			date(creation) < subdate('{date}', interval -1 year) and
			user = %s and
			type != 'Review'
		group by date(creation)
		order by creation asc""".format(date = date), user))


@vmraid.whitelist()
def get_energy_points_percentage_chart_data(user, field):
	result = vmraid.db.get_all('Energy Point Log',
		filters = {'user': user, 'type': ['!=', 'Review']},
		group_by = field,
		order_by = field,
		fields = [field, 'ABS(sum(points)) as points'],
		as_list = True)

	return {
		"labels": [r[0] for r in result if r[0] != None],
		"datasets": [{
			"values": [r[1] for r in result]
		}]
	}

@vmraid.whitelist()
def get_user_rank(user):
	month_start = datetime.today().replace(day=1)
	monthly_rank = vmraid.db.get_all('Energy Point Log',
		group_by = 'user',
		filters = {'creation': ['>', month_start], 'type' : ['!=', 'Review']},
		fields = ['user', 'sum(points)'],
		order_by = 'sum(points) desc',
		as_list = True)

	all_time_rank = vmraid.db.get_all('Energy Point Log',
		group_by = 'user',
		filters = {'type' : ['!=', 'Review']},
		fields = ['user', 'sum(points)'],
		order_by = 'sum(points) desc',
		as_list = True)

	return {
	'monthly_rank': [i+1 for i, r in enumerate(monthly_rank) if r[0] == user],
	'all_time_rank': [i+1 for i, r in enumerate(all_time_rank) if r[0] == user]
	}


@vmraid.whitelist()
def update_profile_info(profile_info):
	profile_info = vmraid.parse_json(profile_info)
	keys = ['location', 'interest', 'user_image', 'bio']

	for key in keys:
		if key not in profile_info:
			profile_info[key] = None

	user = vmraid.get_doc('User', vmraid.session.user)
	user.update(profile_info)
	user.save()
	return user

@vmraid.whitelist()
def get_energy_points_list(start, limit, user):
	return vmraid.db.get_list('Energy Point Log',
		filters = {'user': user, 'type': ['!=', 'Review']},
		fields = ['name','user', 'points', 'reference_doctype', 'reference_name', 'reason',
			'type', 'seen', 'rule', 'owner', 'creation', 'revert_of'],
		start = start,
		limit = limit,
		order_by = 'creation desc')
