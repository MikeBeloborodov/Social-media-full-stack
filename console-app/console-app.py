import requests
from functions import *

def main():
    user = {}
    while True:
        render_main_menu(user)
        user_choice = input("Enter your choice: ")
        handle_user_choice(user, user_choice)

if __name__ == "__main__":
    main()