import secrets
import string 
import pyperclip

def generate_password(length = 16):
    password = ''.join([secrets.choice(string.ascii_letters + string.digits + string.punctuation)for n in range(length) ]) 
    return password

def main():
    try:
        
        password = generate_password()
        print(password)
        choice = input("Copy password? y/n: ").lower()

        if choice in ["y", "yes"]:
            pyperclip.copy(password)
            print("Password copied.")

        else:
            return
            

    except KeyboardInterrupt:
        print("\nGoodbye.")

if __name__ == "__main__":
    main()







