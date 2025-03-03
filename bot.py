import requests
import time
import json
import random
import string
from web3 import Web3
import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.table import Table
from tqdm import tqdm

# Setup logging dengan RichHandler
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("OyachatScript")
console = Console()

# Banner
def print_banner():
    console.print("[bold cyan]╔════════════════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║                 OYACHAT AUTO BOT                   ║[/bold cyan]")
    console.print("[bold cyan]║         Automate your Oyachat registration!        ║[/bold cyan]")
    console.print("[bold cyan]║    Developed by: https://t.me/Offical_Im_kazuha    ║[/bold cyan]")
    console.print("[bold cyan]║    GitHub: https://github.com/Kazuha787            ║[/bold cyan]")
    console.print("[bold cyan]╠════════════════════════════════════════════════════╣[/bold cyan]")
    console.print("[bold cyan]║                                                    ║[/bold cyan]")
    console.print("[bold cyan]║  ██╗  ██╗ █████╗ ███████╗██╗   ██╗██╗  ██╗ █████╗  ║[/bold cyan]")
    console.print("[bold cyan]║  ██║ ██╔╝██╔══██╗╚══███╔╝██║   ██║██║  ██║██╔══██╗ ║[/bold cyan]")
    console.print("[bold cyan]║  █████╔╝ ███████║  ███╔╝ ██║   ██║███████║███████║ ║[/bold cyan]")
    console.print("[bold cyan]║  ██╔═██╗ ██╔══██║ ███╔╝  ██║   ██║██╔══██║██╔══██║ ║[/bold cyan]")
    console.print("[bold cyan]║  ██║  ██╗██║  ██║███████╗╚██████╔╝██║  ██║██║  ██║ ║[/bold cyan]")
    console.print("[bold cyan]║  ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ║[/bold cyan]")
    console.print("[bold cyan]║                                                    ║[/bold cyan]")
    console.print("[bold cyan]╚════════════════════════════════════════════════════╝[/bold cyan]")

# Fungsi untuk membuat daftar alamat wallet acak
def generate_wallets(count):
    w3 = Web3()
    wallets = []
    for _ in range(count):
        account = w3.eth.account.create()
        wallets.append(account.address)
    return wallets

# (Rest of your script remains unchanged)
# Fungsi untuk membuat daftar alamat wallet acak
def generate_wallets(count):
    w3 = Web3()
    wallets = []
    for _ in range(count):
        account = w3.eth.account.create()
        wallets.append(account.address)
    return wallets

# Fungsi untuk mendapatkan email sementara dari Guerrilla Mail
def get_temp_email_guerrilla():
    url = "https://api.guerrillamail.com/ajax.php?f=get_email_address"
    response = requests.get(url)
    data = response.json()
    email = data['email_addr']
    sid_token = data['sid_token']
    logger.info(f"Generated Guerrilla Email: {email}")
    return email, sid_token

# Fungsi untuk mendapatkan domain yang tersedia dari mail.tm
def get_mailtm_domains():
    url = "https://api.mail.tm/domains"
    response = requests.get(url)
    if response.status_code == 200:
        domains = response.json()['hydra:member']
        return domains[0]['domain']
    logger.error(f"Failed to fetch mail.tm domains: {response.status_code} - {response.text}")
    return "xxnm.me"

# Fungsi untuk mendapatkan email sementara dari mail.tm dengan retry
def get_temp_email_mailtm():
    domain = get_mailtm_domains()
    url = "https://api.mail.tm/accounts"
    headers = {"Content-Type": "application/json"}
    email_address = f"{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}@{domain}"
    payload = {"address": email_address, "password": "temporarypassword123"}
    
    for attempt in range(3):
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            data = response.json()
            email = data['address']
            token_url = "https://api.mail.tm/token"
            token_response = requests.post(token_url, json=payload, headers=headers)
            if token_response.status_code == 200:
                token = token_response.json()['token']
                logger.info(f"Generated mail.tm Email: {email}")
                return email, token
            else:
                logger.error(f"Failed to get mail.tm token: {token_response.status_code} - {token_response.text}")
        elif response.status_code == 429:
            logger.warning(f"Rate limit hit (429), retrying in {2 ** attempt} seconds...")
            time.sleep(2 ** attempt)
            continue
        else:
            logger.error(f"Failed to create mail.tm email: {response.status_code} - {response.text}")
        time.sleep(1)
    logger.error("Failed to create mail.tm email after retries")
    return None, None

# Fungsi untuk memilih provider email
def get_temp_email(provider_choice):
    if provider_choice == "1":
        return get_temp_email_guerrilla()
    elif provider_choice == "2":
        return get_temp_email_mailtm()
    else:
        logger.error("Invalid email provider selected")
        return None, None

# Fungsi untuk mendapatkan OTP dari Guerrilla Mail
def get_otp_guerrilla(email, sid_token):
    url = f"https://api.guerrillamail.com/ajax.php?f=check_email&seq=1&sid_token={sid_token}"
    for _ in range(24):
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
                            logger.info(f"OTP Found: {word}")
                            return word
        logger.info("Waiting for OTP... (5 seconds)")
        time.sleep(5)
    logger.error("OTP not found within 120 seconds")
    return None

