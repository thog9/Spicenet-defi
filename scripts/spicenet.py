import os
import sys
import asyncio
import json
import base64
from typing import List
from colorama import init, Fore, Style
import aiohttp
from aiohttp_socks import ProxyConnector
import inquirer
from datetime import datetime, UTC

# Initialize colorama
init(autoreset=True)

# Border width
BORDER_WIDTH = 80

# API URLs
API_BASE_URL = "https://portal-api.spicenet.io/api/v1/challenges"
TASKS_STATUS_URL = f"{API_BASE_URL}/spicenet/tasks-status/1"
DO_TASK_URL = f"{API_BASE_URL}/do-task"
IP_CHECK_URL = "https://api.ipify.org?format=json"
USER_INFO_URL = "https://portal-api.spicenet.io/api/v1/social-pay/me"

# Headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    "Content-Type": "application/json",
    "Origin": "https://portal.spicenet.io",
    "Referer": "https://portal.spicenet.io/",
    "Sec-Ch-Ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "privy-app-id": "cmdonap9700d3ky0jcrppiz4x",
    "privy-ca-id": "910fb1a5-d513-4685-ad17-2276aadf1f78",
    "privy-client": "react-auth:3.0.1"
}

# Configuration
CONFIG = {
    "DELAY_BETWEEN_ACCOUNTS": 5,
    "RETRY_ATTEMPTS": 3,
    "RETRY_DELAY": 3,
    "THREADS": 2,
    "TIMEOUT": 30
}

# Task types
TASK_TYPES = {
    "Daily challenge": ["df80b9eb-46c6-4ac1-b3ee-8d5a50612a6b"],
    "Required Quest": ["a6911f42-bc6c-4324-ae0a-c25d3211f85f"],
    "Spread the word": [
        "66360446-2763-44ee-949b-cf83fc553b4f",
        "ded28535-6777-4607-9413-7122acbaabb4",
        "984b1256-b7c1-41b2-9fb0-5b544532ca4c",
        "5ec71d23-a7b9-4148-b2f5-82d320785b56",
        "5472f07b-53f9-471d-8d3d-b42960a35030",
        "9464ec37-9783-4e36-88d6-ce1ae224e955",
        "5c25cb4d-8097-4c3d-a982-ed7d6eec9f83",
        "a839aece-cd91-40bd-85ed-37824fa1a268",
        "6d125211-b78f-4165-90fb-22f0452f90ab",
        "43d12400-5bcc-4a5c-b89a-b6b95c94a525",
        "c44f04cc-540b-42e2-87f3-344e9a6b5c9f",
        "2b829887-7c7a-4466-9457-64174b1254a6",
        "72f962ea-326c-420f-b94a-6e1951d02eab",
        "a839aece-cd91-40bd-85ed-37824fa1a268",
        "5c25cb4d-8097-4c3d-a982-ed7d6eec9f83"
    ],
    "Create spicy content": [
        "1f8cd410-bedf-41c5-a2c2-fd007dfe9d78",
        "5dfd163c-9e63-4e80-ab92-ea0ac284557e",
        "8a25aa3f-fc90-4f4e-bc4b-5f6919febbad"
    ]
}

