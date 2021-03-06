#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Frédéric Rodrigo 2011                                      ##
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
import urllib


class TagFix_Wikipedia(Plugin):
    def init(self, logger):
        Plugin.init(self, logger)
        self.errors[30310] = { "item": 3031, "level": 2, "tag": ["value", "wikipedia", "fix:chair"], "desc": T_(u"Not a Wikipedia URL") }
        self.errors[30311] = { "item": 3031, "level": 2, "tag": ["value", "wikipedia", "fix:chair"], "desc": T_(u"Wikipedia URL instead of article title") }
        self.errors[30312] = { "item": 3031, "level": 2, "tag": ["value", "wikipedia", "fix:chair"], "desc": T_(u"Missing Wikipedia language before article title") }
        self.errors[30313] = { "item": 3031, "level": 2, "tag": ["value", "wikipedia", "fix:chair"], "desc": T_(u"Use human Wikipedia page title"), "fr": u"Utilisez le nom tel qu'il apparait dans l'article, et non telqu'il apparait dans l'URL de la page" }
        self.errors[30314] = { "item": 3031, "level": 2, "tag": ["value", "wikipedia", "fix:chair"], "desc": T_(u"Missing primary Wikipedia tag") }
        self.errors[30315] = { "item": 3031, "level": 2, "tag": ["value", "wikipedia", "fix:chair"], "desc": T_(u"Invalid wikipedia suffix") }
        self.errors[30316] = { "item": 3031, "level": 2, "tag": ["value", "wikipedia", "fix:chair"], "desc": T_(u"Duplicate wikipedia tag as suffix and prefix") }

        import re
        self.wiki_regexp = re.compile(u"(https?://)?([^\.]+)\.wikipedia.+/wiki/(.+)")
        self.lang_regexp = re.compile(u"[-a-z]+:.*")
        self.lang_restriction_regexp = re.compile(u"^[a-z]{2}$")

    def human_readable(self, string):
        try:
            string = urllib.unquote(string.encode('ascii')).decode('utf8')
        except:
            pass
        return string.replace("_"," ")

    def analyse(self, tags, wikipediaTag="wikipedia"):
        err=[]
        if wikipediaTag in tags:
            m = self.wiki_regexp.match(tags[wikipediaTag])
            if (tags[wikipediaTag].startswith("http://") or tags[wikipediaTag].startswith("https://")) and not m:
                # tag 'wikipedia' starts with 'http://' but it's not a wikipedia url
                return [(30310, 0, {})]
            elif m:
                # tag 'wikipedia' seams to be an url
                return [(30311, 1, {"en": u"Use wikipedia=%s:*" % m.group(2), "fix": {wikipediaTag: "%s:%s" % (m.group(2), self.human_readable(m.group(3)))} })]

            if not self.lang_regexp.match(tags[wikipediaTag]):
                err.append((30312, 2, {}))
            else:
                prefix = tags[wikipediaTag].split(':', 1)[0]
                tag = wikipediaTag+':'+prefix
                if tag in tags:
                    err.append((30316, 6, {"fix": {'-': [tag]}} ))
            if "%" in tags[wikipediaTag] or "_" in tags[wikipediaTag]:
                err.append((30313, 3, {"fix": {wikipediaTag: self.human_readable(tags[wikipediaTag])}} ))

        for tag in [t for t in tags if t.startswith(wikipediaTag+":")]:
            suffix = tag[len(wikipediaTag)+1:]
            if ":" in suffix:
                suffix = suffix.split(":")[0]

            if suffix in tags:
                # wikipedia:xxxx only authorized if tag xxxx exist
                err.extend(self.analyse(tags, wikipediaTag+":"+suffix))

            elif self.lang_restriction_regexp.match(suffix):
                if not wikipediaTag in tags:
                    m = self.wiki_regexp.match(tags[tag])
                    if m:
                        value = self.human_readable(m.group(3))
                    elif tags[tag].startswith(suffix+":"):
                        value = tags[tag][len(suffix)+1:]
                    else:
                        value = self.human_readable(tags[tag])
                    err.append((30314, 4, {"fix": {'-': [tag], '+':{wikipediaTag: "%s:%s" % (suffix, value)}}} ))
            else:
                err.append((30315, 5, {"en": u"Invalid wikipedia suffix '%s'" % suffix} ))
        return err

    def node(self, data, tags):
        return self.analyse(tags)

    def way(self, data, tags, nds):
        return self.analyse(tags)

    def relation(self, data, tags, members):
        return self.analyse(tags)


###########################################################################
from plugins.Plugin import TestPluginCommon

