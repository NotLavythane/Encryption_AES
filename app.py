from flask import Flask, render_template, request, jsonify
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.exceptions import InvalidTag
import os

app = Flask(__name__)

# In-memory session state (demo purpose)
STATE = {
    "key": None,
    "mode": None,
    "iv": None,
    "ciphertext": None,
    "tag": None
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate-key", methods=["POST"])
def generate_key():
    bits = int(request.json["bits"])
    key = os.urandom(bits // 8)

    STATE.update({
        "key": key,
        "mode": None,
        "iv": None,
        "ciphertext": None,
        "tag": None
    })

    return jsonify({"key": key.hex()})

@app.route("/encrypt", methods=["POST"])
def encrypt():
    data = request.json
    plaintext = data["plaintext"].encode()
    mode = data["mode"]

    key = STATE["key"]
    iv = os.urandom(12 if mode == "GCM" else 16)

    if mode == "GCM":
        encryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv)
        ).encryptor()

        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        tag = encryptor.tag

    else:  # CBC
        padder = padding.PKCS7(128).padder()
        padded = padder.update(plaintext) + padder.finalize()

        encryptor = Cipher(
            algorithms.AES(key),
            modes.CBC(iv)
        ).encryptor()

        ciphertext = encryptor.update(padded) + encryptor.finalize()
        tag = None

    STATE.update({
        "mode": mode,
        "iv": iv,
        "ciphertext": ciphertext,
        "tag": tag
    })

    return jsonify({
        "ciphertext": ciphertext.hex(),
        "iv": iv.hex(),
        "tag": tag.hex() if tag else None
    })

@app.route("/decrypt", methods=["POST"])
def decrypt():
    try:
        key = STATE["key"]
        iv = STATE["iv"]
        ciphertext = STATE["ciphertext"]
        tag = STATE["tag"]
        mode = STATE["mode"]

        if mode == "GCM":
            decryptor = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, tag)
            ).decryptor()

            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return jsonify({"output": plaintext.decode()})

        else:
            decryptor = Cipher(
                algorithms.AES(key),
                modes.CBC(iv)
            ).decryptor()

            padded = decryptor.update(ciphertext) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded) + unpadder.finalize()

            return jsonify({"output": plaintext.decode()})

    except InvalidTag:
        return jsonify({
            "output": "[AES-GCM AUTHENTICATION FAILED — TAMPERING DETECTED]"
        })

    except ValueError:
        return jsonify({
            "output": "[CBC INTEGRITY FAILURE — PADDING CORRUPTED]"
        })

@app.route("/bitflip", methods=["POST"])
def bitflip():
    if STATE["mode"] != "CBC":
        return jsonify({"error": "Only CBC supports bit-flipping demo"})

    tampered = bytearray(STATE["ciphertext"])
    tampered[0] ^= 0x01
    STATE["ciphertext"] = bytes(tampered)

    return jsonify({"status": "bit flipped"})

if __name__ == "__main__":
    app.run(debug=True)
