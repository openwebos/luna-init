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

# this script used for extracting uiTzInfo.json from old ext-timezones.json

import json, sys, re

original = json.load(sys.stdin)

ui_info  = {}

for tz in original['timeZone']:
	info = {
		'Country': tz['Country'],
		'City': tz['City'],
		'Description': tz['Description'],
	}
	if tz.get('preferred', False):
		info['preferred'] = True
	ui_info[tz['ZoneID']] = info

s = json.dumps(ui_info, ensure_ascii = False, indent = 2)
s = re.sub(r'\s+$', '', s, flags = re.MULTILINE) + '\n'
sys.stdout.write(s.encode('utf8'))
