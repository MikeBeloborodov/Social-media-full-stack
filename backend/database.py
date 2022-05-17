import psycopg2
from psycopg2.extras import RealDictCursor
from models import *
import time
from fastapi import status, HTTPException
from passlib.context import CryptContext
from settings import settings
import oauth2
from datetime import datetime


now = datetime.now()
time_string = now.strftime("%H:%M:%S %Y-%m-%d")


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
            print(f'[{time_string}][+] DB CONNECTION WAS SUCCESSFUL')
            return [connection, cursor]
        except Exception as db_connection_error:
            print(f'[{time_string}][!] DB CONNECTION ERROR: {db_connection_error}')
            print(f"[{time_string}][!] TRYING TO RECONNECT AGAIN EVERY 5 SECONDS...")
            time.sleep(5)


def return_all_posts(connection, cursor, user_id) -> list:
    # execution check
    try:
        cursor.execute("""
                SELECT x.id, 
                    user_id,
                    title, 
                    content, 
                    x.created_at,
                    updated_at,
                    likes
                    FROM posts x JOIN users y ON x.user_id = y.id
                    ORDER BY created_at DESC""")
        posts = cursor.fetchall()
    except Exception as execution_error:
        print(f"[{time_string}][!] COULD NOT RETRIEVE DATA FROM DB: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve data from DB")

    # check if posts exist
    if not posts:
        print(f"[{time_string}][!] FAILED TO RETURN ALL POSTS FROM DB - NO POSTS AVAILABLE")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Posts database is empty")
    else:
        print(f"[{time_string}][+] SENDING ALL POSTS FROM DB")
        return posts


def return_post_by_id(connection, cursor, id, user_id) -> list:
    # execution check
    try:
        cursor.execute("""
                    SELECT id, user_id, title, content, created_at, updated_at, likes
                    FROM posts
                    WHERE id = %s""", (str(id),))
        post = cursor.fetchone()
    except Exception as execution_error:
        print(f"[{time_string}][!] COULD NOT RETRIEVE DATA FROM DB: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not retrieve data from DB")

    # check if post exists, else return it
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="This post does not exist")
    else:
        print(f"[{time_string}][+] SENDING POST WITH ID {id}")
        return post


def save_post_to_db(connection, cursor, new_post: NewPost, user_id) -> list:
    # get posting user from db
    try:
        cursor.execute("""
                    SELECT * FROM users WHERE id = %s""", (user_id, ))
        posting_user = cursor.fetchone()
    except Exception as execution_error:
        print(f"[{time_string}][!] COULD NOT CREATE NEW POST (FAILED TO RETRIEVE USER FROM DB): {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not write post to DB, user id retreival error.")

    if not posting_user:
            print(f"[{time_string}][!] TRIED TO CREATE A NEW POST, BUT POSTING USER WAS NOT FOUND, ID = {user_id}")
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User with this id does not exist")

    # execution check
    try:
        cursor.execute("""
                    INSERT INTO posts (title, content, user_id)
                    VALUES (%s, %s, %s)
                    RETURNING id, user_id, title, content, created_at, updated_at, likes""", (new_post.title, new_post.content, posting_user['id']))
        returning_post = cursor.fetchone()
        connection.commit()
        print(f"[{time_string}][+] CREATED NEW POST - {new_post.title}")
        return returning_post
    except Exception as execution_error:
        print(f"[{time_string}][!] COULD NOT CREATE NEW POST: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not write post to DB")


