#!/usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Frédéric Rodrigo 2014                                      ##
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

from Analyser_Merge import Analyser_Merge


class Analyser_Merge_Public_Transport_FR_TBC(Analyser_Merge):

    create_table = """
        x VARCHAR(254),
        y VARCHAR(254),
        gid VARCHAR(254),
        ident VARCHAR(254),
        adresse VARCHAR(254),
        campgps VARCHAR(254),
        codepost VARCHAR(254),
        nature VARCHAR(254),
        idmouvt VARCHAR(254),
        idsae VARCHAR(254),
        lignedes VARCHAR(254),
        longarr VARCHAR(254),
        datecrea VARCHAR(254),
        datedepl VARCHAR(254),
        dategear VARCHAR(254),
        dategemo VARCHAR(254),
        dategevo VARCHAR(254),
        mobilie1 VARCHAR(254),
        mobilie2 VARCHAR(254),
        mobilie3 VARCHAR(254),
        mobilie4 VARCHAR(254),
        nomarret VARCHAR(254),
        refmob1 VARCHAR(254),
        refmob2 VARCHAR(254),
        refmob3 VARCHAR(254),
        refmob4 VARCHAR(254),
        ville VARCHAR(254),
        arscol VARCHAR(254),
        prescorb VARCHAR(254),
        confort VARCHAR(254),
        nivacpmr VARCHAR(254),
        photo VARCHAR(254),
        artran VARCHAR(254),
        nivserv VARCHAR(254),
        reseau VARCHAR(254),
        geom_o VARCHAR(254),
        cdate VARCHAR(254),
        mdate VARCHAR(254)
    """

    def __init__(self, config, logger = None):
        self.missing_official = {"item":"8040", "class": 51, "level": 3, "tag": ["merge", "public transport"], "desc": T_(u"TBC stop not integrated") }
        self.possible_merge   = {"item":"8041", "class": 53, "level": 3, "tag": ["merge", "public transport"], "desc": T_(u"TBC stop, integration suggestion") }
        Analyser_Merge.__init__(self, config, logger)
        self.officialURL = "http://data.lacub.fr/data.php?themes=10"
        self.officialName = "Arrêt physique sur le réseau"
        self.csv_file = "merge_data/public_transport_FR_tbc.csv"
        self.csv_format = "WITH DELIMITER AS ',' NULL AS '' CSV HEADER"
        self.csv_encoding = "ISO-8859-15"
        self.csv_select = {
            "reseau": [None, "BUS"]
        }
        self.osmTags = {"highway": "bus_stop"}
        self.osmTypes = ["nodes", "ways"]
        self.sourceTable = "tbc"
        self.sourceX = "x"
        self.sourceY = "y"
        self.sourceSRID = "2154"
        self.defaultTag = {
            "source": "Communauté Urbaine de Bordeaux - 03/2014",
            "highway": "bus_stop",
            "public_transport": "stop_position",
            "bus": "yes",
            "network": "TBC",
        }
        self.defaultTagMapping = {
            "name": lambda res: res['nomarret'],
            "shelter": lambda res: "yes" if "abribus" in res["mobile1"].lower() else "no" if "poteau" in res["mobile1"].lower() else None,
        }
        self.conflationDistance = 100
        self.text = lambda tags, fields: {"en": u"TBC stop %s" % fields["nomarret"], "fr": u"Arrêt TBC %s" % fields["nomarret"]}