# Bilingual vocabulary
LANG = {
    'vi': {
        'title': 'TỰ ĐỘNG HOÀN THÀNH NHIỆM VỤ - SPICENET DEFI',
        'info': 'Thông tin',
        'no_proxies': 'Không tìm thấy proxy trong proxies.txt',
        'using_proxy': 'Sử dụng Proxy - [{proxy}] với IP công khai - [{public_ip}]',
        'no_proxy': 'Không có proxy',
        'unknown': 'Không xác định',
        'invalid_proxy': 'Proxy không hợp lệ hoặc không hoạt động: {proxy}',
        'ip_check_failed': 'Không thể kiểm tra IP công khai: {error}',
        'processing_wallets': 'ĐANG XỬ LÝ VÍ {index}/{total}',
        'loading_token': 'Đang tải token: {token}',
        'login_success': 'Đăng nhập thành công! userId: {userId}',
        'wallet_address': 'Địa chỉ ví: {address}',
        'user_info': 'Name: {name} | Username: {username}',
        'location': 'Location: {location}',
        'token_display': 'Token: {token}',
        'completing_task': 'Đang hoàn thành nhiệm vụ: {task}',
        'task_success': 'Hoàn thành nhiệm vụ!',
        'task_completed': 'Task {task}',
        'task_status': 'Nhiệm vụ: Đã hoàn thành',
        'task_guid': 'IDGuid: {guid}',
        'task_points': 'Points: + {points} điểm',
        'task_failure': 'Thất bại khi hoàn thành nhiệm vụ {task}: {error}',
        'pausing': 'Tạm dừng',
        'seconds': 'giây',
        'completed': 'HOÀN THÀNH: {successful}/{total} HOÀN THÀNH NHIỆM VỤ',
        'error': 'Lỗi',
        'no_tokens': 'Không tìm thấy token trong token.txt',
        'select_task_type': 'Chọn loại nhiệm vụ để thực hiện',
        'menu_title': 'MENU CHÍNH - SPICENET TASKS (TOKEN)',
        'locked': 'Nhiệm vụ này bị khóa hoặc không khả dụng!',
        'token_expired': 'Token đã hết hạn tại {expires_at}. Vui lòng tạo token mới!',
        'token_valid': 'Token hợp lệ đến {time}',
        'press_enter': 'Nhấn Enter để tiếp tục...'
    },
    'en': {
        'title': 'AUTOMATIC TASK COMPLETION - SPICENET DEFI',
        'info': 'Information',
        'no_proxies': 'No proxies found in proxies.txt',
        'using_proxy': 'Using Proxy - [{proxy}] with public IP - [{public_ip}]',
        'no_proxy': 'No proxy',
        'unknown': 'Unknown',
        'invalid_proxy': 'Invalid or non-working proxy: {proxy}',
        'ip_check_failed': 'Unable to check public IP: {error}',
        'processing_wallets': 'PROCESSING WALLET {index}/{total}',
        'loading_token': 'Loading token: {token}',
        'login_success': 'Login successful! userId: {userId}',
        'wallet_address': 'Wallet address: {address}',
        'user_info': 'Name: {name} | Username: {username}',
        'location': 'Location: {location}',
        'token_display': 'Token: {token}',
        'completing_task': 'Completing task: {task}',
        'task_success': 'Task completed!',
        'task_completed': 'Task {task}',
        'task_status': 'Status: Already completed',
        'task_guid': 'IDGuid: {guid}',
        'task_points': 'Points: + {points} points',
        'task_failure': 'Failed to complete task {task}: {error}',
        'pausing': 'Pausing',
        'seconds': 'seconds',
        'completed': 'COMPLETED: {successful}/{total} TASK COMPLETION',
        'error': 'Error',
        'no_tokens': 'No tokens found in token.txt',
        'select_task_type': 'Select task type to execute',
        'menu_title': 'MAIN MENU - SPICENET TASKS (TOKEN)',
        'locked': 'This task is locked or unavailable!',
        'token_expired': 'Token expired at {expires_at}. Please generate a new token!',
        'token_valid': 'Token valid until {time}',
        'press_enter': 'Press Enter to continue...'
    }
}

# Display functions
def print_border(text: str, color=Fore.CYAN, width=BORDER_WIDTH):
    text = text.strip()
    if len(text) > width - 4:
        text = text[:width - 7] + "..."
    padded_text = f" {text} ".center(width - 2)
    print(f"{color}┌{'─' * (width - 2)}┐{Style.RESET_ALL}")
    print(f"{color}│{padded_text}│{Style.RESET_ALL}")
    print(f"{color}└{'─' * (width - 2)}┘{Style.RESET_ALL}")

def print_message(message: str, color=Fore.YELLOW):
    print(f"{color}{message}{Style.RESET_ALL}")

