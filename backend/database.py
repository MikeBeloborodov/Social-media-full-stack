import psycopg2
from psycopg2.extras import RealDictCursor
from models import *
import time
from fastapi import status, HTTPException
from passlib.context import CryptContext
from settings import *


def postgres_database_connection() -> list:
    while True:
        try:
            connection = psycopg2.connect(
                host=settings.database_hostname,
                database=settings.database_name,
                password=settings.database_password,
                user=settings.database_username,
                cursor_factory=RealDictCursor
            )
            cursor = connection.cursor()
            print('[+] DB CONNECTION WAS SUCCESSFUL')
            return [connection, cursor]
        except Exception as db_connection_error:
            print(f'[!] DB CONNECTION ERROR: {db_connection_error}')
            print(f"[!] TRYING TO RECONNECT AGAIN EVERY 5 SECONDS...")
            time.sleep(5)


def return_all_posts(connection, cursor) -> list:
    # execution check
    try:
        cursor.execute("""
                SELECT x.id as post_id, 
                    title, 
                    content, 
                    email,
                    x.created_at,
                    updated_at,
                    likes
                    FROM posts x JOIN users y ON x.owner_email = y.email
                    ORDER BY created_at DESC""")
        posts = cursor.fetchall()
    except Exception as execution_error:
        print(f"[!] COULD NOT RETRIEVE DATA FROM DB: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't retrieve data from DB")

    # check if posts exist
    if not posts:
        print("[!] FAILED TO RETURN ALL POSTS FROM DB - NO POSTS AVAILABLE")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Posts database is empty")
    else:
        print("[+] SENDING ALL POSTS FROM DB")
        return posts


def return_post_by_id(connection, cursor, id) -> list:
    # execution check
    try:
        cursor.execute("""
                    SELECT id, title, content, owner_email, created_at, updated_at, likes
                    FROM posts
                    WHERE id = %s""", (str(id),))
        post = cursor.fetchone()
    except Exception as execution_error:
        print(f"[!] COULD NOT RETRIEVE DATA FROM DB: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't retrieve data from DB")

    # check if post exists, else return it
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="This post doesn't exist")
    else:
        print(f"[+] SENDING POST WITH ID {id}")
        return post


def save_post_to_db(connection, cursor, new_post: Post) -> list:
    # execution check
    try:
        cursor.execute("""
                    INSERT INTO posts (title, content, owner_email)
                    VALUES (%s, %s, %s)
                    RETURNING id, title, content, owner_email, created_at, updated_at, likes""", (new_post.title, new_post.content, new_post.owner_email))
        returning_post = cursor.fetchone()
        connection.commit()
        print(f"[+] CREATED NEW POST - {new_post.title}")
        return returning_post
    except Exception as execution_error:
        print(f"[!] COULD NOT CREATE NEW POST: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't write post to DB")


def save_updated_post_by_id(connection, cursor, id, updated_post: Post, user: User) -> list:
    # check if post exists
    try:
        cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
        found_post = cursor.fetchone()
    except Exception as execution_error:
        print(f"[!] COULD NOT FIND POST TO LIKE: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't find post to update in DB")

    if not found_post:
        print(f"[!] USER {user.email} TRYING TO UPDATE A NON EXISTING POST")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="This post doesn't exist")

    # validation check
    try:
        cursor.execute("""
                    SELECT * 
                    FROM posts
                    WHERE owner_email = %s and id = %s""", (user.email, str(id)))
        found_post = cursor.fetchone()
    except Exception as execution_error:
        print(f"[!] COULD NOT UPDATE POST: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't retrieve post data from DB")

    # send 403 if validation fails
    if not found_post:
        print(f"[!] VALIDATION ERROR FROM USER {user.email} TO UPDATE POST")
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Wrong credentials")

    # execution check
    try:
        cursor.execute("""
                    UPDATE posts 
                    SET title = %s,
                        content = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    RETURNING id, title, content, owner_email, created_at, updated_at, likes""", (updated_post.title, updated_post.content, str(id)))
        returning_post = cursor.fetchone()
        connection.commit()
        print(f"[+] UPDATED POST FROM USER {user.email} - {updated_post.title}")
        return returning_post
    except Exception as execution_error:
        print(f"[!] COULD NOT UPDATE POST: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't update post in DB")


def delete_post_from_db(connection, cursor, id, user: User) -> list:
    # check if post exists
    try:
        cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
        found_post = cursor.fetchone()
    except Exception as execution_error:
        print(f"[!] COULD NOT FIND POST TO LIKE: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't find post to delete in DB")

    if not found_post:
        print(f"[!] USER {user.email} TRYING TO DELETE A NON EXISTING POST")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="This post doesn't exist")

    # validation check
    try:
        cursor.execute("""
                    SELECT * 
                    FROM posts
                    WHERE owner_email = %s and id = %s""", (user.email, str(id)))
        found_post = cursor.fetchone()
    except Exception as execution_error:
        print(f"[!] COULD NOT DELETE POST: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't retrieve post to delete from DB")

    if not found_post:
        print(f"[!] VALIDATION ERROR FROM USER {user.email} TO DELETE POST")
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Wrong credentials")

    # execution check
    try:
        cursor.execute("""
                    DELETE FROM posts 
                    WHERE id = %s
                    RETURNING id, title, content, owner_email, created_at, updated_at, likes""", (str(id),))
        deleted_post = cursor.fetchone()
        connection.commit()
        print(f"[+] DELETED POST FROM USER {user.email} - POST ID {id}")
        return deleted_post
    except Exception as execution_error:
        print(f"[!] COULD NOT DELETE POST: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't delete post from DB")


