import base64
import hashlib
import hmac
import os
import random
import string
from datetime import timedelta

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
from django.core.cache import caches
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.utils import dateparse, timezone
from django.utils.deprecation import MiddlewareMixin

cache = caches['default']  # from django.core.cache import cache没有incr功能
geoip = GeoIP2(path='geoip', country='GeoLite2-Country.mmdb')  # 加载IP地理位置数据库
forbidden = '<div style="font-size:30px;">403 forbidden</div><div>%s</div>'


def insert_random_chars(input_str, num_insertions):
    random_chars = [random.choice(string.ascii_letters + string.digits) for _ in range(num_insertions)]
    str_list = list(input_str)
    for char in random_chars:
        insert_position = random.randint(0, len(str_list))  # 随机位置
        str_list.insert(insert_position, char)  # 在随机位置插入字符
    return ''.join(str_list)


def generate_random_number():
    return [random.randint(0, 1000) + i for i in range(1)]


def set_cookie_with_timestamp(response):
    secret_key = settings.SECRET_KEY
    timestamp = timezone.now().isoformat()
    expiry = timezone.now() + timedelta(minutes=1)  # cookie有效期

    # 生成cookie内容（时间戳和过期时间）
    cookie_value = f"{timestamp}|{expiry.isoformat()}"
    signature = hmac.new(secret_key.encode(), cookie_value.encode(), hashlib.sha256).hexdigest()
    cookie = cookie_value + '|' + signature
    signature_length = len(signature)
    response.set_cookie(f'timestamp_cookie66', cookie, expires=expiry)
    nums = generate_random_number()
    for i in nums:
        if i == 66:
            continue
        f_sig = insert_random_chars(signature, 20)
        f_cookie = cookie_value + '|' + f_sig[:signature_length]
        response.set_cookie(
            f'timestamp_cookie{i}',
            f_cookie,
            expires=expiry
        )


