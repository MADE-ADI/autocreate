#!/usr/bin/env python3

import requests
import json
import random
import string
import time
import re
import os
import sys
from datetime import datetime

requests.packages.urllib3.disable_warnings()

# ============================== WARNA ==============================

BIRU    = "\033[1;34m"
KUNING  = "\033[1;33m"
MERAH   = "\033[1;31m"
PUTIH   = "\033[1;37m"
HIJAU   = "\033[1;32m"
CYAN    = "\033[1;36m"
UNGU    = "\033[1;35m"
ABU     = "\033[0;90m"
END     = "\033[0m"

# ============================== NICKNAME INDO ==============================

NAMA_DEPAN = [
    "Adi", "Agus", "Ayu", "Bayu", "Budi", "Citra", "Dani", "Dewi", "Eka",
    "Fajar", "Galih", "Hadi", "Indra", "Joko", "Kiki", "Lina", "Mira",
    "Nanda", "Oki", "Putu", "Rani", "Sari", "Tika", "Udin", "Vina",
    "Wati", "Yani", "Zaki", "Rizki", "Dinda", "Farel", "Gita", "Hana",
    "Ilham", "Jaya", "Kirana", "Lestari", "Mega", "Nisa", "Okta",
    "Putri", "Raka", "Sinta", "Tiara", "Ulfa", "Vega", "Wulan", "Yoga",
    "Zahra", "Arya", "Bagus", "Cahya", "Dimas", "Elang", "Firman",
    "Gilang", "Hafiz", "Intan", "Jihan", "Kayla", "Laras", "Melati",
    "Nabila", "Omar", "Pandu", "Radit", "Satria", "Taufik", "Umi",
    "Vera", "Wahyu", "Yuda", "Zidan", "Anggi", "Bintang", "Cakra",
    "Damar", "Eza", "Fina", "Gani", "Hesti", "Icha", "Juni", "Kemal",
    "Luna", "Maulana", "Nayla", "Ojan", "Pras", "Rahma", "Surya",
    "Tara", "Umar", "Vino", "Wira", "Yogi", "Zara"
]

NAMA_BELAKANG = [
    "Pratama", "Saputra", "Wijaya", "Kusuma", "Putra", "Putri", "Sari",
    "Lestari", "Wati", "Ningsih", "Rahayu", "Cahyani", "Permana",
    "Nugraha", "Ramadhan", "Hidayat", "Firmansyah", "Setiawan", "Hakim",
    "Utama", "Santoso", "Wibowo", "Suryadi", "Purnama", "Handoko",
    "Prasetyo", "Gunawan", "Susanto", "Hartono", "Kurniawan", "Aditya",
    "Mahendra", "Anggara", "Perdana", "Pamungkas"
]

AKHIRAN = ["", "x", "z", "_", ".", "27", "12", "99", "88", "77", "01", "69",
           "ID", "id", "Jr", "jr", "v2", "XD", "xd", "gg", "GG", "YT", "yt"]


def random_nickname():
    style = random.choice(["full", "depan_angka", "depan_akhiran", "gabung"])
    if style == "full":
        return f"{random.choice(NAMA_DEPAN)} {random.choice(NAMA_BELAKANG)}"
    elif style == "depan_angka":
        return f"{random.choice(NAMA_DEPAN)}{random.randint(1, 999)}"
    elif style == "depan_akhiran":
        return f"{random.choice(NAMA_DEPAN)}{random.choice(AKHIRAN)}"
    else:
        return f"{random.choice(NAMA_DEPAN)}{random.choice(NAMA_BELAKANG)[:3]}{random.randint(0, 99)}"


def random_string(length=10):
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    return "".join(random.choice(chars) for _ in range(length))


