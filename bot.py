import requests

import time

import json

import random

import string

from web3 import Web3



# Fungsi untuk membuat daftar alamat wallet acak

def generate_wallets(count):

    w3 = Web3()

    wallets = []

    for _ in range(count):

        account = w3.eth.account.create()

        wallets.append(account.address)

    return wallets



# Fungsi untuk mendapatkan email sementara dari Guerrilla Mail

def get_temp_email():

    url = "https://api.guerrillamail.com/ajax.php?f=get_email_address"

    response = requests.get(url)

    data = response.json()

    email = data['email_addr']

    sid_token = data['sid_token']

    print(f"[INFO] Generated Temporary Email: {email}")

    return email, sid_token



# Fungsi untuk mendapatkan OTP dari Guerrilla Mail

def get_otp_from_guerrilla(email, sid_token):

    url = f"https://api.guerrillamail.com/ajax.php?f=check_email&seq=1&sid_token={sid_token}"

    

    for _ in range(24):  # 120 detik

        response = requests.get(url)

        if response.status_code == 200:

            data = response.json()

            messages = data.get('list', [])

            if messages:

                latest_message = messages[0]

                mail_id = latest_message['mail_id']

                fetch_url = f"https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id={mail_id}&sid_token={sid_token}"

                mail_response = requests.get(fetch_url)

                if mail_response.status_code == 200:

                    mail_data = mail_response.json()

                    mail_text = mail_data.get('mail_body', '')

                    for word in mail_text.split():

                        if word.isdigit() and len(word) == 6:

                            print(f"[INFO] OTP Found: {word}")

                            return word

        print("[INFO] Waiting for OTP... (5 seconds)")

        time.sleep(5)

    print("[ERROR] OTP not found within 120 seconds.")

    return None



# Langkah 1: Inisialisasi Passwordless

def init_passwordless(email):

    url = "https://auth.privy.io/api/v1/passwordless/init"

    headers = {

        "Content-Type": "application/json",

        "Accept": "application/json",

        "privy-app-id": "clxjfwh3d005bcewwp6vvtfm6",

        "privy-ca-id": "05809be7-08a0-421a-9bf2-48032805e9e5",

        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",

        "Origin": "https://oyachat.com",

        "Referer": "https://oyachat.com/"

    }

    payload = {"email": email}

    

    response = requests.post(url, json=payload, headers=headers)

    print(f"[INFO] Init Passwordless Status: {response.status_code}")

    print(f"[DEBUG] Response: {response.text}")

    return response.status_code == 200



# Langkah 2: Verifikasi OTP

def verify_otp(email, otp):

    url = "https://auth.privy.io/api/v1/passwordless/authenticate"

    headers = {

        "Content-Type": "application/json",

        "Accept": "application/json",

        "privy-app-id": "clxjfwh3d005bcewwp6vvtfm6",

        "privy-ca-id": "05809be7-08a0-421a-9bf2-48032805e9e5",

        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",

        "Origin": "https://oyachat.com",

        "Referer": "https://oyachat.com/"

    }

    payload = {

        "email": email,

        "code": otp

    }

    

    response = requests.post(url, json=payload, headers=headers)

    print(f"[INFO] Verify OTP Status: {response.status_code}")

    print(f"[DEBUG] Response: {response.text}")

    privy_token = response.json().get('token')

    user_id = response.json().get('user', {}).get('id')

    return response.status_code == 200, privy_token, user_id



# Langkah 3: Registrasi/Login ke Oyachat dengan wallet tertentu

def register_oyachat(email, privy_token, user_id, wallet_address, referral_code):

    url = "https://oyachat.com/api/wallet/login"

    headers = {

        "Content-Type": "application/json",

        "Accept": "*/*",

        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",

        "Origin": "https://oyachat.com",

        "Referer": f"https://oyachat.com/?referral_code={referral_code}",

        "Cookie": f"privy-token={privy_token}"

    }

    payload = {

        "email": email,

        "address": wallet_address,

        "referral_code": referral_code,

        "user": {

            "id": user_id,

            "createdAt": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())

        }

    }

    

    response = requests.post(url, json=payload, headers=headers)

    print(f"[INFO] Registration Status for {wallet_address}: {response.status_code}")

    print(f"[DEBUG] Response: {response.text}")

    if response.status_code == 201:

        print(f"[SUCCESS] Registration successful for {wallet_address} with referral code {referral_code}!")

    elif response.status_code == 200 and "Account already exists" not in response.text:

        print(f"[SUCCESS] Login successful for {wallet_address}, possibly registered with {referral_code}!")

    else:

        print(f"[ERROR] Failed to register {wallet_address}. Check response for details.")

    return response.status_code == 201



# Eksekusi

if __name__ == "__main__":

    print("=== Oyachat Auto Registration Script ===")

    

    # Minta kode referral dari pengguna

    referral_code = input("Enter your referral code: ").strip()

    if not referral_code:

        print("[ERROR] Referral code cannot be empty.")

        exit()



    # Minta jumlah wallet yang ingin digenerate

    try:

        num_wallets = int(input("Enter the number of wallets to generate: "))

        if num_wallets <= 0:

            raise ValueError("Number must be greater than 0.")

    except ValueError as e:

        print(f"[ERROR] Invalid input: {e}. Please enter a positive number.")

        exit()



    # Generate wallet sesuai jumlah yang diinput

    print(f"[INFO] Generating {num_wallets} wallets...")

    wallets = generate_wallets(num_wallets)

    print(f"[INFO] Generated Wallets: {wallets}")



    # Proses setiap wallet

    for i, wallet in enumerate(wallets, 1):

        print(f"\n{'='*50}")

        print(f"[INFO] Processing Wallet {i}/{num_wallets}: {wallet}")

        

        # Dapatkan email sementara baru untuk setiap wallet

        email, sid_token = get_temp_email()

        

        if init_passwordless(email):

            otp = get_otp_from_guerrilla(email, sid_token)

            if otp:

                success, privy_token, user_id = verify_otp(email, otp)

                if success:

                    if register_oyachat(email, privy_token, user_id, wallet, referral_code):

                        print(f"[SUCCESS] Wallet {wallet} registered successfully!")

                    else:

                        print(f"[ERROR] Registration failed for wallet {wallet}.")

                else:

                    print(f"[ERROR] OTP verification failed for wallet {wallet}.")

            else:

                print(f"[ERROR] Failed to retrieve OTP for wallet {wallet}.")

        else:

            print(f"[ERROR] Failed to initiate passwordless for wallet {wallet}.")

    

    print(f"\n{'='*50}")

    print("[INFO] Script execution completed.")
