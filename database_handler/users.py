import bcrypt
from initialize_database import Database
from mysql.connector import Error


def hash_password(password):
    byte_pwd = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(byte_pwd, salt)


class Users:
    def __init__(self):
        self.connection = Database().connection

    def add_user(self, username, password, email):
        insert_users_query = """
                INSERT INTO users 
                (username, password, email) 
                VALUES (%s, %s, %s)
                """

        hashed_pwd = hash_password(password)
        users_record = (username, hashed_pwd, email)

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_users_query, users_record)
                self.connection.commit()
        except Error as e:
            print(e)

    def select_user(self, user_id, username, email):
        select_user_query = """
                        SELECT * FROM users
                        WHERE id = %s
                        OR username = %s
                        OR email = %s
                        """

        user_args = (user_id, username, email)

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(select_user_query, user_args)
                output = cursor.fetchone()
                if output:
                    return {'id': output[0], 'username': output[1], 'email': output[2], 'password': output[3]}
                else:
                    raise Error('No user found')
        except Error as e:
            print(e)