def save_updated_post_by_id(connection, cursor, id, updated_post: UpdatedPost, user_id) -> list:
    # check if post exists
    try:
        cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
        found_post = cursor.fetchone()
    except Exception as execution_error:
        print(f"[{time_string}][!] COULD NOT EXTRACT POST TO UPDATE, DB ERROR: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not find post to update in DB")

    if not found_post:
        print(f"[{time_string}][!] USER ID = {user_id} TRYING TO UPDATE A NON EXISTING POST")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="This post does not exist")

    # get updating user from db
    try:
        cursor.execute("""
                    SELECT * FROM users WHERE id = %s""", (user_id, ))
        updating_user = cursor.fetchone()
    except Exception as execution_error:
        print(f"[{time_string}][!] COULD NOT UPDATE POST (FAILED TO RETRIEVE USER FROM DB): {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update post in DB, user id retreival error.")

    if not updating_user:
            print(f"[{time_string}][!] TRIED TO UPDATE POST, BUT UPDATING USER WAS NOT FOUND, ID = {user_id}")
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User with this id does not exist")

    # validation check
    try:
        if found_post['user_id'] != updating_user['id']:
            print(f"[{time_string}][!] VALIDATION ERROR FROM USER ID {user_id} TO UPDATE POST")
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Wrong credentials")
    except Exception as evaluation_error:
        print(f"[{time_string}][!] COULD NOT UPDATE POST: {evaluation_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not compare user email with post owner")

    # execution check
    try:
        cursor.execute("""
                    UPDATE posts 
                    SET title = %s,
                        content = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    RETURNING id, user_id, title, content, created_at, updated_at, likes""", (updated_post.title, updated_post.content, str(id)))
        returning_post = cursor.fetchone()
        connection.commit()
        print(f"[{time_string}][+] UPDATED POST FROM USER ID {user_id} - {updated_post.title}")
        return returning_post
    except Exception as execution_error:
        print(f"[{time_string}][!] COULD NOT UPDATE POST: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update post in DB")


def delete_post_from_db(connection, cursor, id, user_id) -> list:
    # check if post exists
    try:
        cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
        found_post = cursor.fetchone()
    except Exception as execution_error:
        print(f"[{time_string}][!] COULD NOT FIND POST TO LIKE: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not find post to delete in DB")

    if not found_post:
        print(f"[{time_string}][!] USER ID {user_id} TRYING TO DELETE A NON EXISTING POST")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="This post does not exist")

    # get deleting user from db
    try:
        cursor.execute("""
                    SELECT * FROM users WHERE id = %s""", (user_id, ))
        deleting_user = cursor.fetchone()
    except Exception as execution_error:
        print(f"[{time_string}][!] COULD NOT DELETE POST (FAILED TO RETRIEVE USER FROM DB): {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete post in DB, user id retreival error.")

    if not deleting_user:
            print(f"[{time_string}][!] TRIED TO DELETE POST, BUT USER WAS NOT FOUND, ID = {user_id}")
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User with this id does not exist")

    # validation check
    try:
        if found_post['user_id'] != deleting_user['id']:
            print(f"[{time_string}][!] VALIDATION ERROR FROM USER ID {user_id} TO UPDATE POST")
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Wrong credentials")
    except Exception as evaluation_error:
        print(f"[{time_string}][!] COULD NOT UPDATE POST: {evaluation_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not compare user email with post owner")

    # execution check
    try:
        cursor.execute("""
                    DELETE FROM posts 
                    WHERE id = %s
                    RETURNING id, user_id, title, content, created_at, updated_at, likes""", (str(id),))
        deleted_post = cursor.fetchone()
        connection.commit()
        print(f"[{time_string}][+] DELETED POST FROM USER ID {user_id} - POST ID {id}")
        return deleted_post
    except Exception as execution_error:
        print(f"[{time_string}][!] COULD NOT DELETE POST: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete post from DB")


