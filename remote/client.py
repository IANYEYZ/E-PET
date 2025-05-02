import socket
import json
import time
import sys
import tty
import termios
import cv2
import numpy as np
import threading
import struct

def send_message(direction):
    """发送JSON消息到移动服务器"""
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

def receive_video():
    """接收并显示视频流"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '10.31.100.114'
    port = 1146
    
    try:
        client_socket.connect((host, port))
        print("Connected to video server")
        
        data = b""
        payload_size = struct.calcsize('>L')
        
        while True:
            # 接收帧大小
            while len(data) < payload_size:
                packet = client_socket.recv(4096)
                if not packet:
                    return
                data += packet
            
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack('>L', packed_msg_size)[0]
            
            # 接收帧数据
            while len(data) < msg_size:
                data += client_socket.recv(4096)
            
            frame_data = data[:msg_size]
            data = data[msg_size:]
            
            # 解码JPEG帧
            frame = np.frombuffer(frame_data, dtype=np.uint8)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            
            if frame is not None:
                cv2.imshow('Video Stream', frame)
            
            # 按q退出显示窗口
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"Video client error: {e}")
    finally:
        client_socket.close()
        cv2.destroyAllWindows()

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
    """主程序：处理WASD输入和视频显示"""
    # 按键到方向的映射
    key_to_direction = {
        'w': 'forward',
        's': 'backward',
        'a': 'left',
        'd': 'right',
        ' ': 'stop'
    }
    
    # 启动视频接收线程
    video_thread = threading.Thread(target=receive_video, daemon=True)
    video_thread.start()
    
    print("Press W (forward), A (left), S (backward), D (right), Space (stop), or Q (quit).")
    print("Single keypresses are detected; no Enter key required.")
    print("Video stream displayed in separate window (press Q in window to close it).")
    
    while True:
        key = getch()
        
        if key == 'q':
            print("\nExiting...")
            break
        elif key in key_to_direction:
            direction = key_to_direction[key]
            send_message(direction)
        else:
            print(f"Invalid key: {key}. Use W, A, S, D, Space, or Q.")

if __name__ == "__main__":
    main()
