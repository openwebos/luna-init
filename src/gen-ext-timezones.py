#!/usr/bin/env python2
# @@@LICENSE
#
# Copyright (c) 2014 LG Electronics, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# LICENSE@@@

import sys, os.path, os
from getopt import gnu_getopt as getopt
from datetime import datetime
from itertools import *
import pytz
import json
from abbrevs import abbrevs

def findDST(tz, months = [datetime(datetime.utcnow().year, n+1, 1) for n in range(12)]):
	try:
		std = next(dropwhile(lambda m: tz.dst(m).seconds != 0, months))
	except StopIteration: # next raises this if empty list
		raise Exception("Standart time should be present in any time-zone (even in %s)" % (tz))
	summer = next(chain(dropwhile(lambda m: tz.dst(m).seconds == 0, months), [None]))
	return (std, summer)

def genTimeZones(do_guess = True):
	for (cc, zoneIds) in pytz.country_timezones.items():
		for zoneId in zoneIds:
			tz = pytz.timezone(zoneId)
			try:
				(std, summer) = findDST(tz)
			except Exception as e:
				sys.stderr.write("Exception: %s\n  Do some magic for %s\n" % (e, tz))
				std = datetime(datetime.utcnow().year, 1, 1)
				if tz.dst(std).seconds != 0: summer = std
				else: summer = None
			except StopIteration:
				raise Exception("Unexpected StopIteration")

			# use Country from tzdata
			country = pytz.country_names[cc]

			info = uiInfo.get(zoneId, None)
			if info is None:
				if not do_guess:
					# so we shouldn't try to guess?
					# lets skip unknown time-zones
					continue
				# guess City
				(zregion, zpoint) = zoneId.split('/',1)
				if zpoint != country: city = zpoint.replace('_',' ')
				else: city = ''
				# guess Description
				tzname = tz.tzname(std)
				description = abbrevs.get(tzname, tzname)
				preferred = False
			else:
				country = info.get('Country', country) # allow override
				city = info['City']
				description = info['Description']
				preferred = info.get('preferred', False)

			entry = {
				'Country': country,
				'CountryCode': cc,
				'ZoneID': zoneId,
				'supportsDST': 0 if summer is None else 1,
				'offsetFromUTC': int(tz.utcoffset(std).total_seconds()/60),
				'Description': description,
				'City': city
			}
			if preferred: entry['preferred'] = True
			yield entry

def genSysZones():
	for offset in takewhile(lambda x: x < 12.5, count(-14, 0.5)):
		offset_str = str(abs(int(offset)))
		if offset != int(offset): offset_str = offset_str + ":30"
		if offset > 0: ids = [('Etc/GMT+%s' % offset_str, 'GMT-%s' % offset_str)]
		elif offset < 0: ids = [('Etc/GMT-%s' % offset_str, 'GMT+%s' % offset_str)]
		else: ids = [('Etc/' + x, 'GMT') for x in ['GMT-0', 'GMT+0']]
		for (zoneId, id) in ids:
			yield {
				'Country': '',
				'CountryCode': '',
				'ZoneID': zoneId,
				'supportsDST': 0,
				'offsetFromUTC': int(-offset*60),
				'Description': id,
				'City': ''
			}

### Parse options

output = None
source_dir = os.path.curdir
is_zoneinfo_default = True

def set_zoneinfo_dir(zoneinfo_dir):
	global is_zoneinfo_default
	is_zoneinfo_default = False
	def resource_path(name):
		if os.path.isabs(name):
			raise ValueError('Bad path (absolute): %r' % name)
		name_parts = os.path.split(name)
		for part in name_parts:
			if part == os.path.pardir:
				raise ValueError('Bad path segment: %r' % part)
		filepath = os.path.join(zoneinfo_dir, *name_parts)
		return filepath
	pytz.open_resource = lambda name: open(resource_path(name), 'rb')
	pytz.resource_exists = lambda name: os.path.exists(resource_path(name))


opts, args = getopt(sys.argv[1:], 'z:o:s:w', longopts=[
	'zoneinfo-dir=', 'output=', 'source-dir=', 'no-guess', 'white-list-only'
	])

do_guess = True

for (opt, val) in opts:
	if opt in ('--zoneinfo-dir', '-z'): set_zoneinfo_dir(val)
	elif opt in ('--output', '-o'): output = val
	elif opt in ('--source-dir', '-s'): source_dir = val
	elif opt in ('--no-guess', '--white-list-only', '-w'): do_guess = False

# openembedded sets some env variables. lets guess from one of it where is our sysroot.
guess_sysroot = os.environ.get('PKG_CONFIG_SYSROOT_DIR')
if guess_sysroot is not None and is_zoneinfo_default:
	set_zoneinfo_dir(os.path.join(guess_sysroot, 'usr', 'share', 'zoneinfo'))


### load reference files
mccInfo = json.load(open(os.path.join(source_dir, 'mccInfo.json'), 'rb'))
uiInfo = json.load(open(os.path.join(source_dir, 'uiTzInfo.json'), 'rb'))

### load natural timezones from pytz

timeZones = list(genTimeZones(do_guess = do_guess))
timeZones.sort(lambda x, y: cmp(x['offsetFromUTC'], y['offsetFromUTC']))

# gen Etc/* time-zones
sysZones = list(genSysZones())

content = {
	'timeZone': timeZones,
	'syszones': sysZones,
	'mmcInfo': mccInfo
}

if output is None:
	import re
	s = json.dumps(content, ensure_ascii = False, indent = 2)
	s = re.sub(r'\s+$', '', s, flags = re.MULTILINE) + '\n'
	sys.stdout.write(s.encode('utf8'))
else:
	s = json.dumps(content, ensure_ascii = False, indent = None, separators = (',', ':')) + '\n'
	open(output,'wb').write(s.encode('utf8'))
