import requests
import os
from getch import getch

POSTS = "http://127.0.0.1:8000/posts"
REGISTER = "http://127.0.0.1:8000/register"
LOGIN = "http://127.0.0.1:8000/login"

def clear_console():
    os.system('clear')

def press_any_key():
    print("Press any key...")
    getch()

def logged_in_user_screen(user: dict):
    clear_console()
    print(f"Name: {user['name']}")
    print(f"Email: {user['email']}")
    print("1 - View all posts")
    print("2 - Logout")
    print("3 - Register new user")
    print("4 - Create a post")
    print("5 - Like a post")
    print("6 - Exit")

def before_login_screen():
    clear_console()
    print("1 - View all posts")
    print("2 - Login")
    print("3 - Register new user")
    print("4 - Exit")

def render_main_menu(user: dict):
    if not user:
        before_login_screen()
    else:
        logged_in_user_screen(user)

def render_all_posts():
    posts = requests.get(POSTS).json()
    clear_console()
    for post in posts:
        print("+----------------+")
        print(f"Id - {post['post_id']}")
        print(f"Sender name - {post['sender_name']} ({post['email']})")
        print(f"Title - {post['title']}")
        print(f"Text - {post['content']}")
        print(f"Likes - {post['likes']}")
        print(f"Created - {post['date_created']}")
        print("+----------------+")

def register_new_user(name: str, email: str, password: str):
    user_registry = {"name" : name, "email" : email, "password" : password}
    answer = requests.post(REGISTER, json=user_registry).json()
    try:
        if answer[0]['name'] == name:
            return True
        else:
            return answer
    except Exception as error:
        print(f"Error: {error}")
        prtin("Try again.")
        press_any_key()
        return

def user_choice_view_all_posts():
    render_all_posts()
    press_any_key()

def user_choice_register_new_user():
    clear_console()
    name = input("Enter your name: ")
    password = input("Enter your password: ")
    email = input("Enter your email: ")
    answer = register_new_user(name, email, password)
    if answer == True:
        print("Congratulations! You have been registred.")
        print("Now you can log in with your email and password.")
        print(f"Email -  {email}")
        print(f"Password - {password}")
        press_any_key()
    else:
        print("Something went wrong...")
        print(f"You can read the error code: {answer}")
        press_any_key()

def validate_user_login(user: dict, email: str, password: str):
    user_credentials = {"email" : email, "password" : password}
    answer = requests.post(LOGIN, json=user_credentials)
    try:
        if answer.json()[0]['email'] == email:
            user.update(answer.json()[0])
            return True
        else:
            return False
    except Exception as error:
        print(f"User credentials error: {error}")
        press_any_key()
        return False

def user_choice_login(user: dict):
    clear_console()
    email = input("Please enter your email: ")
    password = input("Please enter your password: ")
    answer = validate_user_login(user, email, password)
    if answer == True:
        print("You are now logged in...")
        print(f"Welcome back, {user['name']}")
        press_any_key()
        return
    else:
        print("Something went wrong... Try again.")
        press_any_key()

def user_choice_logout(user: dict):
    user = {}

def handle_user_choice_after_login(user: dict, user_choice: str):
    valid_input = ['1', '2', '3', '4', '5', '6']
    if user_choice not in valid_input:
        print("Error. Invalid input, try again")
        press_any_key()
        return
    elif user_choice == '1':
        user_choice_view_all_posts()
        return
    elif user_choice == '2':
        user_choice_logout(user)
        return
    elif user_choice == '3':
        user_choice_register_new_user()
        return
    elif user_choice == '4':
        return
    elif user_choice == '5':
        return
    elif user_choice == '6':
        clear_console()
        print("Goodbye!")
        press_any_key()
        exit()

def handle_user_choice(user: dict, user_choice: str):
    if user:
        handle_user_choice_after_login(user, user_choice)
        return
    valid_input = ['1', '2', '3', '4']
    if user_choice not in valid_input:
        print("Error. Invalid input, try again")
        press_any_key()
        return
    elif user_choice == '1':
        user_choice_view_all_posts()
        return
    elif user_choice == '2':
        user_choice_login(user)
        return
    elif user_choice == '3':
        user_choice_register_new_user()
        return
    elif user_choice == '4':
        clear_console()
        print("Goodbye!")
        press_any_key()
        exit()