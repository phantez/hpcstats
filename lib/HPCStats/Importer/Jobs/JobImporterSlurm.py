#!/usr/bin/python
# -*- coding: utf-8 -*-

#from HPCStats.Importer.Jobs.JobImporter import JobImporter
from HPCStats.Model.Job import Job
import MySQLdb
from datetime import datetime

#class JobImporterSlurm(JobImporter):
class JobImporterSlurm(object):

    def __init__(self, db, config, cluster_name):
        self._db = db
        self._conf = config
        self._cluster_name = cluster_name

        db_section = "ivanoe/slurm"

        self._dbhost = config.get(db_section,"host")
        self._dbport = int(config.get(db_section,"port"))
        self._dbname = config.get(db_section,"name")
        self._dbuser = config.get(db_section,"user")
        self._dbpass = config.get(db_section,"password")
        self._conn = MySQLdb.connect(host = self._dbhost, user = self._dbuser, passwd = self._dbpass, db = self._dbname, port = self._dbport)
        self._cur = self._conn.cursor(MySQLdb.cursors.DictCursor)

   
    def request_jobs_since_job_id(self, job_id):
        req = "SELECT id_job, id_user, id_group, time_submit, time_start, time_end, nodes_alloc, cpus_alloc, partition, state, nodelist FROM %s_job_table where id_job > %s" % (self._cluster_name, job_id)
        self._cur.execute(req)
        results = self._cur.fetchall()
        return results

    def request_job(self, job_id):
        req = "SELECT id_job, id_user, id_group, time_submit, time_start, time_end, nodes_alloc, cpus_alloc, partition, state, nodelist FROM %s_job_table where id_job = %s" % (self._cluster_name, job_id)
        self._cur.execute(req)
        results = self._cur.fetchall()
        return results

    def get_job_information_from_id_job_list(self,ids_job):
        jobs = []
        for id_job in ids_job:
            result = self.request_job(id_job)
            jobs.append(self.job_from_information(result[0]))
        return jobs

    def get_job_for_id_above(self, id_job):
        jobs = []
        results = self.request_jobs_since_job_id(id_job)
        for result in results:
            jobs.append(self.job_from_information(result))
        return jobs
   
    def job_from_information(self, res):
        job = Job(  id_job = res["id_job"],
                    uid = res["id_user"],
                    gid = res["id_group"],
                    submission_datetime = datetime.fromtimestamp(res["time_submit"]),
                    running_datetime = datetime.fromtimestamp(res["time_start"]),
                    end_datetime = datetime.fromtimestamp(res["time_end"]),
                    nb_procs = res["cpus_alloc"],
                    nb_hosts =  res["nodes_alloc"],
                    running_queue = res["partition"],
                    nodes = res["nodelist"],
                    state = self.get_job_state_from_slurm_state(res["state"]),
                    clustername = self._cluster_name)
        return job


    """
        From slurm.h.inc
            enum job_states {
            JOB_PENDING, /* queued waiting for initiation */
            JOB_RUNNING, /* allocated resources and executing */
            JOB_SUSPENDED, /* allocated resources, execution suspended */
            JOB_COMPLETE, /* completed execution successfully */
            JOB_CANCELLED, /* cancelled by user */
            JOB_FAILED, /* completed execution unsuccessfully */
            JOB_TIMEOUT, /* terminated on reaching time limit */
            JOB_NODE_FAIL, /* terminated on node failure */
            JOB_PREEMPTED, /* terminated due to preemption */
            JOB_END /* not a real state, last entry in table */
            };
    """
    def get_job_state_from_slurm_state(self, state):
        slurm_state = {
            0:"PENDING", # queued waiting for initiation 
            1:"RUNNING", # allocated resources and executing 
            2:"SUSPENDED", # allocated resources, execution suspended 
            3:"COMPLETE", # completed execution successfully 
            4:"CANCELLED", # cancelled by user 
            5:"FAILED", # completed execution unsuccessfully 
            6:"TIMEOUT", # terminated on reaching time limit 
            7:"NODE_FAIL", # terminated on node failure 
            8:"PREEMPTED", # terminated due to preemption 
            9:"END" # not a real state, last entry in table 
        }
        return slurm_state[state]

            

# TO BE MOVED IN ABSTRACT FUNCTION
    def get_last_job_id(self):
        last_job_id = 0
        req = "SELECT MAX(id_job) AS last_id FROM jobs WHERE clustername = '%s'" % (self._cluster_name)
        cur = self._db.get_cur()
        cur.execute(req)
        results = cur.fetchall()
        for job in results:
            if last_job_id < job[0]:
                last_job_id = job[0]
        return last_job_id

    def get_unfinished_job_id(self):
        unfinished_job_id = []
        req = "SELECT id_job FROM jobs WHERE state = 'unfinished'" 
        cur = self._db.get_cur()
        cur.execute(req)
        results = cur.fetchall()
        for job in results:
            unfinished_job_id.append(job[0])
        return unfinished_job_id