def validate_timestamp_cookie(request):
    timestamp_cookie = request.COOKIES.get('timestamp_cookie66')
    if not timestamp_cookie:
        return JsonResponse({'error': 'Missing cookie.'}, status=400)

    try:
        cookie_value, signature = timestamp_cookie.rsplit('|', 1)
        timestamp_str, expiry_str = cookie_value.split('|', 1)
        timestamp = dateparse.parse_datetime(timestamp_str)
        expiry = dateparse.parse_datetime(expiry_str)
    except ValueError:
        return JsonResponse({'error': 'Invalid cookie.'}, status=400)

    # 校验cookie是否过期
    if expiry < timezone.now():
        # 如果cookie过期，重新设置cookie并返回响应
        response = JsonResponse({'message': 'Cookie expired.'}, status=400)
        set_cookie_with_timestamp(response)
        return response

    # 校验时间戳是否在允许的范围内
    if abs((timezone.now() - timestamp).total_seconds()) > 60:  # 1分钟
        return JsonResponse({'error': 'Invalid cookie.'}, status=400)

    # 重新生成签名并校验
    secret_key = settings.SECRET_KEY
    expected_signature = hmac.new(secret_key.encode(), cookie_value.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        return JsonResponse({'error': 'Invalid signature.'}, status=400)
    return None


class ForbiddenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not settings.OPEN_FORBIDDEN:
            return
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))  # 获取访问者IP地址
        try:
            country = geoip.country(ip)['country_code']
            if country != 'CN':
                return HttpResponseForbidden(forbidden % 'Access is denied.')
        except:
            pass

    def process_response(self, request, response):
        if not settings.OPEN_FORBIDDEN:
            return response
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))  # 获取访问者IP地址
        try:
            user_tag = request.COOKIES.get(settings.CSRF_COOKIE_NAME)  # 从请求中获取cookie
            if not user_tag:
                user_tag = response.cookies[settings.CSRF_COOKIE_NAME].value  # 登陆时从响应中获取cookie
        except KeyError:
            user_tag = ip_address

        forbidden_ip_key = 'forbidden:ip:%s' % ip_address
        forbidden_user_key = 'forbidden:user:%s' % user_tag
        for cache_key in [forbidden_ip_key, forbidden_user_key]:  # 同时检查IP地址屏蔽和用户标记屏蔽
            forbidden_time = cache.get(cache_key)
            if forbidden_time:  # 如果被屏蔽了还继续请求
                cache.set(cache_key, forbidden_time, forbidden_time)  # 重置过期时间为初始值，延长屏蔽时间
                return HttpResponseForbidden(forbidden % '访问过于频繁，请稍候再试！')

        ip_count_key = 'count:ip:%s' % ip_address  # 同一IP地址的用户被屏蔽的次数
        user_count_key = 'count:user:%s:%s' % (user_tag, request.path)  # 同一用户在指定时间步长内的访问次数
        forbidden_user_count = settings.FORBIDDEN_USER_COUNT
        if 'HTTP_FILE_UPLOAD_NAME' in request.META:  # 文件传输的交互频率较高，频率限制调高5倍
            forbidden_user_count *= 5

        if cache.get(user_count_key, 0) > forbidden_user_count:  # 同一用户在指定时间步长内访问太多次
            forbidden_time = random.choice(
                range(settings.MIN_FORBIDDEN_TIME, settings.MAX_FORBIDDEN_TIME))  # 生成随机的屏蔽时间长度
            cache.set(forbidden_user_key, forbidden_time, forbidden_time)  # 设置屏蔽该用户
            try:
                cache.incr(ip_count_key)  # 该用户使用的IP被屏蔽的次数增加一次
            except ValueError:
                cache.set(ip_count_key, 1, settings.FORBIDDEN_IP_SECONDS)  # 还没有这个key的话设置为1
            return HttpResponseForbidden(forbidden % '访问过于频繁，请稍候再试！')
        elif cache.get(ip_count_key, 0) > settings.FORBIDDEN_IP_COUNT:  # 同一IP地址的用户被屏蔽三次后屏蔽该IP地址的访问
            forbidden_time = random.choice(
                range(settings.MIN_FORBIDDEN_TIME, settings.MAX_FORBIDDEN_TIME))  # 生成随机的屏蔽时间长度
            cache.set(forbidden_ip_key, forbidden_time, forbidden_time)  # 设置屏蔽该IP地址
            return HttpResponseForbidden(forbidden % '访问过于频繁，请稍候再试！')
        else:
            try:
                cache.incr(user_count_key)  # 该用户的访问次数增加一次
            except ValueError:
                cache.set(user_count_key, 1, settings.FORBIDDEN_USER_SECONDS)  # 还没有这个key的话设置为1
            return response


class SetTimestampCookieMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if 'timestamp_cookie66' not in request.COOKIES:
            set_cookie_with_timestamp(response)
        return response


class TimestampCookieValidationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        validation_response = validate_timestamp_cookie(request)
        if validation_response:
            return validation_response


def generate_encrypted_cookie(secret_key):
    cookie_value = os.urandom(16).hex()
    # 加密Cookie
    cipher = AES.new(secret_key.encode(), AES.MODE_ECB)
    encrypted_cookie = base64.b64encode(cipher.encrypt(pad(cookie_value.encode(), AES.block_size))).decode()
    return encrypted_cookie, cookie_value


class CookieEncryptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.secret_key = "7646cc99d133894ba5e532de2a93f352"

    def __call__(self, request):
        encrypted_cookie = request.COOKIES.get('encrypted_cookie')

        if not encrypted_cookie:
            # 首次请求，生成加密Cookie并返回
            encrypted_cookie, cookie_value = generate_encrypted_cookie(self.secret_key)
            response = self.get_response(request)
            response.set_cookie('encrypted_cookie', encrypted_cookie)
            return response
        else:
            if len(encrypted_cookie) < 256:
                return HttpResponseForbidden("Invalid encrypted cookie")
            request.decrypted_cookie = encrypted_cookie
            response = self.get_response(request)
            return response