# Utility functions
def load_proxies(file_path: str = "proxies.txt", language: str = 'vi'):
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW} {LANG[language]['no_proxies']}. Using no proxy.{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add proxies here, one per line\n# Example: socks5://user:pass@host:port or http://host:port\n")
            return []
        
        proxies = []
        with open(file_path, 'r') as f:
            for line in f:
                proxy = line.strip()
                if proxy and not proxy.startswith('#'):
                    proxies.append(proxy)
        
        if not proxies:
            print(f"{Fore.YELLOW} {LANG[language]['no_proxies']}. Using no proxy.{Style.RESET_ALL}")
            return []
        
        return proxies
    except Exception as e:
        print(f"{Fore.RED} {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return []

def load_tokens(file_path: str = "token.txt", language: str = 'vi') -> List[str]:
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.YELLOW} {LANG[language]['no_tokens']}. Creating new file.{Style.RESET_ALL}")
            with open(file_path, 'w') as f:
                f.write("# Add tokens here, one per line\n# Example: eyJhbGciOiJ...\n")
            return []
        
        tokens = []
        with open(file_path, 'r') as f:
            for line in f:
                token = line.strip()
                if token and not token.startswith('#'):
                    tokens.append(token)
        
        if not tokens:
            print(f"{Fore.RED} {LANG[language]['no_tokens']}{Style.RESET_ALL}")
            sys.exit(1)
        
        return tokens
    except Exception as e:
        print(f"{Fore.RED} {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return []

async def get_proxy_ip(proxy: str = None, language: str = 'vi') -> str:
    try:
        connector = ProxyConnector.from_url(proxy) if proxy else None
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])) as session:
            async with session.get(IP_CHECK_URL, headers=HEADERS) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('ip', LANG[language]['unknown'])
                print(f"{Fore.YELLOW} {LANG[language]['ip_check_failed'].format(error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                return LANG[language]['unknown']
    except Exception as e:
        print(f"{Fore.YELLOW} {LANG[language]['ip_check_failed'].format(error=str(e))}{Style.RESET_ALL}")
        return LANG[language]['unknown']

async def get_user_info(token: str, language: str = 'vi', proxy: str = None) -> dict:
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    for attempt in range(CONFIG['RETRY_ATTEMPTS']):
        try:
            connector = ProxyConnector.from_url(proxy) if proxy else None
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])) as session:
                async with session.get(USER_INFO_URL, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    print(f"{Fore.RED} {LANG[language]['error']}: Failed to fetch user info (HTTP {response.status}){Style.RESET_ALL}")
                    return {}
        except Exception as e:
            if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                await asyncio.sleep(CONFIG['RETRY_DELAY'])
                continue
            print(f"{Fore.RED} {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
            return {}
    return {}

async def complete_task(token: str, task_guid: str, task_name: str, points: str, language: str = 'vi', proxy: str = None) -> bool:
    print(f"{Fore.CYAN} > {LANG[language]['completing_task'].format(task=task_name)}{Style.RESET_ALL}")
    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    payload = {"taskGuid": task_guid, "extraArguments": []}
    
    for attempt in range(CONFIG['RETRY_ATTEMPTS']):
        try:
            connector = ProxyConnector.from_url(proxy) if proxy else None
            async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])) as session:
                async with session.post(DO_TASK_URL, headers=headers, json=payload) as response:
                    if response.status == 201:
                        data = await response.json()
                        if data.get("status"):
                            print(f"{Fore.GREEN} {LANG[language]['task_success']}{Style.RESET_ALL}")
                            print(f"    - {LANG[language]['task_guid'].format(guid=task_guid)}")
                            print(f"    - {LANG[language]['task_points'].format(points=points)}")
                            return True
                        print(f"{Fore.RED} {LANG[language]['task_failure'].format(task=task_name, error='Task not successful')}{Style.RESET_ALL}")
                        return False
                    print(f"{Fore.RED} {LANG[language]['task_failure'].format(task=task_name, error=f'HTTP {response.status}')}{Style.RESET_ALL}")
                    return False
        except Exception as e:
            if attempt < CONFIG['RETRY_ATTEMPTS'] - 1:
                await asyncio.sleep(CONFIG['RETRY_DELAY'])
                continue
            print(f"{Fore.RED} {LANG[language]['task_failure'].format(task=task_name, error=str(e))}{Style.RESET_ALL}")
            return False
    return False