# Fungsi untuk mendapatkan OTP dari mail.tm
def get_otp_mailtm(email, token):
    url = "https://api.mail.tm/messages"
    headers = {"Authorization": f"Bearer {token}"}
    for _ in range(24):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data['hydra:member']:
                latest_message = data['hydra:member'][0]
                msg_url = f"https://api.mail.tm/messages/{latest_message['id']}"
                msg_response = requests.get(msg_url, headers=headers)
                if msg_response.status_code == 200:
                    mail_data = msg_response.json()
                    mail_text = mail_data.get('text', '')
                    for word in mail_text.split():
                        if word.isdigit() and len(word) == 6:
                            logger.info(f"OTP Found: {word}")
                            return word
        elif response.status_code == 429:
            logger.warning("Rate limit hit (429) while fetching OTP, waiting 5 seconds...")
            time.sleep(5)
            continue
        logger.info("Waiting for OTP... (5 seconds)")
        time.sleep(5)
    logger.error("OTP not found within 120 seconds")
    return None

# Fungsi untuk mendapatkan OTP berdasarkan provider
def get_otp(email, token, provider_choice):
    if provider_choice == "1":
        return get_otp_guerrilla(email, token)
    elif provider_choice == "2":
        return get_otp_mailtm(email, token)
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
    logger.info(f"Init Passwordless Status: {response.status_code}")
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
    payload = {"email": email, "code": otp}
    
    response = requests.post(url, json=payload, headers=headers)
    logger.info(f"Verify OTP Status: {response.status_code}")
    privy_token = response.json().get('token')
    user_id = response.json().get('user', {}).get('id')
    return response.status_code == 200, privy_token, user_id

# Langkah 3: Registrasi/Login ke Oyachat
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
    logger.info(f"Registration Status for {wallet_address}: {response.status_code}")
    return response.status_code == 201

# Proses registrasi untuk satu wallet
def process_wallet(wallet, referral_code, provider_choice):
    console.print(f"\n[bold cyan]{'='*50}[/bold cyan]")
    logger.info(f"Processing Wallet: {wallet}")
    email, token = get_temp_email(provider_choice)
    if email and token and init_passwordless(email):
        otp = get_otp(email, token, provider_choice)
        if otp:
            success, privy_token, user_id = verify_otp(email, otp)
            if success:
                if register_oyachat(email, privy_token, user_id, wallet, referral_code):
                    logger.info(f"Wallet {wallet} registered successfully!", extra={"markup": True, "highlighter": None})
                    return True
                else:
                    logger.error(f"Registration failed for wallet {wallet}")
            else:
                logger.error(f"OTP verification failed for wallet {wallet}")
        else:
            logger.error(f"Failed to retrieve OTP for wallet {wallet}")
    else:
        logger.error(f"Failed to initiate process for wallet {wallet}")
    return False

# Eksekusi berurutan dengan ringkasan tabel
if __name__ == "__main__":
    print_banner()
    
    referral_code = input("Enter your referral code: ").strip()
    if not referral_code:
        logger.error("Referral code cannot be empty")
        exit()

    try:
        num_wallets = int(input("Enter the number of wallets to generate: "))
        if num_wallets <= 0:
            raise ValueError("Number must be greater than 0.")
    except ValueError as e:
        logger.error(f"Invalid input: {e}. Please enter a positive number")
        exit()

    console.print("Choose email provider:")
    console.print("1. Guerrilla Mail")
    console.print("2. mail.tm")
    provider_choice = input("Enter your choice (1 or 2): ").strip()
    if provider_choice not in ["1", "2"]:
        logger.error("Invalid choice. Please enter 1 or 2")
        exit()

    logger.info(f"Generating {num_wallets} wallets...")
    wallets = generate_wallets(num_wallets)
    logger.info(f"Berhasil generate {num_wallets} wallet")

    # Menyimpan hasil untuk ringkasan
    results = []

    # Proses setiap wallet dengan tqdm progress bar
    for i, wallet in enumerate(tqdm(wallets, desc="Processing Wallets", unit="wallet"), 1):
        logger.info(f"Processing wallet {i}/{num_wallets}")
        success = process_wallet(wallet, referral_code, provider_choice)
        results.append((wallet, "Success" if success else "Failed"))

    # Tampilkan ringkasan dalam tabel
    console.print(f"\n[bold cyan]{'='*50}[/bold cyan]")
    table = Table(title="Registration Summary", show_header=True, header_style="bold magenta")
    table.add_column("Wallet Address", style="cyan", overflow="fold")
    table.add_column("Status", justify="center", style="green")
    
    for wallet, status in results:
        table.add_row(wallet, f"[{'green' if status == 'Success' else 'red'}]{status}[/]")

    console.print(table)
    logger.info("Script execution completed")
      
