#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from HPCStats.Importer.Users.UserImporterXLSLdapSlurm import UserImporterXLSLdapSlurm
from HPCStats.Importer.Users.UserImporterLdap import UserImporterLdap

class UserImporterFactory(object):

    def __init__(self):
        pass

    def factory(self, db, config, cluster_name):
        if config.get(cluster_name, "users") == "xls+ldap+slurm":
            return UserImporterXLSLdapSlurm(db, config, cluster_name)
        elif config.get(cluster_name, "users") == "ldap":
            return UserImporterLdap(db, config, cluster_name)
        else:
            logging.critical("TO BE CODED")
            # Throw Exception
        return None
