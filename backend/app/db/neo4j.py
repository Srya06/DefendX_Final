from neo4j import GraphDatabase
from app.core.config import settings

class Neo4jConnection:
    def __init__(self):
        self._driver = None
        if settings.NEO4J_URI:
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
            )

    def close(self):
        if self._driver is not None:
            self._driver.close()

    def get_session(self):
        if self._driver is not None:
            return self._driver.session(database="defendx")
        return None

    def execute_query(self, query, parameters=None):
        if self._driver is None:
            return None
        with self._driver.session(database="defendx") as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

neo4j_conn = Neo4jConnection()

def get_neo4j():
    return neo4j_conn
