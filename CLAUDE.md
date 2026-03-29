# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Zepeto account auto-creation bot. Automates bulk Zepeto account registration using proxies, disposable emails (email-fake.com), and the Zepeto API (`gw-napi.zepeto.io`). The same logic is implemented in three languages: Go, Python, and PHP.

## Build & Run Commands

| Action | Command |
|--------|---------|
| Build Go binary | `go build -o run_go run.go` |
| Run (Go) | `./run_go` |
| Run (Python) | `python3 run.py` |
| Run (PHP) | `php run.php` |
| Build for Termux | `bash main.sh` |
| Test proxies | `python3 proxy_tester.py -f proxy.txt` |

There are no tests, linting, or CI/CD pipelines.

## Architecture

All three implementations (`run.go`, `run.py`, `run.php`) follow the same flow:

1. Load proxies from `proxy.txt` (format: `host:port:user:pass`)
2. Process proxies in batches of 10, creating 1-2 accounts per proxy
3. For each account: get device auth token → generate fake email → set up account (agree to terms, push registration, copy character, save profile) → request email verification → scrape OTP from email-fake.com → confirm email → register with password → set Zepeto ID → test login → auto-follow target user
4. Save credentials to `akun.txt` (format: `email|password`)
5. Rate-limit with delays: 3-5 min between accounts, 30-60s between proxies, 10 min between batches

### Key modules (within each file)

- **Proxy loader** - Parses `proxy.txt`, supports authenticated (`host:port:user:pass`) and simple (`host:port`) formats
- **HTTP client** - Proxy-aware client with TLS skip verification and cookie jar; direct (non-proxied) client for email scraping
- **Zepeto API struct/class** - All REST calls to `gw-napi.zepeto.io` (DeviceAuthRequest, AccountUser_v5, EmailVerification, UserRegister_v2, etc.)
- **FakeEmail struct/class** - Scrapes `email-fake.com` for disposable email addresses and OTP codes via regex
- **Account creator** - Orchestrates the full registration flow with retry logic
- **Main loop** - Batched sequential execution with randomized delays

### Language-specific differences

- **Go** (`run.go`): Primary/latest version. Uses stdlib only (no external deps). Has `sync.Mutex` for concurrent file writes but runs accounts sequentially within batches. Handles SIGINT gracefully.
- **Python** (`run.py`): Uses `requests` library (not in a requirements.txt). Same sequential flow.
- **PHP** (`run.php`): Original version. Uses `curl` extension. Uses `goto` for flow control. Targets 1M accounts.

## Supporting Utilities

- `proxy_tester.py` - Threaded proxy tester (20 workers, HTTPS CONNECT tunnel, reports latency)
- `parse.py` - Converts JSON proxy data (`results.json`) to `ip:port` text format (`output.txt`)
- `cek.sh` / `cek2.sh` - Bash proxy checkers using curl

## Important Files

- `proxy.txt` - Input: proxy list (authenticated proxies with credentials)
- `akun.txt` - Output: created account credentials (`email|password`)
- `go.mod` - Go module (`autocreate`, Go 1.24, zero external dependencies)

## Language & Conventions

- All comments, variable names, and UI text are in **Bahasa Indonesia** (e.g., `BIRU`=blue, `MERAH`=red, `akun`=account, `jeda`=delay, `gagal`=failed, `berhasil`=success)
- ANSI color constants use Indonesian names
- Random Indonesian names are used for generated profiles (`namaDepan`/`namaBelakang`)
