import os
from mysql.connector import connect


class Database:
    def __init__(self):
        self._connection = None
        self.initialize_connection()

    def initialize_connection(self):
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASS')
        db_host = 'mysql.agh.edu.pl'
        self._connection = connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database='ciesiel3'
        )

    def get_connection(self):
        return self._connection

    def close_connection(self):
        self._connection.close()

    def create_users_table(self):
        create_users_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            id INT(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL
        )
        """

        with self._connection.cursor() as cursor:
            cursor.execute(create_users_table_query)
            self._connection.commit()

    def create_toys_table(self):
        create_toys_table_query = """
        CREATE TABLE IF NOT EXISTS toys (
            id INT(11) NOT NULL PRIMARY KEY,
            name VARCHAR(255),
            min_price FLOAT(7,2),
            manufacturer VARCHAR(255),
            num_of_shops SMALLINT,
            img_url VARCHAR(255)
        )
        """

        with self._connection.cursor() as cursor:
            cursor.execute(create_toys_table_query)
            self._connection.commit()

    def create_offers_table(self):
        create_offers_table_query = """
        CREATE TABLE IF NOT EXISTS offers (
            id INT(11) NOT NULL PRIMARY KEY,
            url VARCHAR(1024) NOT NULL UNIQUE,
            toy_id INT(11) NOT NULL,
            shop_id INT(11),
            shop_name VARCHAR(255),
            price FLOAT(7,2),
            FOREIGN KEY(toy_id) REFERENCES toys(id)
        )
        """

        with self._connection.cursor() as cursor:
            cursor.execute(create_offers_table_query)
            self._connection.commit()

    def create_search_history_table(self):
        create_search_history_table_query = """
            CREATE TABLE IF NOT EXISTS search_history (
                user_id INT(11),
                user_input VARCHAR(255),
                datetime DATETIME,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """

        with self._connection.cursor() as cursor:
            cursor.execute(create_search_history_table_query)
            self._connection.commit()

    def create_shopping_list_table(self):
        create_shopping_list_table_query = """
            CREATE TABLE IF NOT EXISTS shopping_list (
                user_id INT(11),
                offer_id INT(11),
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(offer_id) REFERENCES offers(id)
            )
            """

        with self._connection.cursor() as cursor:
            cursor.execute(create_shopping_list_table_query)
            self._connection.commit()

    def create_tables(self):
        self.create_users_table()
        self.create_toys_table()
        self.create_offers_table()
        self.create_search_history_table()
        self.create_shopping_list_table()
