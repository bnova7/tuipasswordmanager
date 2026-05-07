import getpass 
import json
import os 
import pyperclip
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM



def password_manager():
    try:
        filename = "vault.json"

        if not os.path.exists(filename):
            vault, salt = create_vault(filename)
        master_password = getpass.getpass("Enter your master password: ")
            

                

        try:
            vault, salt = open_vault(master_password)
            print("Vault unlocked.")

        except Exception as e:
            print("failed to unlock vault: ", type(e), e)
            return
        
        while True:
            # options: add pwd view entries delete entry and exit.
            print("\nOptions: ")
            print("1. Add Password")
            print("2. View Entries")
            print("3. Delete Entry")
            print("4. Exit")

            choice = input("> ")

            if choice == "1":
                site = input("Site: ")
                app_name = input("App name: ")
                username = input("username: ")
                password = getpass.getpass("Password: ")

                vault["accounts"].append({
                    "site": site,
                    "username": username,
                    "password": password

                })
                print("Entry added.")
            
            #view entry
            elif choice == "2":
                if not vault["accounts"]:
                    print("No entries.")
                    continue
                    
                
                for i, acc in enumerate(vault["accounts"]):
                    print(f"\n{i}. {acc['site']}")

                try:
                    index = int(input("\nEnter index to view: "))
                except ValueError:
                    print("Invalid input.")
                    continue

                if  0 <= index < len(vault["accounts"]):
                    acc = vault["accounts"][index]
                    print("\n--- Entry ---")
                    print(f"Site: {acc['site']}")
                    print(f"Username: {acc['username']}")
                    print(f"Password: {acc['password']}")
                    if int(input("Press 1 to copy the password.")) == 1:
                        pyperclip.copy(acc['password'])
                        print("password copied.")
                    else:
                        print("invalid input.")
                else:
                        print("Invalid index.")


            #delete entry
            elif choice == "3":
                index = int(input("Index to delete: "))

                if 0 <= index < len(vault["accounts"]):
                    vault["accounts"].pop(index)
                    print("Deleted.")

                else:
                    print("Invalid option.")


            #exit program
            elif choice == "4":
                save_vault(master_password,vault,salt)
                print("Vault saved, Goodbye.")
                break
            else:
                print("Invalid option.")
    except KeyboardInterrupt:
        print("Goodbye.")
        

        


#first time users get asked for master password
#write to the vault file 
#encrypt vault file 
def create_vault(filename="vault.json"):
    print("No vault found. Creating new vault.")

    password = getpass.getpass("Create master password: ")
    confirm = getpass.getpass("Confirm master password: ")

    if password != confirm:
        print("Passwords don't match.")
        return None, None
    
    vault = {
        "accounts": []
    }

    salt = os.urandom(16)

    save_vault(password, vault, salt, filename)

    print("Vault created successfully.")

    return vault, salt

    

# try unlocking the vault with master pwd 
#might need try except block 

def open_vault(master_password: str , filename = "vault.json"):
    with open(filename,"r") as f:
        data = json.load(f)

    #gets salt nonce and ciphertext from vault file
    salt = bytes.fromhex(data["salt"])
    nonce = bytes.fromhex(data["nonce"])
    ciphertext = bytes.fromhex(data["ciphertext"])
    
    key = derive_key(master_password, salt)
    aesgcm = AESGCM(key)

    plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    vault = json.loads(plaintext.decode())
    
    return vault, salt


def save_vault(master_password: str, vault: dict, salt: bytes, filename="vault.json"):
    print("about to save vault")
    key = derive_key(master_password, salt)
    aesgcm = AESGCM(key)

    nonce = os.urandom(12)

    plaintext = json.dumps(vault).encode()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    data = {
        "salt": salt.hex(),
        "nonce": nonce.hex(),
        "ciphertext": ciphertext.hex()
    }
    print("writing to file.")
    with open(filename,"w") as f:
        json.dump(data, f)
        print("file written")
    print("VAULT SAVED.")

    


def derive_key(password: str, salt: bytes)-> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000
    )

    return kdf.derive(password.encode())

print("Key derived successfully ")


if __name__ == "__main__":
    password_manager()