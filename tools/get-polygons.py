#!/usr/bin/env python
#-*- coding: utf-8 -*-

import re
import sys
sys.path.append(".")
import osmose_config

list_polygons = []

for country in osmose_config.config.values():
  if country.polygon_id:
    if re.match("france_.*", country.country) and country.analyser_options["proj"] == 2154:
      list_polygons.append(str(1403916))
    elif re.match("^italy_.*", country.country):
      list_polygons.append(str(365331))
    elif re.match("^belgium_.*", country.country):
      list_polygons.append(str(52411))
    else:
      list_polygons.append(str(country.polygon_id))

list_polygons = set(list_polygons)

print ",".join(list_polygons)

