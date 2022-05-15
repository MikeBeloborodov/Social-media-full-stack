import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from models import *
import time

def postgre_database_connection() -> list:
	while True:
		try:
			connection = psycopg2.connect(
											host='localhost',
											database='social-media-app-api',
											user='postgres',
											cursor_factory=RealDictCursor
											)
			cursor = connection.cursor()
			print('[+] DB CONNECTION WAS SUCCESSFULL')
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
							name as sender_name,
							email,
							date_created,
							date_updated,
							likes
							FROM posts x JOIN users y ON x.owner_email = y.email
							ORDER BY date_created
	""")
		posts = cursor.fetchall()
		print("[+] SENDING ALL POSTS FROM DB")
		return posts
	except Exception as execution_error:
		print(f"[!] COULD NOT RETRIEVE DATA FROM DB: {execution_error}")
		return []

def return_post_by_id(connection, cursor, id) -> list:
	# execution check
	try:
		cursor.execute(f"""
						SELECT *
						FROM posts
						WHERE id = {id}
		""")
		post = cursor.fetchall()
		if not post:
			return [{"Message" : f"There is not post with id {id}"}]
		print(f"[+] SENDING POST WITH ID {id}")
		return post
	except Exception as execution_error:
		print(f"[!] COULD NOT RETRIEVE DATA FROM DB: {execution_error}")
		return [{"Message" : "Something went wrong... DB execution error"}]

def save_user_to_db(connection, cursor, new_user: User) -> list:
	# execution check	
	try:
		cursor.execute(f"""
						INSERT INTO users (name, email, password)
						VALUES ('{new_user.name}', '{new_user.email}', {new_user.password})
						RETURNING name, email
		""")
		user = cursor.fetchall()
		connection.commit()
		print(f"[+] CREATED NEW USER - {new_user.name} {new_user.email}")
		return user
	except Exception as execution_error:
		print(f"[!] COULD NOT CREATE NEW USER: {execution_error}")
		return [{"Message" : "Something went wrong... DB execution error"}]

def save_post_to_db(connection, cursor, new_post: Post) -> list:
	# execution check	
	try:
		cursor.execute(f"""
						INSERT INTO posts (title, content, owner_email)
						VALUES ('{new_post.title}', '{new_post.content}', '{new_post.owner_email}')
						RETURNING title, content
		""")
		returning_post = cursor.fetchall()
		connection.commit()
		print(f"[+] CREATED NEW POST - {new_post.title}")
		return returning_post
	except Exception as execution_error:
		print(f"[!] COULD NOT CREATE NEW POST: {execution_error}")
		return [{"Message" : "Something went wrong... DB execution error"}]

def update_post_in_db(connection, cursor, id, updated_post: Post, user: User) -> list:
	# validation check
	try:
		cursor.execute(f"""
						SELECT * 
						FROM posts
						WHERE owner_email = '{user.email}' and id = {id}
		""")
		found_posts = cursor.fetchall()
		if not found_posts:
			print(f"[!] VALIDATION ERROR FROM USER {user.email} TO UPDATE POST")
			return [{"Message" : "Validation error, this post doesn't belong to user"}]
	except Exception as execution_error:
		print(f"[!] COULD NOT UPDATE POST: {execution_error}")
		return [{"Message" : "Something went wrong... DB execution error"}]
	
	# execution check	
	try:
		cursor.execute(f"""
						UPDATE posts 
						SET title = '{updated_post.title}',
							content = '{updated_post.content}',
							date_updated = NOW()
						WHERE id = {id}
						RETURNING title, content
		""")
		returning_post = cursor.fetchall()
		connection.commit()
		print(f"[+] UPDATED POST FROM USER {updated_post.owner_email} - {updated_post.title}")
		return returning_post
	except Exception as execution_error:
		print(f"[!] COULD NOT UPDATE POST: {execution_error}")
		return [{"Message" : "Something went wrong... DB execution error"}]

def delete_post_from_db(connection, cursor, id, user: User):
	# validation check
	try:
		cursor.execute(f"""
						SELECT * 
						FROM posts
						WHERE owner_email = '{user.email}' and id = {id}
		""")
		found_posts = cursor.fetchall()
		if not found_posts:
			print(f"[!] VALIDATION ERROR FROM USER {user.email} TO DELETE POST")
			return [{"Message" : "Validation error, this post doesn't belong to user"}]
	except Exception as execution_error:
		print(f"[!] COULD NOT DELETE POST: {execution_error}")
		return [{"Message" : "Something went wrong... DB execution error"}]
	
	# execution check	
	try:
		cursor.execute(f"""
						DELETE FROM posts 
						WHERE id = {id}
						RETURNING title, content
		""")
		deleted_post = cursor.fetchall()
		connection.commit()
		print(f"[+] DELETED POST FROM USER {user.email} - POST ID {id}")
		return deleted_post
	except Exception as execution_error:
		print(f"[!] COULD NOT UPDATE POST: {execution_error}")
		return [{"Message" : "Something went wrong... DB execution error"}]

def check_user_credentials(connection, cursor, user_credentials: Login_user):
	# validation check
	try:
		cursor.execute(f"""
						SELECT * 
						FROM users
						WHERE email = '{user_credentials.email}' and
						password = '{user_credentials.password}'
		""")
		found_users = cursor.fetchall()
		if not found_users:
			print(f"[!] VALIDATION ERROR FROM USER {user_credentials.email} TO LOGIN")
			return [{"Message" : "Validation error, wrong email or password"}]
	except Exception as execution_error:
		print(f"[!] COULD NOT LOGIN USER: {execution_error}")
		return [{"Message" : "Something went wrong... DB execution error"}]
	
	return [{"email" : found_users[0]['email'], 
			"name" : found_users[0]['name'],
			"id" : found_users[0]['id'],
			"registration_date" : found_users[0]['data_registred']}]