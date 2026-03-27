#!/bin/bash
pkg update -y
pkg i golang -y
clear
go build -o run_go run.go
echo "cara jalankan: ./run_go"
