import psycopg2
from pprint import pprint


def create_db(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Clients(
        id SERIAL PRIMARY KEY,
        name VARCHAR(20),
        lastname VARCHAR(30),
        email VARCHAR(254)
        );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Phone(
        number VARCHAR(11) PRIMARY KEY,
        client_id INTEGER REFERENCES clients(id)
        );
    """)
    return


def delete_db(cur):
    cur.execute("""
        DROP TABLE Clients, Phone CASCADE;
        """)


def add_phone(cur, client_id, tel):
    cur.execute("""
        INSERT INTO phone(number, client_id)
        VALUES (%s, %s)
        """, (tel, client_id))
    return client_id


def add_client(cur, name=None, lastname=None, email=None, tel=None):
    cur.execute("""
        INSERT INTO clients(name, lastname, email)
        VALUES (%s, %s, %s)
        """, (name, lastname, email))
    cur.execute("""
        SELECT id from clients
        ORDER BY id DESC
        LIMIT 1
        """)
    id = cur.fetchone()[0]
    if tel is None:
        return id
    else:
        add_phone(cur, id, tel)
        return id


def update_client(cur, id, name=None, surname=None, email=None):
    cur.execute("""
        SELECT * from clients
        WHERE id = %s
        """, (id, ))
    info = cur.fetchone()
    if name is None:
        name = info[1]
    if surname is None:
        surname = info[2]
    if email is None:
        email = info[3]
    cur.execute("""
        UPDATE clients
        SET name = %s, lastname = %s, email =%s 
        where id = %s
        """, (name, surname, email, id))
    return id


def delete_phone(cur, number):
    cur.execute("""
        DELETE FROM phone
        WHERE number = %s
        """, (number, ))
    return number


def delete_client(cur, id):
    cur.execute("""
        DELETE FROM phone
        WHERE client_id = %s
        """, (id, ))
    cur.execute("""
        DELETE FROM clients 
        WHERE id = %s
       """, (id,))
    return id


def find_client(cur, name=None, surname=None, email=None, tel=None):
    if name is None:
        name = '%'
    else:
        name = '%' + name + '%'
    if surname is None:
        surname = '%'
    else:
        surname = '%' + surname + '%'
    if email is None:
        email = '%'
    else:
        email = '%' + email + '%'
    if tel is None:
        cur.execute("""
            SELECT c.id, c.name, c.lastname, c.email, p.number FROM clients c
            LEFT JOIN phone p ON c.id = p.client_id
            WHERE c.name LIKE %s AND c.lastname LIKE %s
            AND c.email LIKE %s
            """, (name, surname, email))
    else:
        cur.execute("""
            SELECT c.id, c.name, c.lastname, c.email, p.number FROM clients c
            LEFT JOIN phone p ON c.id = p.client_id
            WHERE c.name LIKE %s AND c.lastname LIKE %s
            AND c.email LIKE %s AND p.number like %s
            """, (name, surname, email, tel))
    return cur.fetchall()



with psycopg2.connect(database="client_db", user="postgres",
                      password="905995ike") as conn:
    with conn.cursor() as curs:

        delete_db(curs) # Удаление таблиц перед запуском

        create_db(curs)# Cоздание таблиц

        # Добавляем клиентов
        add_client(curs, "Александр", "Иванов", "ai@mail.ru")
        add_client(curs, "Михайл", "Петров", "tr@mail.ru", 79059059999)
        add_client(curs, "Дмитрий", "Петров", "dp@mail.ru", 79139130002)
        add_client(curs, "Виктор", "Сергеев", "vs@mail.ru", 79139020015)
        add_client(curs, "Сава", "Сидоров", "ss@mail.ru", 79059039532)
        add_client(curs, "Алиса", "Иванова", "ai@mail.ru", 79059959954)
        add_client(curs, "Артем", "Дуров", "ad@mail.ru")

        print("Данные в таблицах")
        curs.execute("""
            SELECT c.id, c.name, c.lastname, c.email, p.number FROM clients c
            LEFT JOIN phone p ON c.id = p.client_id
            ORDER by c.id
            """)
        pprint(curs.fetchall())

        # Добавляем клиенту номер телефона
        add_phone(curs, 2, 79555555555)
        add_phone(curs, 1, 79012222222)

        curs.execute("""
            SELECT c.id, c.name, c.lastname, c.email, p.number FROM clients c
            LEFT JOIN phone p ON c.id = p.client_id
            ORDER by c.id
            """)
        pprint(curs.fetchall())
        # Изменим данные клиента
        update_client(curs, 4, "Алеша", None, 'aa@mail.ru')

        # Удаляем клиенту номер телефона
        delete_phone(curs, '79012222222')
        curs.execute("""
            SELECT c.id, c.name, c.lastname, c.email, p.number FROM clients c
            LEFT JOIN phone p ON c.id = p.client_id
            ORDER by c.id
            """)
        pprint(curs.fetchall())

        # Удалим клиента номер 2
        delete_client(curs, 2)
        curs.execute("""
                        SELECT c.id, c.name, c.lastname, c.email, p.number FROM clients c
                        LEFT JOIN phone p ON c.id = p.client_id
                        ORDER by c.id
                        """)
        pprint(curs.fetchall())

        # Найдём клиента
        pprint(find_client(curs, 'Артем'))

        pprint(find_client(curs, None, None, 'dp@mail.ru'))

        pprint(find_client(curs, 'Сава', 'Сидоров', 'ss@mail.ru'))

        pprint(find_client(curs, 'Дмитрий', 'Петров', 'dp@mail.ru', '79139130002'))

        pprint(find_client(curs, None, None, None, '79059959954'))