def log(color, msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{ABU}[{ts}]{END} {color}{msg}{END}")


# ============================== PROXY ==============================

def load_proxies(path="proxy.txt"):
    proxies = []
    if not os.path.isfile(path):
        log(MERAH, f"File {path} tidak ditemukan!")
        sys.exit(1)
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(":")
            if len(parts) == 4:
                ip, port, user, pwd = parts
                proxy_url = f"http://{user}:{pwd}@{ip}:{port}"
                proxies.append({"http": proxy_url, "https": proxy_url, "raw": line})
            elif len(parts) == 2:
                ip, port = parts
                proxy_url = f"http://{ip}:{port}"
                proxies.append({"http": proxy_url, "https": proxy_url, "raw": line})
    log(PUTIH, f"Total proxy dimuat: {len(proxies)}")
    return proxies


# ============================== API ZEPETO ==============================

class Zepeto:
    BASE = "https://gw-napi.zepeto.io"

    def __init__(self, proxy=None):
        self.session = requests.Session()
        self.session.verify = False
        if proxy:
            self.session.proxies = {"http": proxy["http"], "https": proxy["https"]}
        self.auth_token = None

    def _headers_token(self):
        return {
            "Host": "gw-napi.zepeto.io",
            "X-Zepeto-Duid": random_string(32),
            "User-Agent": "Mozilla/5.0 (Windows 98; Win 9x 4.90) AppleWebKit/533.2 "
                          "(KHTML, like Gecko) Chrome/80.0.4147.39 Safari/533.2 Edg/80.01080.48",
            "Content-Type": "application/json; charset=utf-8",
        }

    def _headers_auth(self):
        return {
            "Host": "gw-napi.zepeto.io",
            "Authorization": f"Bearer {self.auth_token}",
            "X-Zepeto-Duid": random_string(32),
            "User-Agent": "android.zepeto_global/3.48.100 (android; U; Android OS 7.1.2 "
                          "/ API-25 (QKQ1.190825.002/G9550ZHU1AQEE); id-ID; occ-ID; asus ASUS_Z01QD)",
            "X-Timezone": "Asia/Moscow",
            "Content-Type": "application/json; charset=utf-8",
        }

    def _post(self, endpoint, data, headers=None):
        url = f"{self.BASE}/{endpoint}"
        h = headers or self._headers_auth()
        for attempt in range(3):
            try:
                r = self.session.post(url, headers=h, data=json.dumps(data), timeout=60)
                return r.json()
            except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError):
                if attempt < 2:
                    time.sleep(3)
                else:
                    log(MERAH, f"Proxy error [{endpoint}] setelah 3x retry")
                    return {}
            except requests.exceptions.Timeout:
                if attempt < 2:
                    time.sleep(2)
                else:
                    log(MERAH, f"Timeout [{endpoint}]")
                    return {}
            except Exception:
                return {}

    # --- Auth ---
    def get_token(self):
        data = {"deviceId": random_string(32)}
        result = self._post("DeviceAuthenticationRequest", data, self._headers_token())
        self.auth_token = result.get("authToken")
        return self.auth_token is not None

    # --- Registration steps ---
    def accusr(self):
        return self._post("AccountUser_v5", {
            "creatorAllItemsVersion": "_",
            "creatorHotItemGroupId": "_",
            "creatorHotItemsVersion": "_",
            "creatorNewItemsVersion": "_",
            "params": {"appVersion": "3.48.100", "itemVersion": "_", "language": "_", "platform": "_"},
            "timeZone": "Asia/Moscow",
        })

    def agree1(self):
        return self._post("SaveUserDataPolicyRequest", {"country": "ru"})

    def agree2(self):
        return self._post("GetUserAppProperty", {"key": "agreeTermsDate"})

    def agree3(self):
        return self._post("PutUserAppProperty", {"key": "agreeTermsDate", "value": datetime.now().isoformat()})

    def pushreg(self):
        return self._post("PushRegistrationRequest", {
            "platform": "Android", "provider": "FCM",
            "pushId": "ejyrBwjWRU2XJjtJg-WXET:APA91bG-hocRcsgs6Nh9-aWKTeyKjR_"
                      "djCrCJjlImGyn5Olz6l97gSKm7g8IaSKYQXYQSmfntIS32Ua1_ZGMukSS"
                      "yldw-4Z_CB1fRrmpJHviUClHO9kTwFWABRk1qSMVnicbtctU81MU",
            "pushOn": True,
        })

    def char(self):
        return self._post("CopyCharacterByHashcode", {"hashCode": "ZPT115", "characterId": ""})

    def save_profile(self, nickname):
        return self._post("SaveProfileRequest_v2", {
            "job": "spy", "name": nickname, "nationality": "", "statusMessage": "nojalpro",
        })

    def follow(self):
        return self._post("FollowRequest_v2", {"followUserId": "65c62931734c7765c37aa8fc"})

    # --- Email verification ---
    def email_verify_request(self, email):
        return self._post("EmailVerificationRequest", {"email": email})

    def email_confirm(self, email, otp):
        return self._post("EmailConfirmationRequest", {"email": email, "verifyCode": otp})

    # --- Register ---
    def register(self, email, password="Nojal3123"):
        return self._post("UserRegisterRequest_v2", {
            "userName": email, "displayName": email, "password": password,
        })

    def init_zepeto_id(self, zepeto_id):
        return self._post("InitZepetoIdRequest", {"zepetoId": zepeto_id, "place": "signup"})

    def login(self, zepeto_id, password="Nojal3123"):
        return self._post("AuthenticationRequest_v2", {"userId": zepeto_id, "password": password})


