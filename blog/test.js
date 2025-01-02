const secretKey = "7646cc99d133894ba5e532de2a93f352";

function encryptCookie(str) {
    var key = CryptoJS.enc.Utf8.parse(secretKey);
    var srcs = CryptoJS.enc.Utf8.parse(str);
    var encrypted = CryptoJS.AES.encrypt(srcs, key, {mode: CryptoJS.mode.ECB, padding: CryptoJS.pad.Pkcs7});
    return encrypted.toString();
}

setInterval(() => {
    var cookieValue = 'asxe' + navigator.userAgent + secretKey + Date.now();
    var encryptedCookie = encryptCookie(cookieValue);
    document.cookie = `encrypted_cookie=${encryptedCookie}; path=/`;
}, 1000);
