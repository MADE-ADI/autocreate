<?php
// error_reporting(0);
// warna

$biru = "\033[1;34m";
$kuning = "\033[1;33m";
$merah = "\033[1;31m";
$putih = "\033[1;37m";
$hijau = "\033[1;32m";
$cyan = "\033[1;36m";
$ungu = "\033[1;35m";
$dark = "\033[1;30m";
$abu = "\033[0;90m";
$abu1 = "\033[1;90m";
$merah1 = "\033[1;91m";
$end = "\033[0m";
$blockabu = "\033[100m";
$blockmerah = "\033[101m";
$blockstabilo = "\033[102m";
$blockkuning = "\033[103m";
$blockbiru = "\033[104m";
$blockpink = "\033[105m";
$blockcyan = "\033[106m";
$blockputih = "\033[107m";
$uhijau = "\033[4;32m";
$umerah = "\033[4;31m";
$uyellow = "\033[4;33m";
$uputih = "\033[4;37m";
$ubiru = "\033[4;34m";
$uungu = "\033[4;35m";
$ucyan = "\033[4;36m";
$uhitam = "\033[4;30m";


function slow($str)
{
    $arr = str_split($str);
    foreach ($arr as $az) {
        echo $az;
        usleep(3);
    }
}

function fast($str)
{
    $arr = str_split($str);
    foreach ($arr as $az) {
        echo $az;
        usleep(30);
    }
}

####################################################################################################
// CURL
####################################################################################################


class curls
{
    public static function curl(
        $url = 0,
        $httpheader = 0,
        $post = 0,
        $request = 0,
        $proxy = 0
    ) {
        $curl = curl_init();
        curl_setopt_array(
            $curl,
            array(
                CURLOPT_URL => $url,
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_FOLLOWLOCATION => true,
                CURLOPT_SSL_VERIFYPEER => false,
                CURLOPT_SSL_VERIFYHOST => false,
                CURLOPT_CONNECTTIMEOUT => 30,
                CURLOPT_TIMEOUT => 60,
                CURLOPT_MAXREDIRS => 10,
                CURLOPT_AUTOREFERER => true,
                CURLOPT_ENCODING => "",
                CURLOPT_COOKIEJAR => "cookie.txt",
                CURLOPT_COOKIEFILE => "cookie.txt",
                CURLOPT_HEADER => true
            )
        );
        if ($httpheader) {
            curl_setopt($curl, CURLOPT_HTTPHEADER, $httpheader);
        }
        if ($post) {
            curl_setopt_array(
                $curl,
                array(
                    CURLOPT_POST => true,
                    CURLOPT_POSTFIELDS => $post
                )
            );
        }
        if ($request) {
            curl_setopt($curl, CURLOPT_CUSTOMREQUEST, $request);
        }
        if ($proxy) {
            curl_setopt_array(
                $curl,
                array(
                    CURLOPT_HTTPPROXYTUNNEL => true,
                    CURLOPT_PROXY => $proxy,
                    CURLOPT_PROXYTYPE => CURLPROXY_SOCKS5
                )
            );
        }
        $response = curl_exec($curl);
        $httpcode = curl_getinfo($curl);
        $header = substr($response, 0, curl_getinfo($curl, CURLINFO_HEADER_SIZE));
        $body = substr($response, curl_getinfo($curl, CURLINFO_HEADER_SIZE));
        curl_close($curl);
        return array($header, $body);
    }

}

####################################################################################################
// TOKEN
####################################################################################################


class token extends curls
{
    public static function randoms($length = 10)
    {
        $characters = '0123456789abcdefghijklmnopqrstuvwxyz';
        $charactersLength = strlen($characters);
        $randomString = '';
        for ($i = 0; $i < $length; $i++) {
            $randomString .= $characters[rand(0, $charactersLength - 1)];
        }
        return $randomString;
    }

