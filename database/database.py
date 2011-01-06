#
# Author: Edward Benson <eob@csail.mit.edu>
#

import sqlite3
import os

class Database:
    
    def __init__(self, dbfile):
        self.dbfile = dbfile
        self.db = None
        self.connect()
        self.load_schema()
        
    def connect(self):
        if os.path.exists(self.dbfile):
            self.db = sqlite3.connect(self.dbfile)
        else:
            self.db = sqlite3.connect(self.dbfile)
            self.db.commit()
    
    def commit(self):
        self.db.commit()

    def close(self):
        self.db.close()
    
    def bool_query(self, query, params=None):
        try:
            cur = self.query(query, params)
            has_result = cur.fetchone() != None
            cur.close()
            return has_result
        except Exception as ex:
            print "Exception in database::bool_query"
            print ex
            self.connect()
            return False
            
    def ensure_connection(self):
        pass
        
    def query(self, query, params=None):
        try:
            self.ensure_connection()
            cur = self.db.cursor()
            if type(query).__name__ == 'str':
                if params:
                    if type(params).__name__ == 'list':
                        cur.execute(query, params)
                    else:
                        cur.execute(query, [str(params)])
                else:
                    cur.execute(query)
            elif type(query).__name__ == 'list':
                fields = []
                values = []
                questions = []
                for k,v in params.items():
                    fields.append("%s = ?" % k)

                params = (', '.join(query[1:]), query[0], " AND ".join(fields))
                sql = "SELECT %s FROM %s WHERE %s;" % params
                cur.execute(sql, values)
            return cur
        except Exception as ex:
            print "Exception in database::query"
            print ex
            self.connect()
            return None
        
    def safe_insert(self, table, dic):
        if not self.bool_query([table, '*'], dic):
            self.insert(table, dic)

    def insert(self, table, dic):
        try:
            self.ensure_connection()
            fields = []
            values = []
            for k,v in dic.items():
                fields.append(k)
                values.append(v)
            questions = ['%s' for v in values]
            sql = "INSERT INTO %s (%s) VALUES (%s)" % (table, ', '.join(fields), ', '.join(questions))
            cur = self.db.cursor()
            cur.execute(sql, values)
            cur.close()
        except Exception as ex:
            print "Exception in database::insert"
            print ex
            self.connect()
            
    def last_inserted_id(self):
        try:
            self.ensure_connection()
            cur = self.db.cursor()
            cur.execute("SELECT last_insert_rowid() as last;")  
            rowid = cur.fetchone()[0]
            cur.close() 
            return rowid
        except Exception as ex:
            print "Exception in database::last_inserted_id"
            print ex
            self.connect()
            return None
            
    def load_schema(self):
        cur = self.db.cursor()
        cur.execute(self.events_schema())
        cur.execute(self.queries_schema())
        cur.execute(self.tasks_schema())
        cur.close()
        self.db.commit()
        
    def events_schema(self):
        return """
        CREATE TABLE IF NOT EXISTS events (
            eid integer PRIMARY KEY AUTOINCREMENT,
            source        varchar(255),
            title         varchar(255),
            venue         varchar(255),
            address1      varchar(255),
            address2      varchar(255),
            description   text,
            url           varchar(255),
            event_time    datetime,
            ticket_price  float default 0
        );
        """
        
    def queries_schema(self):
        return """
        CREATE TABLE IF NOT EXISTS queries (
            qid integer PRIMARY KEY AUTOINCREMENT,
            eid           integer default 0,
            query         varchar(255),
            start_date    datetime,
            stop_date     datetime
        );
        """

    def tasks_schema(self):
        return """
        CREATE TABLE IF NOT EXISTS tasks (
            tid integer PRIMARY KEY AUTOINCREMENT,
            task          varchar(255),
            after         datetime,
            reschedule    integer default 0,
            complete      integer default 0,
            completed_on  datetime,
            delta         integer
        );
        """