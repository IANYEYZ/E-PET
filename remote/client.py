import socket
import json
import time
import sys
import tty
import termios

def send_message(direction):
    """发送JSON消息到服务器"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '10.31.100.114'
    port = 1145
    
    message = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "sender": "client",
        "direction": direction
    }
    
    try:
        client_socket.connect((host, port))
        json_message = json.dumps(message)
        client_socket.send(json_message.encode('utf-8'))
        print(f"Sent message: {json_message}")
    except Exception as e:
        print(f"Error sending {direction}: {e}")
    finally:
        client_socket.close()

def getch():
    """获取单个键输入，无需按回车"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch.lower()

def main():
    """主程序：通过termios检测WASD和空格键输入控制移动"""
    # 按键到方向的映射
    key_to_direction = {
        'w': 'forward',
        's': 'backward',
        'a': 'left',
        'd': 'right',
        ' ': 'stop'  # 空格键发送stop
    }
    
    print("Press W (forward), A (left), S (backward), D (right), Space (stop), or Q (quit).")
    print("Single keypresses are detected; no Enter key required.")
    
    while True:
        # 检测单个键输入
        key = getch()
        
        # 处理输入
        if key == 'q':
            print("\nExiting...")
            break
        elif key in key_to_direction:
            # 发送对应的方向命令
            direction = key_to_direction[key]
            send_message(direction)
        else:
            print(f"Invalid key: {key}. Use W, A, S, D, Space, or Q.")

if __name__ == "__main__":
    main()