    public static function token()
    {
        $header = array(
            "Host: gw-napi.zepeto.io",
            "X-Zepeto-Duid: " . self::randoms(32),
            "User-Agent: Mozilla/5.0 (Windows 98; Win 9x 4.90) AppleWebKit/533.2 (KHTML, like Gecko) Chrome/80.0.4147.39 Safari/533.2 Edg/80.01080.48",
            "Content-Type: application/json; charset=utf-8"
        );
        $url = "https://gw-napi.zepeto.io/DeviceAuthenticationRequest";
        $data = json_encode(["deviceId" => self::randoms(32)]);
        return json_decode(self::curl($url, $header, $data)[1], 1);
    }
}

####################################################################################################
// LOGIN
####################################################################################################

function headers()
{
    global $auth;
    $header = array(
        "Host: gw-napi.zepeto.io",
        "Authorization: Bearer {$auth}",
        "X-Zepeto-Duid: " . token::randoms(32),
      "User-Agent: android.zepeto_global/3.48.100 (android; U; Android OS 7.1.2 / API-25 (QKQ1.190825.002/G9550ZHU1AQEE); id-ID; occ-ID; asus ASUS_Z01QD)",
        "X-Timezone: Asia/Moscow",
        "Content-Type: application/json; charset=utf-8"
    );
    return $header;
}

function loginemail()
{
    global $email, $pass;

    $url = "https://gw-napi.zepeto.io/AuthenticationRequest_v2";
    $data = json_encode(["userId" => "$email", "password" => "$pass"]);
    return json_decode(curls::curl($url, headers(), $data)[1], 1);
}

function search($searchnama)
{
    $url = "https://gw-napi.zepeto.io/FriendNicknameSearchWithFeedInfo";
    $data = json_encode(["cursor" => "0", "keyword" => $searchnama, "size" => 30, "place" => "home"]);
    return json_decode(curls::curl($url, headers(), $data)[1], 1);
}

function user($id)
{
    $url = "https://gw-napi.zepeto.io/UserVisitRequest_v2";
    $data = json_encode(["visitUserId" => $id, "resolve" => true]);
    return json_decode(curls::curl($url, headers(), $data)[1], 1);
}

function questlist($questcode)
{
  $url = "https://gw-napi.zepeto.io/QuestListRequest_v2";
  $data = json_encode(["questId" => "$questcode"]);
  return json_decode(curls::curl($url, headers1(), $data)[1], 1);
}

function questrun($questcode)
{
  $url = "https://gw-napi.zepeto.io/ActionRequest_v3";
  $data = json_encode(["actionCodes" => ["$questcode"]]);
  return json_decode(curls::curl($url, headers1(), $data)[1], 1);
}

function questclaim($questcode)
{
  $url = "https://gw-napi.zepeto.io/QuestRewardReceiveRequest_v2";
  $data = json_encode(["questId" => "$questcode"]);
  return json_decode(curls::curl($url, headers1(), $data)[1], 1);
}

function questfinalclaim()
{
  $url = "https://gw-napi.zepeto.io/QuestFinalRewardReceiveRequest_v2";
  $data = json_encode([]);
  return json_decode(curls::curl($url, headers1(), $data)[1], 1);
}

function questmiddleclaim()
{
  $url = "https://gw-napi.zepeto.io/QuestMiddleRewardReceiveRequest_v2";
  $data = json_encode([]);
  return json_decode(curls::curl($url, headers1(), $data)[1], 1);
}

function questwait($questcode)
{
  $url = "https://gw-napi.zepeto.io/WaitTimeQuestStartRequest_v2";
  $data = json_encode(["questId" => "$questcode"]);
  return json_decode(curls::curl($url, headers1(), $data)[1], 1);
}


####################################################################################################
// REGIST
####################################################################################################

class reg extends curls
{

     public static function follow()
    {

        $url = "https://gw-napi.zepeto.io/FollowRequest_v2";
        $data = json_encode(["followUserId" => "65c62931734c7765c37aa8fc"]);
        return json_decode(self::curl($url, headers(), $data)[1], 1);
    }


