from Cryptodome.Cipher import AES


def encode(tg_id, password):
    delta = 16 - len(tg_id)
    key = tg_id
    while delta != 0:
        key += 'L'
        delta -= 1
    key = str.encode(key)
    cipher = AES.new(key, AES.MODE_EAX)
    data = str.encode(password)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return {'nonce': nonce, 'ciphertext': ciphertext, 'tag': tag}


def decode(tg_id, nonce, ciphertext, tag):
    delta = 16 - len(tg_id)
    key = tg_id
    while delta != 0:
        key += 'L'
        delta -= 1
    key = str.encode(key)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext).decode('utf-8')
    try:
        cipher.verify(tag)
        return plaintext
    except ValueError:
        print("Key incorrect or message corrupted")

# encode('74190981', '123456')
# decode('74190981', b'H$\xffG\xfcf\re\x04\xe4P\xff\xbb\x9a\xb4\xba', b'\x9d^yq\xe3y', b'\xa9\x04\xcd\xb9\xb0\xbe\xaf\xb1\x88\x13\xfd\xa9\x04\xbb\xb9Y')