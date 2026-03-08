import psycopg2

class MessengerGogaDatabase():
    def __init__(self, db, user, password, host, port):
        connection = psycopg2.connect(database=db, user=user, password=password, host=host, port=port)

        cursor = connection.cursor()

        self.cursor = cursor
        self.connection = connection
    def select_all_schemas(self):
        self.cursor.execute("SELECT nspname FROM pg_namespace;")
        for schema in self.cursor.fetchall():
            print(schema[0])
    def query(self, query):
        self.cursor.execute(query)
        try:
            records = self.cursor.fetchall()
            self.connection.commit()
            return records
        except:
            self.connection.commit()
            return None
    def close(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()