    public static function accusr()
    {

        $url = "https://gw-napi.zepeto.io/AccountUser_v5";
        $data = json_encode(["creatorAllItemsVersion" => "_", "creatorHotItemGroupId" => "_", "creatorHotItemsVersion" => "_", "creatorNewItemsVersion" => "_", "params" => ["appVersion" => "3.48.100", "itemVersion" => "_", "language" => "_", "platform" => "_"], "timeZone" => "Asia/Moscow"]);
        return json_decode(self::curl($url, headers(), $data)[1], 1);
    }

    public static function save()
    {

        $url = "https://gw-napi.zepeto.io/SaveProfileRequest_v2";
        $data = json_encode(["job" => "spy", "name" => "NOJAL 🔥", "nationality" => "", "statusMessage" => "uhuyy"]);
        return json_decode(self::curl($url, headers(), $data)[1], 1);
    }

    public static function agree1()
    {
        $url = "https://gw-napi.zepeto.io/SaveUserDataPolicyRequest";
        $data = json_encode(["country" => "ru"]);
        return json_decode(self::curl($url, headers(), $data)[1], 1);
    }

    public static function agree2()
    {
        $url = "https://gw-napi.zepeto.io/GetUserAppProperty";
        $data = json_encode(["key" => "agreeTermsDate"]);
        return json_decode(self::curl($url, headers(), $data)[1], 1);
    }

    public static function agree3()
    {
        $url = "https://gw-napi.zepeto.io/PutUserAppProperty";
        $data = json_encode(["key" => "agreeTermsDate", "value" => date("c")]);
        return json_decode(self::curl($url, headers(), $data)[1], 1);
    }

    public static function pushreg()
    {
        $url = "https://gw-napi.zepeto.io/PushRegistrationRequest";
        $data = json_encode(["platform" => "Android", "provider" => "FCM", "pushId" => "ejyrBwjWRU2XJjtJg-WXET:APA91bG-hocRcsgs6Nh9-aWKTeyKjR_djCrCJjlImGyn5Olz6l97gSKm7g8IaSKYQXYQSmfntIS32Ua1_ZGMukSSyldw-4Z_CB1fRrmpJHviUClHO9kTwFWABRk1qSMVnicbtctU81MU", "pushOn" => true]);
        return json_decode(self::curl($url, headers(), $data)[1], 1);
    }

    public static function char()
    {
        $url = "https://gw-napi.zepeto.io/CopyCharacterByHashcode";
        $data = json_encode(["hashCode" => "ZPT115", "characterId" => ""]);
        return json_decode(self::curl($url, headers(), $data)[1], 1);
    }

    public static function email1()
    {
        global $email;
        $url = "https://gw-napi.zepeto.io/EmailVerificationRequest";
        $data = json_encode(["email" => $email]);
        return json_decode(self::curl($url, headers(), $data)[1], 1);
    }

    public static function email2()
    {
        global $otp, $email;
        $url = "https://gw-napi.zepeto.io/EmailConfirmationRequest";
        $data = json_encode(["email" => $email, "verifyCode" => $otp]);
        return json_decode(self::curl($url, headers(), $data)[1], 1);
    }

    public static function reqname($requestname)
    {
        global $r;
        $url = "https://gw-napi.zepeto.io/RecommendZepetoIdRequest";
        $data = json_encode(["zepetoId" => $requestname . $r]);
        return json_decode(self::curl($url, headers(), $data)[1], 1);
    }

    public static function validname()
    {
        global $rek;
        $url = "https://gw-napi.zepeto.io/ValidateZepetoIdRequest";
        $data = json_encode(["zepetoId" => $rek]);
        return json_decode(self::curl($url, headers(), $data)[1], 1);
    }

    public static function tahap1($email)
    {
        global $email;
        $url = "https://gw-napi.zepeto.io/UserRegisterRequest_v2";
        $data = json_encode(["userName" => $email, "displayName" => $email, "password" => "$email"]);
        return json_decode(self::curl($url, headers(), $data)[1], 1);
    }