# ============================== FAKE EMAIL ==============================

class FakeEmail:
    URL = "https://email-fake.com"
    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/109.0.5405.114 Safari/537.36",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update(self.HEADERS)

    def get_email(self):
        for attempt in range(3):
            try:
                r = self.session.get(f"{self.URL}/", timeout=30)
                match = re.search(r'<span id="email_ch_text">([^<]+)</span>', r.text)
                if match:
                    return match.group(1)
            except Exception:
                if attempt < 2:
                    time.sleep(2)
        return None

    def get_otp(self, email):
        try:
            r = self.session.get(f"{self.URL}/{email}", timeout=30)
            match = re.search(
                r'<span id="verificaiton-code-text"[^>]*>(\d+)</span>', r.text
            )
            return match.group(1) if match else None
        except Exception:
            return None


# ============================== CREATE ACCOUNT ==============================

def create_account(proxy, nomor):
    proxy_short = proxy["raw"].split(":")[0]
    log(UNGU, f"[Akun #{nomor}] Proxy: {proxy_short}")

    zep = Zepeto(proxy)
    fem = FakeEmail()

    # 1. Token
    if not zep.get_token():
        log(MERAH, f"[Akun #{nomor}] Gagal ambil token")
        return False

    log(CYAN, f"[Akun #{nomor}] Token OK")

    # 2. Fake email
    email = fem.get_email()
    if not email:
        log(MERAH, f"[Akun #{nomor}] Gagal ambil email")
        return False

    log(PUTIH, f"[Akun #{nomor}] Email: {email}")

    # 3. Setup akun
    zep.accusr()
    zep.agree1()
    zep.agree2()
    zep.agree3()
    zep.pushreg()
    zep.char()

    nickname = random_nickname()
    zep.save_profile(nickname)
    log(PUTIH, f"[Akun #{nomor}] Nickname: {nickname}")

    # 4. Email verification
    zep.email_verify_request(email)
    log(KUNING, f"[Akun #{nomor}] Menunggu OTP...")

    otp = None
    for attempt in range(5):
        time.sleep(3)
        otp = fem.get_otp(email)
        if otp:
            break
        log(KUNING, f"[Akun #{nomor}] Mengecek OTP... ({attempt + 1}/5)")

    if not otp:
        log(MERAH, f"[Akun #{nomor}] OTP tidak ditemukan")
        return False

    confirm = zep.email_confirm(email, otp)
    if confirm.get("isSuccess") != 1 and confirm.get("isSuccess") is not True:
        log(MERAH, f"[Akun #{nomor}] Verifikasi OTP gagal")
        return False

    log(CYAN, f"[Akun #{nomor}] OTP Berhasil: {otp}")

    # 5. Register
    reg = zep.register(email)
    if not reg.get("isSuccess"):
        log(MERAH, f"[Akun #{nomor}] Register gagal: {reg}")
        return False

    # 6. Set Zepeto ID
    zepeto_id = random_string(8)
    zep.init_zepeto_id(zepeto_id)

    # 7. Login test
    zep.login(zepeto_id)

    # 8. Follow
    zep.follow()

    # 9. Simpan
    with open("akun.txt", "a") as f:
        f.write(f"{email}|Nojal3123\n")

    log(HIJAU, f"[Akun #{nomor}] BERHASIL -> {email} | Pass: Nojal3123 | Nick: {nickname}")
    return True


