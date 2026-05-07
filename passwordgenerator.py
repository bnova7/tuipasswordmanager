import random 
import string 
import pyperclip




try:
    random = ''.join([random.choice(string.ascii_letters + string.digits + string.punctuation)for n in range(16) ]) 

    try:
        print(random)
        if int(input("Enter 1 to copy password.")):
            pyperclip.copy(random)

    except ValueError:
        print("Invalid input.")

except KeyboardInterrupt:
    print("\nGoodbye.")





