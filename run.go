package main

import (
	"bufio"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io"
	"math/rand"
	"net/http"
	"net/http/cookiejar"
	"net/url"
	"os"
	"os/signal"
	"regexp"
	"strings"
	"sync"
	"syscall"
	"time"
)

// ============================== WARNA ==============================

const (
	BIRU   = "\033[1;34m"
	KUNING = "\033[1;33m"
	MERAH  = "\033[1;31m"
	PUTIH  = "\033[1;37m"
	HIJAU  = "\033[1;32m"
	CYAN   = "\033[1;36m"
	UNGU   = "\033[1;35m"
	ABU    = "\033[0;90m"
	END    = "\033[0m"
)

// ============================== NICKNAME INDO ==============================

var namaDepan = []string{
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
	"Tara", "Umar", "Vino", "Wira", "Yogi", "Zara",
}

var namaBelakang = []string{
	"Pratama", "Saputra", "Wijaya", "Kusuma", "Putra", "Putri", "Sari",
	"Lestari", "Wati", "Ningsih", "Rahayu", "Cahyani", "Permana",
	"Nugraha", "Ramadhan", "Hidayat", "Firmansyah", "Setiawan", "Hakim",
	"Utama", "Santoso", "Wibowo", "Suryadi", "Purnama", "Handoko",
	"Prasetyo", "Gunawan", "Susanto", "Hartono", "Kurniawan", "Aditya",
	"Mahendra", "Anggara", "Perdana", "Pamungkas",
}

var akhiran = []string{
	"", "x", "z", "_", ".", "27", "12", "99", "88", "77", "01", "69",
	"ID", "id", "Jr", "jr", "v2", "XD", "xd", "gg", "GG", "YT", "yt",
}

func randomNickname() string {
	style := rand.Intn(4)
	switch style {
	case 0:
		return namaDepan[rand.Intn(len(namaDepan))] + " " + namaBelakang[rand.Intn(len(namaBelakang))]
	case 1:
		return fmt.Sprintf("%s%d", namaDepan[rand.Intn(len(namaDepan))], rand.Intn(999)+1)
	case 2:
		return namaDepan[rand.Intn(len(namaDepan))] + akhiran[rand.Intn(len(akhiran))]
	default:
		d := namaDepan[rand.Intn(len(namaDepan))]
		b := namaBelakang[rand.Intn(len(namaBelakang))]
		prefix := b
		if len(b) > 3 {
			prefix = b[:3]
		}
		return fmt.Sprintf("%s%s%d", d, prefix, rand.Intn(100))
	}
}

func randomString(length int) string {
	chars := "0123456789abcdefghijklmnopqrstuvwxyz"
	b := make([]byte, length)
	for i := range b {
		b[i] = chars[rand.Intn(len(chars))]
	}
	return string(b)
}

func log(color, msg string) {
	ts := time.Now().Format("15:04:05")
	fmt.Printf("%s[%s]%s %s%s%s\n", ABU, ts, END, color, msg, END)
}

// ============================== PROXY ==============================

type Proxy struct {
	URL *url.URL
	Raw string
	IP  string
}

func loadProxies(path string) []Proxy {
	file, err := os.Open(path)
	if err != nil {
		log(MERAH, fmt.Sprintf("File %s tidak ditemukan!", path))
		os.Exit(1)
	}
	defer file.Close()

	var proxies []Proxy
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}
		parts := strings.Split(line, ":")
		var proxyURL *url.URL
		var ip string
		if len(parts) == 4 {
			ip = parts[0]
			proxyURL, _ = url.Parse(fmt.Sprintf("http://%s:%s@%s:%s", parts[2], parts[3], parts[0], parts[1]))
		} else if len(parts) == 2 {
			ip = parts[0]
			proxyURL, _ = url.Parse(fmt.Sprintf("http://%s:%s", parts[0], parts[1]))
		} else {
			continue
		}
		if proxyURL != nil {
			proxies = append(proxies, Proxy{URL: proxyURL, Raw: line, IP: ip})
		}
	}
	log(PUTIH, fmt.Sprintf("Total proxy dimuat: %d", len(proxies)))
	return proxies
}

// ============================== HTTP CLIENT ==============================

func newClient(proxy *Proxy) *http.Client {
	transport := &http.Transport{
		TLSClientConfig:   &tls.Config{InsecureSkipVerify: true},
		DisableKeepAlives:  false,
		MaxIdleConns:       10,
		IdleConnTimeout:    30 * time.Second,
	}
	if proxy != nil {
		transport.Proxy = http.ProxyURL(proxy.URL)
	}
	jar, _ := cookiejar.New(nil)
	return &http.Client{
		Transport: transport,
		Timeout:   60 * time.Second,
		Jar:       jar,
	}
}

