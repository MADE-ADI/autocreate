#!/bin/bash

# Path ke file proxy
PROXY_FILE="proxy.txt"

# Periksa apakah file proxy ada
if [[ ! -f "$PROXY_FILE" ]]; then
    echo "File $PROXY_FILE tidak ditemukan!"
    exit 1
fi

# Loop melalui setiap proxy di file
while IFS= read -r PROXY; do
    # Lewati baris kosong
    [[ -z "$PROXY" ]] && continue

    # Validasi format proxy
    if [[ ! "$PROXY" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:[0-9]+:[^:]+:[^:]+$ ]]; then
        echo "Format proxy tidak valid: $PROXY"
        continue
    fi

    # Parse proxy
    IP=$(echo "$PROXY" | cut -d':' -f1)
    PORT=$(echo "$PROXY" | cut -d':' -f2)
    USERNAME=$(echo "$PROXY" | cut -d':' -f3)
    PASSWORD=$(echo "$PROXY" | cut -d':' -f4)

    # Tampilkan proxy yang sedang digunakan
    echo "Menggunakan proxy: $IP:$PORT dengan username $USERNAME"

    # Atur proxy untuk skrip
    export http_proxy="http://$USERNAME:$PASSWORD@$IP:$PORT"
    export https_proxy="http://$USERNAME:$PASSWORD@$IP:$PORT"

    # Jalankan skrip PHP (uncomment jika diperlukan)
    php run.php

    # Hapus pengaturan proxy (opsional)
    unset http_proxy
    unset https_proxy

    # Beri jeda waktu (opsional)
    sleep 5
done < "$PROXY_FILE"

