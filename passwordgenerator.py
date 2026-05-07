import secrets
import string 
import pyperclip

def generate_password(length = 16):
    password = ''.join([secrets.choice(string.ascii_letters + string.digits + string.punctuation)for n in range(length) ]) 
    return password

def main():
    try:
        try:
            password = generate_password()
            print(password)
            if input("Enter y to copy password.") == 'y' or 'yes':
                pyperclip.copy(password)
            print("password copied.")
        except ValueError:
            print("Invalid input.")
    except KeyboardInterrupt:
        print("\nGoodbye.")

if __name__ == "__main__":
    main()