def is_token_expired(token: str, language: str = 'vi') -> tuple[bool, str]:
    try:
        payload = token.split('.')[1]
        payload += '=' * (-len(payload) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(payload).decode())
        exp = decoded.get('exp')
        if not exp:
            return False, "Không tìm thấy thời gian hết hạn"
        
        exp_dt = datetime.fromtimestamp(exp, UTC)
        now_dt = datetime.now(UTC)
        
        if now_dt > exp_dt:
            return True, exp_dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        else:
            return False, exp_dt.strftime('%H:%M:%S UTC')
    except Exception as e:
        return False, f"Không thể decode token: {str(e)}"

async def process_token(index: int, token: str, task_type: str, language: str = 'vi', proxies: List[str] = None) -> bool:
    total_tokens = len(load_tokens())
    proxy = proxies[index % len(proxies)] if proxies else None
    print_border(f"ĐANG XỬ LÝ VÍ {index + 1}/{total_tokens}", Fore.YELLOW)
    
    print(f"{Fore.CYAN} > {LANG[language]['loading_token'].format(token=token[:10] + '...' + token[-10:])}{Style.RESET_ALL}")
    
    # Kiểm tra token hết hạn qua JWT
    expired, exp_info = is_token_expired(token, language)
    if expired:
        print(f"{Fore.YELLOW} {LANG[language]['token_expired'].format(expires_at=exp_info)}{Style.RESET_ALL}")
        return False
    else:
        print(f"{Fore.CYAN} {LANG[language]['token_valid'].format(time=exp_info)}{Style.RESET_ALL}")

    public_ip = await get_proxy_ip(proxy, language)
    proxy_display = proxy if proxy else LANG[language]['no_proxy']
    print(f"{Fore.CYAN} {LANG[language]['using_proxy'].format(proxy=proxy_display, public_ip=public_ip)}{Style.RESET_ALL}")

    user_info = await get_user_info(token, language, proxy)
    if not user_info:
        print(f"{Fore.RED} {LANG[language]['error']}: Unable to fetch user info{Style.RESET_ALL}")
        return False

    user_id = user_info.get("twitterMetadata", {}).get("userId", user_info.get("id", "Unknown"))
    print(f"{Fore.GREEN} > {LANG[language]['login_success'].format(userId=user_id)}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}    - {LANG[language]['wallet_address'].format(address=user_info.get('walletAddress', 'Unknown'))}")
    
    twitter = user_info.get("twitterMetadata", {})
    if twitter:
        print(f"{Fore.YELLOW}    - {LANG[language]['user_info'].format(name=twitter.get('name', 'N/A'), username=twitter.get('username', 'N/A'))}")
        print(f"{Fore.YELLOW}    - {LANG[language]['location'].format(location=twitter.get('location', 'N/A'))}")

    tasks_to_complete = []
    if task_type == "All Tasks":
        tasks_to_complete.extend(TASK_TYPES["Required Quest"])
        tasks_to_complete.extend(TASK_TYPES["Spread the word"])
        tasks_to_complete.extend(TASK_TYPES["Create spicy content"])
        tasks_to_complete.extend(TASK_TYPES["Daily challenge"])
    else:
        if task_type in ["Spread the word", "Create spicy content"]:
            tasks_to_complete.extend(TASK_TYPES["Required Quest"])
        tasks_to_complete.extend(TASK_TYPES[task_type])

    headers = {**HEADERS, "Authorization": f"Bearer {token}"}
    try:
        connector = ProxyConnector.from_url(proxy) if proxy else None
        async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=CONFIG['TIMEOUT'])) as session:
            async with session.get(TASKS_STATUS_URL, headers=headers) as response:
                if response.status in [200, 304]:
                    data = await response.json()
                    tasks_status = {task["taskGuid"]: task for task in data.get("tasksStatus", [])}
                else:
                    print(f"{Fore.RED} {LANG[language]['error']}: Failed to fetch task status (HTTP {response.status}){Style.RESET_ALL}")
                    return False
    except Exception as e:
        print(f"{Fore.RED} {LANG[language]['error']}: {str(e)}{Style.RESET_ALL}")
        return False

    for task_guid in tasks_to_complete:
        task_info = tasks_status.get(task_guid, {})
        if not task_info.get("isEnabled", False):
            print(f"{Fore.YELLOW} {LANG[language]['locked']}{Style.RESET_ALL}")
            continue
        if task_info.get("pointsReceived", "0") != "0" or task_info.get("title", "") == "Follow Spicenet on X":
            print(f"{Fore.GREEN} {LANG[language]['task_completed'].format(task=task_info.get('title', task_guid))}")
            print(f"{Fore.YELLOW}   - {LANG[language]['task_status']}")
            continue
        task_name = task_info.get("title", task_guid)
        if await complete_task(token, task_guid, task_name, task_info.get("maxPoints", "0"), language, proxy):
            await asyncio.sleep(1)  

    return True

