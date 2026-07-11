"""B站扫码登录 - 在CMD内显示二维码"""
import requests
import json
import time
import sys

def generate_qrcode_ascii(url):
    """生成二维码的ASCII字符画"""
    try:
        import qrcode
        from PIL import Image
        import io
        
        # 创建二维码
        qr = qrcode.QRCode(box_size=2, border=1)
        qr.add_data(url)
        qr.make(fit=True)
        
        # 生成矩阵
        matrix = qr.get_matrix()
        
        # 转换为ASCII字符
        ascii_qr = []
        for row in matrix:
            line = ''.join(['██' if cell else '  ' for cell in row])
            ascii_qr.append(line)
        
        return '\n'.join(ascii_qr)
    except ImportError:
        return None

def login():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    print("正在获取登录二维码...")
    
    # 获取二维码
    resp = session.get('https://passport.bilibili.com/x/passport-login/web/qrcode/generate')
    data = resp.json()
    
    if data['code'] != 0:
        print("❌ 获取二维码失败")
        return None
    
    qrcode_url = data['data']['url']
    qrcode_key = data['data']['qrcode_key']
    
    print("\n" + "="*50)
    print("📱 请使用B站APP扫描下方二维码：")
    print("="*50 + "\n")
    
    # 尝试生成ASCII二维码
    ascii_qr = generate_qrcode_ascii(qrcode_url)
    
    if ascii_qr:
        print(ascii_qr)
        print("\n" + "="*50)
        print("💡 如果二维码显示不完整，请调整CMD窗口字体大小")
    else:
        print("⚠️  未安装qrcode库，无法显示二维码")
        print("提示：运行 'pip install qrcode pillow' 安装依赖后可显示二维码")
    
    print("="*50)
    print("\n⏳ 等待扫码... (3秒后开始轮询)")
    
    # 等待扫码
    while True:
        time.sleep(2)
        
        check_url = f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={qrcode_key}'
        resp = session.get(check_url)
        result = resp.json()
        
        code = result['data'].get('code', -1)
        message = result['data'].get('message', '')
        
        if code == 0:
            print("\n✅ 登录成功！")
            
            # 获取Cookie
            cookies = session.cookies.get_dict()
            cookie_str = '; '.join([f'{k}={v}' for k, v in cookies.items()])
            
            # 保存
            with open('bilibili_cookie.txt', 'w', encoding='utf-8') as f:
                f.write(cookie_str)
            
            print(f"📁 Cookie已保存到 bilibili_cookie.txt")
            
            # 验证登录信息
            resp = session.get('https://api.bilibili.com/x/web-interface/nav')
            user = resp.json()
            if user['code'] == 0:
                print(f"👤 用户: {user['data']['uname']}")
                print(f"⭐ 等级: Lv{user['data']['level_info']['current_level']}")
                print(f"💰 硬币: {user['data']['money']}")
            
            print("\n✅ 现在可以运行爬虫了！")
            return cookie_str
            
        elif code == 86038:
            print("\n❌ 二维码已过期，请重新运行程序")
            return None
        elif code == 86090:
            print("📱 已扫描，请在手机上确认登录...")
        elif code == 86101:
            sys.stdout.write(".")
            sys.stdout.flush()
        else:
            if message:
                print(f"\n状态: {message}")
            else:
                sys.stdout.write(".")
                sys.stdout.flush()

if __name__ == '__main__':
    print("\n" + "="*50)
    print("   B站扫码登录工具 - CMD二维码显示版")
    print("="*50 + "\n")
    
    try:
        cookie = login()
        if cookie:
            print("\n🎉 登录完成！")
            input("\n按回车键退出...")
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消登录")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")