func newDirectClient() *http.Client {
	transport := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	jar, _ := cookiejar.New(nil)
	return &http.Client{
		Transport: transport,
		Timeout:   30 * time.Second,
		Jar:       jar,
	}
}

// ============================== ZEPETO API ==============================

type Zepeto struct {
	client    *http.Client
	authToken string
}

func newZepeto(proxy *Proxy) *Zepeto {
	return &Zepeto{client: newClient(proxy)}
}

func (z *Zepeto) headersToken() map[string]string {
	return map[string]string{
		"Host":           "gw-napi.zepeto.io",
		"X-Zepeto-Duid":  randomString(32),
		"User-Agent":     "Mozilla/5.0 (Windows 98; Win 9x 4.90) AppleWebKit/533.2 (KHTML, like Gecko) Chrome/80.0.4147.39 Safari/533.2 Edg/80.01080.48",
		"Content-Type":   "application/json; charset=utf-8",
	}
}

func (z *Zepeto) headersAuth() map[string]string {
	return map[string]string{
		"Host":           "gw-napi.zepeto.io",
		"Authorization":  "Bearer " + z.authToken,
		"X-Zepeto-Duid":  randomString(32),
		"User-Agent":     "android.zepeto_global/3.48.100 (android; U; Android OS 7.1.2 / API-25 (QKQ1.190825.002/G9550ZHU1AQEE); id-ID; occ-ID; asus ASUS_Z01QD)",
		"X-Timezone":     "Asia/Moscow",
		"Content-Type":   "application/json; charset=utf-8",
	}
}

func (z *Zepeto) post(endpoint string, data interface{}, headers map[string]string) map[string]interface{} {
	urlStr := "https://gw-napi.zepeto.io/" + endpoint
	body, _ := json.Marshal(data)

	for attempt := 0; attempt < 3; attempt++ {
		req, err := http.NewRequest("POST", urlStr, strings.NewReader(string(body)))
		if err != nil {
			return map[string]interface{}{}
		}
		for k, v := range headers {
			req.Header.Set(k, v)
		}

		resp, err := z.client.Do(req)
		if err != nil {
			if attempt < 2 {
				time.Sleep(3 * time.Second)
				continue
			}
			log(MERAH, fmt.Sprintf("Error [%s] setelah 3x retry", endpoint))
			return map[string]interface{}{}
		}
		defer resp.Body.Close()
		respBody, err := io.ReadAll(resp.Body)
		if err != nil {
			return map[string]interface{}{}
		}
		var result map[string]interface{}
		if err := json.Unmarshal(respBody, &result); err != nil {
			return map[string]interface{}{}
		}
		return result
	}
	return map[string]interface{}{}
}

func (z *Zepeto) postAuth(endpoint string, data interface{}) map[string]interface{} {
	return z.post(endpoint, data, z.headersAuth())
}

func (z *Zepeto) getToken() bool {
	result := z.post("DeviceAuthenticationRequest", map[string]string{"deviceId": randomString(32)}, z.headersToken())
	if token, ok := result["authToken"].(string); ok {
		z.authToken = token
		return true
	}
	return false
}

func (z *Zepeto) accusr() {
	z.postAuth("AccountUser_v5", map[string]interface{}{
		"creatorAllItemsVersion":  "_",
		"creatorHotItemGroupId":   "_",
		"creatorHotItemsVersion":  "_",
		"creatorNewItemsVersion":  "_",
		"params":                  map[string]string{"appVersion": "3.48.100", "itemVersion": "_", "language": "_", "platform": "_"},
		"timeZone":               "Asia/Moscow",
	})
}

func (z *Zepeto) agree1() { z.postAuth("SaveUserDataPolicyRequest", map[string]string{"country": "ru"}) }
func (z *Zepeto) agree2() { z.postAuth("GetUserAppProperty", map[string]string{"key": "agreeTermsDate"}) }
func (z *Zepeto) agree3() {
	z.postAuth("PutUserAppProperty", map[string]string{"key": "agreeTermsDate", "value": time.Now().Format(time.RFC3339)})
}

func (z *Zepeto) pushreg() {
	z.postAuth("PushRegistrationRequest", map[string]interface{}{
		"platform": "Android", "provider": "FCM",
		"pushId": "ejyrBwjWRU2XJjtJg-WXET:APA91bG-hocRcsgs6Nh9-aWKTeyKjR_djCrCJjlImGyn5Olz6l97gSKm7g8IaSKYQXYQSmfntIS32Ua1_ZGMukSSyldw-4Z_CB1fRrmpJHviUClHO9kTwFWABRk1qSMVnicbtctU81MU",
		"pushOn": true,
	})
}