async def run_spicenet(task_type: str, language: str = 'vi'):
    print()
    print_border(LANG[language]['title'], Fore.CYAN)
    print()

    proxies = load_proxies('proxies.txt', language)
    print()

    tokens = load_tokens('token.txt', language)
    token_count = len(tokens)

    print_border(f"ĐANG XỬ LÝ {token_count} VÍ", Fore.MAGENTA)
    print()

    total_processed = 0
    successful_processed = 0
    semaphore = asyncio.Semaphore(CONFIG['THREADS'])

    async def sem_process_token(index: int):
        nonlocal successful_processed, total_processed
        async with semaphore:
            try:
                success = await process_token(index, tokens[index], task_type, language, proxies)
                total_processed += 1
                if success:
                    successful_processed += 1
                if index < token_count - 1:
                    delay = CONFIG['DELAY_BETWEEN_ACCOUNTS']
                    print_message(f" {LANG[language]['pausing']} {delay:.2f} {LANG[language]['seconds']}", Fore.YELLOW)
                    await asyncio.sleep(delay)
            except Exception as e:
                print(f"{Fore.RED} {LANG[language]['error']}: Processing token {index + 1}: {str(e)}{Style.RESET_ALL}")
                total_processed += 1

    tasks = [sem_process_token(i) for i in range(token_count)]
    await asyncio.gather(*tasks, return_exceptions=True)

    print()
    print_border(f"{LANG[language]['completed'].format(successful=successful_processed, total=total_processed)}", Fore.GREEN)
    print()

def select_task_type_for_script(language: str = 'vi'):
    print_border(LANG[language]['menu_title'], Fore.YELLOW)
    questions = [
        inquirer.List('task_type',
                      message=f"{Fore.CYAN}{LANG[language]['select_task_type']}{Style.RESET_ALL}",
                      choices=[
                          ("1. Daily Check-in", "Daily challenge"),
                          ("2. Required Quest", "Required Quest"),
                          ("3. Spread the Word", "Spread the word"),
                          ("4. Create Spicy Content", "Create spicy content"),
                          ("5. All Tasks", "All Tasks"),
                          ("X. Exit", "exit")
                      ],
                      carousel=True)
    ]
    answer = inquirer.prompt(questions)
    return answer['task_type'] if answer else "exit"

async def run_spicenet_script(language: str = 'vi'):
    task_type = select_task_type_for_script(language)
    if task_type == "exit":
        print_border(LANG[language]['completed'].format(successful=0, total=0), Fore.GREEN)
        return
    await run_spicenet(task_type, language)

if __name__ == "__main__":
    asyncio.run(run_spicenet_script('vi'))
