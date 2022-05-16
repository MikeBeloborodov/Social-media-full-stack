from functions import *

def main():
    user = {}
    while True:
        check_connection()
        render_main_menu(user)
        user_choice = input("Enter your choice: ")
        check_connection()
        handle_user_choice(user, user_choice)

if __name__ == "__main__":
    main()