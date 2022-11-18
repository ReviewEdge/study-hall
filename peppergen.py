from password_hasher import PasswordHasher
pepper_key = PasswordHasher.random_pepper()
with open("pepper.bin", 'wb') as fout:
    fout.write(pepper_key)