func (z *Zepeto) char() {
	z.postAuth("CopyCharacterByHashcode", map[string]string{"hashCode": "ZPT115", "characterId": ""})
}

func (z *Zepeto) saveProfile(nickname string) {
	z.postAuth("SaveProfileRequest_v2", map[string]string{
		"job": "spy", "name": nickname, "nationality": "", "statusMessage": "nojalpro",
	})
}

func (z *Zepeto) follow() {
	z.postAuth("FollowRequest_v2", map[string]string{"followUserId": "65c62931734c7765c37aa8fc"})
}

func (z *Zepeto) emailVerifyRequest(email string) {
	z.postAuth("EmailVerificationRequest", map[string]string{"email": email})
}

func (z *Zepeto) emailConfirm(email, otp string) map[string]interface{} {
	return z.postAuth("EmailConfirmationRequest", map[string]string{"email": email, "verifyCode": otp})
}

func (z *Zepeto) register(email string) map[string]interface{} {
	return z.postAuth("UserRegisterRequest_v2", map[string]string{
		"userName": email, "displayName": email, "password": "zxcvbnm.",
	})
}

func (z *Zepeto) initZepetoID(zepetoID string) {
	z.postAuth("InitZepetoIdRequest", map[string]string{"zepetoId": zepetoID, "place": "signup"})
}

func (z *Zepeto) login(zepetoID string) {
	z.postAuth("AuthenticationRequest_v2", map[string]string{"userId": zepetoID, "password": "zxcvbnm."})
}

// ============================== FAKE EMAIL ==============================

type FakeEmail struct {
	client *http.Client
}

func newFakeEmail() *FakeEmail {
	return &FakeEmail{client: newDirectClient()}
}

var reEmail = regexp.MustCompile(`<span id="email_ch_text">([^<]+)</span>`)
var reOTP = regexp.MustCompile(`<span id="verificaiton-code-text"[^>]*>(\d+)</span>`)

func (f *FakeEmail) doGet(urlStr string) (string, error) {
	req, err := http.NewRequest("GET", urlStr, nil)
	if err != nil {
		return "", err
	}
	req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
	req.Header.Set("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5405.114 Safari/537.36")

	resp, err := f.client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}
	return string(body), nil
}

func (f *FakeEmail) getEmail() string {
	for attempt := 0; attempt < 3; attempt++ {
		html, err := f.doGet("https://email-fake.com/")
		if err != nil {
			if attempt < 2 {
				time.Sleep(2 * time.Second)
			}
			continue
		}
		matches := reEmail.FindStringSubmatch(html)
		if len(matches) > 1 {
			return matches[1]
		}
	}
	return ""
}

func (f *FakeEmail) getOTP(email string) string {
	html, err := f.doGet("https://email-fake.com/" + email)
	if err != nil {
		return ""
	}
	matches := reOTP.FindStringSubmatch(html)
	if len(matches) > 1 {
		return matches[1]
	}
	return ""
}

// ============================== CREATE ACCOUNT ==============================

var fileMu sync.Mutex

