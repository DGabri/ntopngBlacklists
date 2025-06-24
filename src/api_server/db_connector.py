#!/usr/bin/python3
from contextlib import contextmanager
import mysql.connector
import time
import re

class ClickhouseConnector:
    def __init__(
        self,
        host,
        port,
        user,
        password,
    ):
        """
        Initialize the ClickhouseConnector with connection parameters.

        Args:
            host: The Clickhouse server host
            port: The Clickhouse MySQL protocol port
            user: The Clickhouse username
            password: The Clickhouse password (if any)
            database: The default database to connect to (optional)
        """
        self.connection_params = {"host": host, "port": port, "user": user}

        if password:
            self.connection_params["password"] = password

    @contextmanager
    def get_connection(self, database = None):
        """
        Context manager for handling database connections.

        Args:
            database: Optional database name to connect to

        Yields:
            A MySQL connector connection to Clickhouse
        """
        conn_params = self.connection_params.copy()
        if database:
            conn_params["database"] = database

        connection = None
        try:
            connection = mysql.connector.connect(**conn_params)
            yield connection
        except mysql.connector.Error as err:
            self.logging.error(f"Database connection error: {err}")
            raise
        finally:
            if connection and connection.is_connected():
                connection.close()

    def execute_query(
        self,
        query,
        database = None,
        params = None,
        fetch = False,
    ):
        
        results = None
        with self.get_connection(database) as connection:
            cursor = connection.cursor()
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                if fetch:
                    results = cursor.fetchall()
                else:
                    cursor.fetchall()
                    connection.commit()

            except mysql.connector.Error as err:
                self.logging.error(f"Query execution error: {err}")
                connection.rollback()
                raise
            finally:
                cursor.close()

        return results
    
    ##########################################################################################
    
    def query_data(self, query, database, params = None):
        return self.execute_query(query, database, params, fetch=True)

    def get_ip_events(self, ip):

        query = "SELECT timestamp, alert_id, info, reason FROM default.clean_alerts WHERE ip = %s ORDER BY timestamp DESC LIMIT 10"
        params = (ip,)

        result = self.query_data(query, database="default", params=params)
        return result