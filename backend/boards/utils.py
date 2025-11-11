import hashlib
from datetime import datetime, timedelta
from mnemonic import Mnemonic

# BIP39 영어 단어 목록 (2048개)
mnemo = Mnemonic("english")
WORDLIST = mnemo.wordlist


def get_user_fingerprint(ip_address: str, timestamp: datetime = None) -> str:
    """
    IP 주소와 시간을 조합하여 BIP39 니모닉 단어 하나를 반환
    같은 시간대(1분 단위)에 같은 IP는 같은 단어를 받음
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    # 1분 단위로 반올림 (같은 분에는 같은 단어)
    time_key = timestamp.strftime('%Y%m%d%H%M')
    
    # IP + 시간 조합 해시
    combined = f"{ip_address}:{time_key}"
    hash_digest = hashlib.sha256(combined.encode()).digest()
    
    # 해시값을 숫자로 변환하여 2048로 나눈 나머지 → 단어 인덱스
    hash_int = int.from_bytes(hash_digest[:2], byteorder='big')
    word_index = hash_int % 2048
    
    return WORDLIST[word_index]


def check_rate_limit(fingerprint: str, cache) -> bool:
    """
    레이트 리밋 체크: 1분에 3개까지만 글 작성 가능
    """
    from django.conf import settings
    
    cache_key = f"rate_limit:{fingerprint}"
    count = cache.get(cache_key, 0)
    
    if count >= settings.RATE_LIMIT_MAX_POSTS:
        return False
    
    cache.set(cache_key, count + 1, settings.RATE_LIMIT_WINDOW)
    return True


def hash_password(password: str) -> str:
    """비밀번호 해시"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """비밀번호 검증"""
    return hash_password(password) == hashed