func createAccount(proxy Proxy, nomor int) bool {
	log(UNGU, fmt.Sprintf("[Akun #%d] Proxy: %s", nomor, proxy.IP))

	zep := newZepeto(&proxy)
	fem := newFakeEmail()

	// 1. Token
	if !zep.getToken() {
		log(MERAH, fmt.Sprintf("[Akun #%d] Gagal ambil token", nomor))
		return false
	}
	log(CYAN, fmt.Sprintf("[Akun #%d] Token OK", nomor))

	// 2. Fake email
	email := fem.getEmail()
	if email == "" {
		log(MERAH, fmt.Sprintf("[Akun #%d] Gagal ambil email", nomor))
		return false
	}
	log(PUTIH, fmt.Sprintf("[Akun #%d] Email: %s", nomor, email))

	// 3. Setup akun
	zep.accusr()
	zep.agree1()
	zep.agree2()
	zep.agree3()
	zep.pushreg()
	zep.char()

	nickname := randomNickname()
	zep.saveProfile(nickname)
	log(PUTIH, fmt.Sprintf("[Akun #%d] Nickname: %s", nomor, nickname))

	// 4. Email verification
	zep.emailVerifyRequest(email)
	log(KUNING, fmt.Sprintf("[Akun #%d] Menunggu OTP...", nomor))

	var otp string
	for attempt := 0; attempt < 5; attempt++ {
		time.Sleep(3 * time.Second)
		otp = fem.getOTP(email)
		if otp != "" {
			break
		}
		log(KUNING, fmt.Sprintf("[Akun #%d] Mengecek OTP... (%d/5)", nomor, attempt+1))
	}

	if otp == "" {
		log(MERAH, fmt.Sprintf("[Akun #%d] OTP tidak ditemukan", nomor))
		return false
	}

	confirm := zep.emailConfirm(email, otp)
	isSuccess, _ := confirm["isSuccess"]
	if isSuccess != true && isSuccess != float64(1) {
		log(MERAH, fmt.Sprintf("[Akun #%d] Verifikasi OTP gagal", nomor))
		return false
	}
	log(CYAN, fmt.Sprintf("[Akun #%d] OTP Berhasil: %s", nomor, otp))

	// 5. Register
	reg := zep.register(email)
	if s, ok := reg["isSuccess"]; !ok || (s != true && s != float64(1)) {
		log(MERAH, fmt.Sprintf("[Akun #%d] Register gagal", nomor))
		return false
	}

	// 6. Set Zepeto ID
	zepetoID := randomString(8)
	zep.initZepetoID(zepetoID)

	// 7. Login test
	zep.login(zepetoID)

	// 8. Follow
	zep.follow()

	// 9. Simpan
	fileMu.Lock()
	f, err := os.OpenFile("akun.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err == nil {
		fmt.Fprintf(f, "%s|Nojal3123\n", email)
		f.Close()
	}
	fileMu.Unlock()

	log(HIJAU, fmt.Sprintf("[Akun #%d] BERHASIL -> %s | Pass: Nojal3123 | Nick: %s", nomor, email, nickname))
	return true
}

// ============================== MAIN ==============================

func main() {
	rand.Seed(time.Now().UnixNano())

	// Handle CTRL+C
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
	go func() {
		<-sigCh
		fmt.Printf("\n%s[!] Dihentikan oleh user (CTRL+C)%s\n", KUNING, END)
		fmt.Printf("%s[*] Akun yang sudah dibuat tersimpan di akun.txt%s\n", PUTIH, END)
		os.Exit(0)
	}()

	fmt.Printf(`
%s╔══════════════════════════════════════════════╗
║      ZEPETO AUTO CREATE - Golang Edition     ║
║   Batch 10 Proxy | 1-2 Akun/Proxy | Proxy   ║
╚══════════════════════════════════════════════╝%s

`, CYAN, END)

	proxies := loadProxies("proxy.txt")
	if len(proxies) == 0 {
		log(MERAH, "Tidak ada proxy!")
		os.Exit(1)
	}

	// Hapus cookie lama
	os.Remove("cookie.txt")

	batchSize := 10
	totalAkun := 0
	batchNum := 0

	for i := 0; i < len(proxies); i += batchSize {
		end := i + batchSize
		if end > len(proxies) {
			end = len(proxies)
		}
		batch := proxies[i:end]
		batchNum++

		log(BIRU, strings.Repeat("=", 50))
		log(BIRU, fmt.Sprintf("BATCH #%d | Proxy %d-%d dari %d", batchNum, i+1, i+len(batch), len(proxies)))
		log(BIRU, strings.Repeat("=", 50))

		for j, proxy := range batch {
			jumlahAkun := rand.Intn(2) + 1
			log(UNGU, fmt.Sprintf("Proxy [%d/%d]: %s -> %d akun", j+1, len(batch), proxy.IP, jumlahAkun))

			for k := 0; k < jumlahAkun; k++ {
				totalAkun++
				success := createAccount(proxy, totalAkun)

				if !success {
					log(MERAH, "Gagal, lanjut...")
				}

				// Jeda antar akun: 3-5 menit
				if k < jumlahAkun-1 {
					jeda := rand.Intn(121) + 180
					log(KUNING, fmt.Sprintf("Jeda antar akun: %dm %ds", jeda/60, jeda%60))
					time.Sleep(time.Duration(jeda) * time.Second)
				}
			}

			// Jeda antar proxy: 30-60 detik
			if j < len(batch)-1 {
				jeda := rand.Intn(31) + 30
				log(ABU, fmt.Sprintf("Jeda antar proxy: %ds", jeda))
				time.Sleep(time.Duration(jeda) * time.Second)
			}
		}

		log(HIJAU, fmt.Sprintf("Batch #%d selesai | Total akun dibuat: %d", batchNum, totalAkun))

	}

	fmt.Println()
	log(HIJAU, fmt.Sprintf("SELESAI! Total akun dibuat: %d", totalAkun))
	log(PUTIH, "Akun tersimpan di akun.txt")
}