def save_user_to_db(connection, cursor, new_user: CreateUser) -> list:
    # hash password
    try:
        pwd_context = CryptContext(schemes=['bcrypt'])
        new_user.password = pwd_context.hash(new_user.password)
    except Exception as hash_error:
        print(f"[!] UNABLE TO HASH NEW USER PASSWORD - {new_user.email}")
        print(f"Error: {hash_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't create user, internal error")

    # check if user already exists
    try:
        cursor.execute("""
                    SELECT * FROM users
                    WHERE email = %s""", (new_user.email, ))
        accounts_found = cursor.fetchall()
    except Exception as user_validation_error:
        print(f"[!] ERROR DURING USER SEARCH IN DB - {new_user.email}")
        print(f"Error: {user_validation_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database internal error during user search")

    if accounts_found:
        print(f"[!] ERROR, USER {new_user.email} ALREADY EXISTS!")
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Error. This user already exists.")

    # execution check
    try:
        cursor.execute("""
                    INSERT INTO users (email, password)
                    VALUES (%s, %s)
                    RETURNING id, email, created_at""", (new_user.email, new_user.password))
        user = cursor.fetchall()
        connection.commit()
        print(f"[+] CREATED NEW USER - {new_user.email}")
        return user
    except Exception as execution_error:
        print(f"[!] COULD NOT CREATE NEW USER: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't write user to DB")


def check_user_credentials(connection, cursor, user_credentials: LoginUser) -> list:
    # try accessing DB
    try:
        cursor.execute("""SELECT * FROM users WHERE email = %s""", (user_credentials.email, ))
        found_user = cursor.fetchone()
    except Exception as hash_error:
        print(f"[!] UNABLE TO RETRIEVE USER DURING LOGIN - {user_credentials.email}")
        print(f"Error: {hash_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't login user, internal error")

    # first we check if user email exists
    if not found_user:
        print(f"[!] VALIDATION ERROR FROM USER {user_credentials.email} TO LOGIN, EMAIL IS WRONG")
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Wrong credentials")

    # then we check if stored hashed password and given password are the same
    hashed_password_in_db = found_user['password']
    pwd_context = CryptContext(schemes=['bcrypt'])
    if not pwd_context.verify(user_credentials.password, hashed_password_in_db):
        print(f"[!] USER {user_credentials.email} TRYING TO LOGIN WITH A WRONG PASSWORD")
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Wrong credentials")

    # if everything is okay we send data back
    print(f"[+] USER {user_credentials.email} IS NOW LOGGED IN")
    return [{"email": found_user['email'],
             "id": found_user['id'],
             "registration_date": found_user['created_at']}]


def save_user_like(connection, cursor, id: int, user_email: str) -> list:
    print(id)
    # check if post exists
    try:
        cursor.execute("""
                    SELECT * FROM posts WHERE id = %s""", (str(id),))
        found_post = cursor.fetchone()
    except Exception as execution_error:
        print(f"[!] COULD NOT FIND POST TO LIKE: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't find post to like in DB")

    if not found_post:
        print(f"[!] USER {user_email} TRYING TO LIKE A NON EXISTING POST")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="This post doesn't exist")

    # validation check
    try:
        cursor.execute("""
                    Select x.id, post_id, liked_user_email 
                    FROM posts x 
                    JOIN likes y 
                    ON x.id = y.post_id
                    WHERE 		liked_user_email = %s 
                                and post_id = %s""", (user_email, str(id)))
        found_post = cursor.fetchone()
    except Exception as execution_error:
        print(f"[!] COULD NOT LIKE POST: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't find post in DB")

    # check if already liked
    if found_post:
        print(f"[!] USER {user_email} TRYING TO LIKE A POST AGAIN")
        raise HTTPException(status.HTTP_409_CONFLICT, detail="User already liked this post")

    # execution check
    try:
        cursor.execute("""
                    UPDATE posts 
                    SET likes = likes + 1
                    WHERE id = %s
                    RETURNING id, title, content, owner_email, created_at, updated_at, likes""", (str(id),))
        returning_post = cursor.fetchone()
        connection.commit()
        cursor.execute("""
                    INSERT INTO likes (post_id, liked_user_email)
                    VALUES (%s, %s)""", (str(id), user_email))
        connection.commit()
        print(f"[+] POST ID {id} WAS LIKED BY USER {user_email}")
        return returning_post
    except Exception as execution_error:
        print(f"[!] COULD NOT LIKE POST: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't update user like in DB")