class Test(TestPluginCommon):
    def setUp(self):
        TestPluginCommon.setUp(self)
        self.analyser = TagFix_Wikipedia(None)
        self.analyser.init(None)

    def check(self, tags, has_error, fix=None):
        errors = self.analyser.analyse(tags)
        errors_msg = [self.analyser.errors[e[0]]["desc"]["en"] for e in errors]+[e[2]["en"] for e in errors if "en" in e[2]]
        errors_fix = [e[2].get("fix") for e in errors]
        if has_error==False and errors_msg:
            print "FAIL:%s\nshould not have errors\nCurrent errors: %s\n"%(tags, errors_msg)
            return 1
        if has_error and has_error not in errors_msg:
            print "FAIL:%s\nshould have error '%s'\ninstead of      %s\n"%(tags, has_error, errors_msg)
            return 1
        if fix and fix not in errors_fix:
            print "FAIL:%s\nshould have fix %s\ninstead of     %s\n"%(tags, fix, errors_fix)
            return 1
        if has_error:
            self.check_err(errors, (tags, errors_msg))
        return 0

    def test(self):
        err = 0

        err += self.check( { "wikipedia": "fr:Tour Eiffel"},
                           has_error=False)

        err += self.check( { "wikipedia": "fr:Tour Eiffel",
                             "wikipedia:de" : "Eiffelturm"},
                           has_error=False)
        # add check on synonyme

        # Don't use URL directly
        err += self.check( { "wikipedia": "http://www.google.fr"},
                           has_error="Not a Wikipedia URL")

        err += self.check( { "wikipedia": "http://fr.wikipedia.org/wiki/Tour_Eiffel"},
                           has_error="Wikipedia URL instead of article title",
                           fix={ "wikipedia": u"fr:Tour Eiffel"})

        err += self.check( { "wikipedia": "https://fr.wikipedia.org/wiki/Tour_Eiffel"},
                           has_error="Wikipedia URL instead of article title",
                           fix={ "wikipedia": u"fr:Tour Eiffel"})

        err += self.check( { "wikipedia": "fr.wikipedia.org/wiki/Tour_Eiffel"},
                           has_error="Wikipedia URL instead of article title",
                           fix={ "wikipedia": u"fr:Tour Eiffel"})

        # Tag 'wikipedia:lang' can be used only in complement of 'wikipedia=lang:xxxx'
        err += self.check( {"wikipedia:fr" : u"Tour Eiffel"},
                           has_error=u"Missing primary Wikipedia tag",
                           fix={'+': {'wikipedia': u'fr:Tour Eiffel'}, '-': ['wikipedia:fr']})

        err += self.check( {"wikipedia:fr" : u"fr:Tour Eiffel"},
                           has_error=u"Missing primary Wikipedia tag",
                           fix={'+': {'wikipedia': u'fr:Tour Eiffel'}, '-': ['wikipedia:fr']})

        err += self.check( { "wikipedia:fr": "http://fr.wikipedia.org/wiki/Tour_Eiffel"},
                           has_error=u"Missing primary Wikipedia tag",
                           fix={'+': {'wikipedia': u'fr:Tour Eiffel'}, '-': ['wikipedia:fr']})

        err += self.check( { "wikipedia:fr": "fr.wikipedia.org/wiki/Tour_Eiffel"},
                           has_error=u"Missing primary Wikipedia tag",
                           fix={'+': {'wikipedia': u'fr:Tour Eiffel'}, '-': ['wikipedia:fr']})

        # Missing lang in value
        err += self.check( { "wikipedia": "Tour Eiffel"},
                           has_error=u"Missing Wikipedia language before article title")

        # Human readeable
        err += self.check( { "wikipedia": "fr:Tour_Eiffel"},
                           has_error=u"Use human Wikipedia page title",
                           fix={ "wikipedia": u"fr:Tour Eiffel"})

        err += self.check( { "wikipedia": u"fr:Château_de_Gruyères_(Ardennes)"},
                           has_error=u"Use human Wikipedia page title",
                           fix={ "wikipedia": u"fr:Château de Gruyères (Ardennes)"})

        err += self.check( { "name" : "Rue Jules Verne",
                             "wikipedia:name": "fr:Jules Verne"},
                           has_error=False)

        err += self.check( { "name" : "Rue Jules Verne",
                             "wikipedia:name": "fr:Jules Verne",
                             "wikipedia:name:de" : "Jules Verne"},
                           has_error=False)

        # Don't use URL directly
        err += self.check( { "name" : "Rue Jules Verne",
                             "wikipedia:name": "http://www.google.fr"},
                           has_error="Not a Wikipedia URL")

        err += self.check( { "name" : "Rue Jules Verne",
                             "wikipedia:name": "http://fr.wikipedia.org/wiki/Jules_Verne"},
                           has_error="Wikipedia URL instead of article title",
                           fix={ "wikipedia:name": u"fr:Jules Verne"})

        err += self.check( { "name" : "Rue Jules Verne",
                             "wikipedia:name": "fr.wikipedia.org/wiki/Jules_Verne"},
                           has_error="Wikipedia URL instead of article title",
                           fix={ "wikipedia:name": u"fr:Jules Verne"})

        # Tag 'wikipedia:lang' can be used only in complement of 'wikipedia=lang:xxxx'
        err += self.check( { "name" : "Rue Jules Verne",
                             "wikipedia:name:fr" : u"Jules Verne"},
                           has_error=u"Missing primary Wikipedia tag",
                           fix={'+': {'wikipedia:name': u'fr:Jules Verne'}, '-': ['wikipedia:name:fr']})

        # Missing lang in value
        err += self.check( { "name" : "Rue Jules Verne",
                             "wikipedia:name": "Jules Verne"},
                           has_error=u"Missing Wikipedia language before article title")

        # Human readable
        err += self.check( { "name" : "Rue Jules Verne",
                             "wikipedia:name": "fr:Jules_Verne"},
                           has_error=u"Use human Wikipedia page title",
                           fix={ "wikipedia:name": u"fr:Jules Verne"})

        err += self.check( { "name" : "Gare SNCF",
                             "operator": "Sncf",
                             "wikipedia:operator": "fr:Sncf"},
                           has_error=False)

        err += self.check( { "wikipedia:toto": "quelque chose"},
                           has_error=u"Invalid wikipedia suffix 'toto'")

        err += self.check( { "wikipedia:fr": "quelque chose", "wikipedia": "fr:autre chose"},
                           has_error=u"Duplicate wikipedia tag as suffix and prefix")

        if err:
            print "%i errors" % err
        assert not err
        