    public static function tahap2()
    {
        global $rek;
        $url = "https://gw-napi.zepeto.io/InitZepetoIdRequest";
        $data = json_encode(["zepetoId" => $rek, "place" => "signup"]);
        return json_decode(self::curl($url, headers(), $data)[1], 1);
    }

    public static function tahap3()
    {
        global $rek, $email;
        $url = "https://gw-napi.zepeto.io/AuthenticationRequest_v2";
        $data = json_encode(["userId" => $rek, "password" => $email]);
        return json_decode(self::curl($url, headers(), $data)[1], 1);
    }
}


####################################################################################################
// GENERATED EMAIL
####################################################################################################

class email extends curls
{
    public static function getemail1()
    {
        $header = array(
            "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5405.114 Safari/537.36"
        );
        $url = "https://email-fake.com/";
        return self::curl($url, $header)[1];
    }

    public static function getemail2($email)
    {
        $header = array(
            "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5405.114 Safari/537.36"
        );
        $url = "https://email-fake.com/{$email}";
        return self::curl($url, $header)[1];
    }

    public static function getemail3()
    {
        $header = array(
            "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5405.114 Safari/537.36"
        );
        $url = "https://email-fake.com/inbox2";
        return self::curl($url, $header)[1];
    }
}

c:
if (file_exists("cookie.txt")) {
    unlink("cookie.txt");
}

echo $putih . "> Beberapa Akun Sedang Dibuat : ";

$targetAkun = 1000000;
$akunSudahDibuat = 0;

while ($akunSudahDibuat < $targetAkun) {
    echo str_repeat($putih . "~", 50) . "\n";
    $auth = token::token()["authToken"];
    $getemail1 = email::getemail1();
    $email = explode('</span>', explode('<span id="email_ch_text">', $getemail1)[1])[0];

    $accusr = reg::accusr();
    $agree1 = reg::agree1();
    $agree2 = reg::agree2();
    $agree3 = reg::agree3();
    $push = reg::pushreg();
    $char = reg::char();
    $save = reg::save();
    $email1 = reg::email1();
    echo ($putih . "Mengecek OTP .   \r");
    sleep(1);
    echo ("Mengecek OTP ..  \r");
    sleep(1);
    echo ("Mengecek OTP ... \r");
    sleep(1);
    $getemail2 = email::getemail2($email);
    $otp=explode('</span>',explode('<span id="verificaiton-code-text" style="display: block; font-weight: 700; font-size: 44px; line-height: 48px; color: #292930; text-align: center; letter-spacing: 8px">',$getemail2)[1])[0];
    if ($otp) {
        $email2 = reg::email2();
        $con = $email2["isSuccess"];
        if ($con == '1') {
            echo ($cyan . "Kode Verifikasi Berhasil Di Terima √\n");
        }
    } else {
        echo $merah . "Silakan Jalankan Ulang! !\n";
        goto c; 
    }


    $tahap1 = reg::tahap1($email)["isSuccess"];
    $tahap2 = reg::tahap2()["isSuccess"];
    $tahap3 = reg::tahap3();

    if ($tahap1) {
        echo $hijau . "Akun Baru [ Email : {$email} ]\n";
        $file = fopen("akun.txt", "a");
        fwrite($file, "{$email}\n");
        fclose($file);
        $akunSudahDibuat++;
    } elseif (!$tahap1) {
        echo $merah . "Password Tidak Bisa Digunakan, Harap Masukkan Password yang Kuat !\n";
    } else {
        echo $merah . "Silakan Jalankan Ulang!.\n";
        goto c;
    }

    if (file_exists("cookie.txt")) {
        unlink("cookie.txt");
    }
 }

echo $putih . "> Note :\n";
echo "> Akun Tersimpan Di akun.txt, Buka File akun.txt jika ingin melihat akun2 yg sudah di buat\n";

