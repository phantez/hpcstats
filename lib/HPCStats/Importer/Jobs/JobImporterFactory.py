#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from HPCStats.Importer.Jobs.JobImporterSlurm import JobImporterSlurm
from HPCStats.Importer.Jobs.JobImporterTorque import JobImporterTorque

class JobImporterFactory(object):

    def __init__(self):
        pass

    def factory(self, db, config, cluster_name):
        if config.get(cluster_name, "jobs") == "slurm": ## Slurm
            return JobImporterSlurm(db, config, cluster_name)
        elif config.get(cluster_name, "jobs") == "torque": ## Torque
            return JobImporterTorque(db, config, cluster_name)
        else:
            logging.critical("TO BE CODED")
            # Throw Exception
        return None
