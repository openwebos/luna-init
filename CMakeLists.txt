# @@@LICENSE
#
# Copyright (c) 2012-2014 LG Electronics, Inc.
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

cmake_minimum_required(VERSION 2.8.7)

project(luna-init NONE)

include(webOS/webOS)
webos_modules_init(1 0 0 QUALIFIER RC3)
webos_component(2 0 1)
webos_config_build_doxygen(doc Doxyfile)

# ext-timezones.json
add_custom_command(
	OUTPUT ext-timezones.json
	COMMAND echo "Generating ext-timezones.json"
	COMMAND python2
		${CMAKE_SOURCE_DIR}/src/gen-ext-timezones.py
		-s ${CMAKE_SOURCE_DIR}/src
		-o ext-timezones.json
	DEPENDS src/gen-ext-timezones.py
	        src/mccInfo.json
	        src/uiTzInfo.json
	        src/abbrevs.py
)

set(ext_timezones_json ${CMAKE_CURRENT_BINARY_DIR}/ext-timezones.json)

add_custom_target(generate ALL DEPENDS ext-timezones.json)

# install json files in /usr/palm
MESSAGE (STATUS, "Install json files in ${WEBOS_INSTALL_WEBOS_PREFIX}")
install(DIRECTORY files/conf/ DESTINATION ${WEBOS_INSTALL_WEBOS_PREFIX} 
        PATTERN "svn"         EXCLUDE 
        PATTERN ".svn"        EXCLUDE
	PATTERN "fonts"       EXCLUDE
	PATTERN "region.json" EXCLUDE
	PATTERN ".json"       PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
)
install(FILES ${ext_timezones_json} DESTINATION ${WEBOS_INSTALL_WEBOS_PREFIX}
	PERMISSIONS OWNER_READ OWNER_WRITE)

# install region json file in /etc/palm
MESSAGE (STATUS, "Install region.json in ${WEBOS_INSTALL_WEBOS_SYSCONFDIR}")
install(FILES files/conf/region.json DESTINATION ${WEBOS_INSTALL_WEBOS_SYSCONFDIR} 
	PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE)

# install font files /usr/share/fonts
MESSAGE (STATUS, "Install fonts in ${WEBOS_INSTALL_DATADIR}")
install(DIRECTORY files/conf/fonts DESTINATION ${WEBOS_INSTALL_DATADIR} 
        PATTERN "fonts.tgz" EXCLUDE
        PATTERN "svn"  EXCLUDE 
        PATTERN ".svn" EXCLUDE
	PATTERN ".xml" PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
    PATTERN ".ttf" PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
    PATTERN ".txt" PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE
)

