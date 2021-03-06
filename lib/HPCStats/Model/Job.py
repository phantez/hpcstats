#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
import logging
import string
from ClusterShell.NodeSet import NodeSet, NodeSetParseRangeError

class Job:

    def __init__( self,
                  db_id = 0,
                  id_job = 0,
                  sched_id = 0,
                  cluster_name = "",
                  uid = -1,
                  gid = -1,
                  submission_datetime = 0,
                  running_datetime = 0,
                  end_datetime = 0,
                  nb_procs = 0,
                  nb_hosts = 0,
                  running_queue = "",
                  nodes = "",
                  state = "unknown" ):
        self._db_id = db_id
        self._sched_id = sched_id
        self._id_job = id_job
        self._cluster_name = cluster_name
        self._uid = uid
        self._gid = gid
        self._submission_datetime = submission_datetime
        self._running_datetime = running_datetime
        self._end_datetime = end_datetime
        self._nb_procs = nb_procs
        self._nb_hosts = nb_hosts
        self._running_queue = running_queue
        self._nodes = nodes
        self._state = state

    def __str__(self):
        if self._running_datetime == 0:
           running_datetime = "notyet"
        else:
           running_datetime = self._running_datetime.strftime('%Y-%m-%d %H:%M:%S')
        if self._end_datetime == 0:
           end_datetime = "notyet"
        else:
           end_datetime = self._end_datetime.strftime('%Y-%m-%d %H:%M:%S')
        return "%s/%s (%d|%d) %s / %s / %s -> %d / %d [%s] %s" % \
               ( self._cluster_name,
                 self._id_job,
                 self._uid,
                 self._gid,
                 self._submission_datetime,
                 self._running_datetime,
                 self._end_datetime,
                 self._nb_hosts,
                 self._nb_procs,
                 self._nodes,
                 self._state )
    def save(self, db):
        req = """
            INSERT INTO jobs (
                            id_job,
                            sched_id,
                            uid,
                            gid,
                            clustername,
                            running_queue,
                            submission_datetime,
                            running_datetime,
                            end_datetime,
                            nb_nodes,
                            nb_cpus,
                            state)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
            RETURNING id; """
        datas = (
            self._id_job,
            self._sched_id,
            self._uid,
            self._gid,
            self._cluster_name,
            self._running_queue,
            self._submission_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            self._running_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            self._end_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            self._nb_hosts,
            self._nb_procs,
            self._state )
 
        dbcursor = db.get_cur()

        #print dbcursor.mogrify(req, datas)

        dbcursor.execute(req, datas)
        self._db_id = dbcursor.fetchone()[0]

        try:
	 if self._nodes is not None:
            for node in NodeSet(self._nodes.replace("x",",")):
                req = """
                    INSERT INTO job_nodes (
                                    job,
                                    node,
                                    cpu_id
                                    )
                    VALUES (%s, %s, %s); """
                datas = (
                    self._db_id,
                    node,
                    "unknown")
                db.get_cur().execute(req, datas)
        except NodeSetParseRangeError as e:
            logging.error("could not parse nodeset %s", self._nodes) 
        
    def update(self, db):
        req = """
            UPDATE jobs SET
                       id_job = %s,
                       uid = %s,
                       gid = %s,
                       clustername = %s,
                       running_queue = %s,
                       submission_datetime = %s,
                       running_datetime = %s,
                       end_datetime = %s,
                       nb_nodes = %s,
                       nb_cpus = %s,
                       state = %s
            WHERE sched_id = %s
            RETURNING id; """
        datas = (
            self._id_job,
            self._uid,
            self._gid,
            self._cluster_name,
            self._running_queue,
            self._submission_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            self._running_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            self._end_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            self._nb_hosts,
            self._nb_procs,
            self._state,
            self._sched_id )

        dbcursor = db.get_cur()
        dbcursor.execute(req, datas)
        self._db_id = dbcursor.fetchone()[0]

        # Add nodes to job_nodes if not defined already
        req = """ SELECT count(job) FROM job_nodes WHERE job = %s; """
        datas = ( self._db_id, )

        #print dbcursor.mogrify(req, datas)

        dbcursor.execute(req, datas)
        nodecount = dbcursor.fetchone()[0]

        if nodecount == 0 and self._nodes is not None:
            for node in NodeSet(self._nodes.replace("x",",")):
                if node != "None assigned":
                    req = """
                        INSERT INTO job_nodes (
                                        job,
                                        node,
                                        cpu_id
                                        )
                        VALUES (%s, %s, %s); """
                    datas = (
                        self._db_id,
                        node,
                        "unknown")
		    #print (datas)
                    db.get_cur().execute(req, datas)

		    
    """ accessors """

    def get_db_id(self):
        return self._db_id

    def get_uid(self):
        return self._uid

    def get_running_datetime(self):
        return self._running_datetime

    def set_running_datetime(self, running_datetime):
        self._running_datetime = running_datetime

    def get_end_datetime(self):
        return self._end_datetime

    def get_nb_procs(self):
        return self._nb_procs

    def get_state(self):
        return self._state

    def get_cluster_name(self):
        return self._cluster_name