# ============================== MAIN ==============================

def main():
    print(f"""
{CYAN}╔══════════════════════════════════════════════╗
║     ZEPETO AUTO CREATE - Python Edition      ║
║   Batch 10 Proxy | 1-2 Akun/Proxy | Proxy   ║
╚══════════════════════════════════════════════╝{END}
""")

    proxies = load_proxies("proxy.txt")
    if not proxies:
        log(MERAH, "Tidak ada proxy!")
        sys.exit(1)

    batch_size = 10
    total_akun = 0
    batch_num = 0

    # Hapus cookie lama
    if os.path.isfile("cookie.txt"):
        os.remove("cookie.txt")

    for i in range(0, len(proxies), batch_size):
        batch = proxies[i:i + batch_size]
        batch_num += 1
        log(BIRU, f"{'=' * 50}")
        log(BIRU, f"BATCH #{batch_num} | Proxy {i + 1}-{i + len(batch)} dari {len(proxies)}")
        log(BIRU, f"{'=' * 50}")

        for j, proxy in enumerate(batch):
            jumlah_akun = random.randint(1, 2)
            proxy_short = proxy["raw"].split(":")[0]
            log(UNGU, f"Proxy [{j + 1}/{len(batch)}]: {proxy_short} -> {jumlah_akun} akun")

            for k in range(jumlah_akun):
                total_akun += 1
                success = create_account(proxy, total_akun)

                if not success:
                    log(MERAH, f"Gagal, lanjut...")

                # Jeda antar akun: 2-4 menit
                if k < jumlah_akun - 1:
                    jeda = random.randint(120, 240)
                    log(KUNING, f"Jeda antar akun: {jeda // 60}m {jeda % 60}s")
                    time.sleep(jeda)

            # Jeda antar proxy dalam batch: 30-60 detik
            if j < len(batch) - 1:
                jeda = random.randint(30, 60)
                log(ABU, f"Jeda antar proxy: {jeda}s")
                time.sleep(jeda)

        log(HIJAU, f"Batch #{batch_num} selesai | Total akun dibuat: {total_akun}")

        # Jeda antar batch: 20-30 menit
        if i + batch_size < len(proxies):
            jeda = random.randint(1200, 1800)
            menit = jeda // 60
            detik = jeda % 60
            log(KUNING, f"Jeda antar batch: {menit}m {detik}s")
            log(KUNING, f"Lanjut batch berikutnya pukul: "
                        f"{datetime.fromtimestamp(time.time() + jeda).strftime('%H:%M:%S')}")
            time.sleep(jeda)

    print(f"\n{HIJAU}{'=' * 50}")
    log(HIJAU, f"SELESAI! Total akun dibuat: {total_akun}")
    log(PUTIH, f"Akun tersimpan di akun.txt")
    print(f"{'=' * 50}{END}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{KUNING}[!] Dihentikan oleh user (CTRL+C){END}")
        print(f"{PUTIH}[*] Akun yang sudah dibuat tersimpan di akun.txt{END}")
        sys.exit(0)