def save_post_like_to_db(connection, cursor, id: int, user_id) -> list:
    # check if post exists
    try:
        cursor.execute("""
                    SELECT * FROM posts WHERE id = %s""", (str(id),))
        found_post = cursor.fetchone()
    except Exception as execution_error:
        print(f"[{time_string}][!] COULD NOT FIND POST TO LIKE: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not find post to like in DB")

    if not found_post:
        print(f"[{time_string}][!] USER ID {user_id} TRYING TO LIKE A NON EXISTING POST")
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="This post does not exist")

    # get liking user from db
    try:
        cursor.execute("""
                    SELECT * FROM users WHERE id = %s""", (user_id, ))
        liking_user = cursor.fetchone()
    except Exception as execution_error:
        print(f"[{time_string}][!] COULD NOT DELETE POST (FAILED TO RETRIEVE USER FROM DB): {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete post in DB, user id retreival error.")

    if not liking_user:
            print(f"[{time_string}][!] TRIED TO DELETE POST, BUT USER WAS NOT FOUND, ID = {user_id}")
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User with this id does not exist")

    # validation check
    try:
        cursor.execute("""
                    Select x.id, post_id, liked_user_id
                    FROM posts x 
                    JOIN likes y 
                    ON x.id = y.post_id
                    WHERE 		liked_user_id = %s 
                                and post_id = %s""", (liking_user['id'], str(id)))
        found_post = cursor.fetchone()
    except Exception as execution_error:
        print(f"[{time_string}][!] COULD NOT LIKE POST: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not find post in DB")

    # check if already liked
    if found_post:
        print(f"[{time_string}][!] USER ID {user_id} TRYING TO LIKE A POST AGAIN")
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User already liked this post")

    # execution check
    try:
        cursor.execute("""
                    UPDATE posts 
                    SET likes = likes + 1
                    WHERE id = %s
                    RETURNING id, user_id, title, content, created_at, updated_at, likes""", (str(id),))
        returning_post = cursor.fetchone()
        connection.commit()
        cursor.execute("""
                    INSERT INTO likes (post_id, liked_user_id)
                    VALUES (%s, %s)""", (str(id), liking_user['id']))
        connection.commit()
        print(f"[{time_string}][+] POST ID {id} WAS LIKED BY USER ID {user_id}")
        return returning_post
    except Exception as execution_error:
        print(f"[{time_string}][!] COULD NOT LIKE POST: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update user like in DB")


def save_user_to_db(connection, cursor, new_user: CreateUser) -> list:
    # hash password
    try:
        pwd_context = CryptContext(schemes=['bcrypt'])
        new_user.password = pwd_context.hash(new_user.password)
    except Exception as hash_error:
        print(f"[{time_string}][!] UNABLE TO HASH NEW USER PASSWORD - {new_user.email}")
        print(f"[{time_string}]Error: {hash_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create user, internal error")

    # check if user already exists
    try:
        cursor.execute("""
                    SELECT * FROM users
                    WHERE email = %s""", (new_user.email, ))
        accounts_found = cursor.fetchall()
    except Exception as user_validation_error:
        print(f"[{time_string}][!] ERROR DURING USER SEARCH IN DB - {new_user.email}")
        print(f"[{time_string}]Error: {user_validation_error}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database internal error during user search")

    if accounts_found:
        print(f"[{time_string}][!] ERROR, USER {new_user.email} ALREADY EXISTS!")
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Error. This user already exists.")

    # execution check
    try:
        cursor.execute("""
                    INSERT INTO users (email, password)
                    VALUES (%s, %s)
                    RETURNING id, email, created_at""", (new_user.email, new_user.password))
        user = cursor.fetchall()
        connection.commit()
        print(f"[{time_string}][+] CREATED NEW USER - {new_user.email}")
        return user
    except Exception as execution_error:
        print(f"[{time_string}][!] COULD NOT CREATE NEW USER: {execution_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not write user to DB")


def check_user_credentials(connection, cursor, user_credentials: LoginUser) -> dict:
    # try accessing DB
    try:
        cursor.execute("""SELECT * FROM users WHERE email = %s""", (user_credentials.username, ))
        found_user = cursor.fetchone()
    except Exception as hash_error:
        print(f"[{time_string}][!] UNABLE TO RETRIEVE USER DURING LOGIN - {user_credentials.username}")
        print(f"[{time_string}]Error: {hash_error}")
        connection.rollback()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not login user, internal error")

    # first we check if user email exists
    if not found_user:
        print(f"[{time_string}][!] VALIDATION ERROR FROM USER {user_credentials.username} TO LOGIN, EMAIL IS WRONG")
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Wrong credentials")

    # then we check if stored hashed password and given password are the same
    pwd_context = CryptContext(schemes=['bcrypt'])
    if not pwd_context.verify(user_credentials.password, found_user['password']):
        print(f"[{time_string}][!] USER {user_credentials.username} TRYING TO LOGIN WITH A WRONG PASSWORD")
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Wrong credentials")

    # if everything is okay we send data back
    print(f"[{time_string}][+] USER {user_credentials.username} IS NOW LOGGED IN")
    access_token = oauth2.create_access_token(data = {"user_id" : found_user['id']})

    return {"access_token": access_token, "token_type": "bearer", "date_time" : time_string}
