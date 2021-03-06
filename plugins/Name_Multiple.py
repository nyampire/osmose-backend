#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Yoann Arnaud <yarnaud@crans.org> 2009                       ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
##                                                                       ##
###########################################################################

from plugins.Plugin import Plugin


class Name_Multiple(Plugin):

    def init(self, logger):
        Plugin.init(self, logger)
        self.errors[705] = { "item": 5030, "level": 1, "tag": ["name", "fix:survey"], "desc": T_(u"The name tag contains two names") }

        import re
        self.Re1 = re.compile(u"^.*;.*$")
        self.Re2 = re.compile(u"^.*/.*$")
        self.Re3 = re.compile(u"^.*\+.+$")

    def way(self, data, tags, nds):
        if u"name" not in tags:
            return
        if u"aeroway" in tags:
            return

        if self.Re1.match(tags["name"]):
            return [(705,0,{"en": "name=%s" % tags["name"]})]
        if self.Re2.match(tags["name"]):
            return [(705,1,{"en": "name=%s" % tags["name"]})]
        if self.Re3.match(tags["name"]):
            return [(705,2,{"en": "name=%s" % tags["name"]})]

###########################################################################
from plugins.Plugin import TestPluginCommon

class Test(TestPluginCommon):
    def setUp(self):
        TestPluginCommon.setUp(self)
        self.p = Name_Multiple(None)
        self.p.init(None)

    def test(self):
        self.check_err(self.p.way(None, {"name": "aueuie ; ueuaeuie"}, None))
        self.check_err(self.p.way(None, {"name": "aueuie / ueuaeuie"}, None))
        self.check_err(self.p.way(None, {"name": "aueuie + ueuaeuie"}, None))
        assert not self.p.way(None, {"name": "aueuie + ueuaeuie", "aeroway": "yes"}, None)
