# -*- coding: utf-8 -*-
# This file is part of HPCStats
#
# Copyright (C) 2011-2012 EDF SA
# Contact:
#       CCN - HPC <dsp-cspit-ccn-hpc@edf.fr>
#       1, Avenue du General de Gaulle
#       92140 Clamart
#
#
#Authors: CCN - HPC <dsp-cspit-ccn-hpc@edf.fr>
#This program is free software; you can redistribute in and/or
#modify it under the terms of the GNU General Public License,
#version 2, as published by the Free Software Foundation.
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#On Calibre systems, the complete text of the GNU General
#Public License can be found in `/usr/share/common-licenses/GPL'.

###############################################################

import logging
import psycopg2

class HPCStatsdb:

    def __init__(self, dbhostname, dbport, dbname, dbuser, dbpassword):
        """ This object is a singleton class, this means only one instance will be created """
        self.database = {
            'dbhostname': dbhostname,
            'dbport':     dbport,
            'dbname':     dbname,
            'dbuser':     dbuser,
            'dbpassword': dbpassword,
        }
        self._cur = None
        self._conn = None

    def infos(self):
        return self.database["dbhostname"], self.database["dbport"], self.database["dbname"],self.database["dbuser"], self.database["dbpassword"]

    def bind(self):
        """ Connection to the database """
        self._conn = psycopg2.connect("host = %(dbhostname)s dbname= %(dbname)s user= %(dbuser)s password= %(dbpassword)s" % self.database)
        self._cur = self._conn.cursor()
        return self._cur, self._conn

    def unbind(self):
        """ Disconnect from the database """
        self._conn.close()

    def execute(self, req, datas):
        try:
            self._cur.execute(req, datas)
        except psycopg2.IntegrityError, exception_error_msg:
            logging.error("integrity error %s", exception_error_msg )
            logging.error(self._cur.mogrify(req, datas))

    def get_cur(self):
        return self._cur

    def get_conn(self):
        return self._conn

    def commit(self):
        self._conn.commit()
