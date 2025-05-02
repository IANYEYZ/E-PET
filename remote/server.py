import socket
import json
import cv2 # type: ignore
import numpy as np
import threading
import struct
from helpers.wheel import WHEEL

def handle_movement_server():
    """处理移动命令的服务器"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '10.31.100.114'
    port = 1145
    
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Movement server listening on {host}:{port}")
    
    wheel = WHEEL()
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Movement connected by {addr}")
        
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                try:
                    json_data = json.loads(data)
                    print("Received JSON message:")
                    print(json.dumps(json_data, indent=2))
                    
                    direction = json_data.get('direction', '').lower()
                    if direction == 'forward':
                        wheel.straight()
                        print("Executing wheel.straight()")
                    elif direction == 'right':
                        wheel.rotate_clockwise()
                        print("Executing wheel.rotate_clockwise()")
                    elif direction == 'left':
                        wheel.rotate_counterclockwise()
                        print("Executing wheel.rotate_counterclockwise()")
                    elif direction == 'backward':
                        wheel.back()
                        print("Executing wheel.back()")
                    elif direction == 'stop':
                        wheel.stop()
                        print("Executing wheel.stop()")
                    else:
                        print(f"Unknown direction: {direction}")
                
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
                except AttributeError as e:
                    print(f"Error with wheel methods: {e}")
                
            client_socket.close()
        except Exception as e:
            print(f"Movement server error: {e}")
            client_socket.close()

def handle_video_server():
    """处理视频流的服务器"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '10.31.100.114'
    port = 1146
    
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Video server listening on {host}:{port}")
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    while True:
        client_socket, addr = server_socket.accept()
        print(f"Video connected by {addr}")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Failed to capture frame")
                    break
                
                # 压缩为JPEG
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
                result, encimg = cv2.imencode('.jpg', frame, encode_param)
                if not result:
                    print("Error: Failed to encode frame")
                    continue
                
                data = encimg.tobytes()
                # 发送帧大小（4字节）+帧数据
                client_socket.sendall(struct.pack('>L', len(data)) + data)
                
        except Exception as e:
            print(f"Video server error: {e}")
            client_socket.close()
        
        # 客户端断开后继续监听
        print(f"Video client {addr} disconnected")

def main():
    """主程序：启动移动和视频服务器"""
    movement_thread = threading.Thread(target=handle_movement_server, daemon=True)
    video_thread = threading.Thread(target=handle_video_server, daemon=True)
    
    movement_thread.start()
    video_thread.start()
    
    try:
        # 保持主线程运行
        movement_thread.join()
        video_thread.join()
    except KeyboardInterrupt:
        print("\nExiting server...")
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
