function encryptCookie(value, secretKey) {
    return CryptoJS.AES.encrypt(value, secretKey).toString();
}

// 生成加密的Cookie
const secretKey = "7646cc99d133894ba5e532de2a93f352";
const cookieValue = 'asxe' + navigator.userAgent + secretKey;
const encryptedCookie = encryptCookie(cookieValue, secretKey);
document.cookie = `encrypted_cookie=${encryptedCookie}; path=/`;
