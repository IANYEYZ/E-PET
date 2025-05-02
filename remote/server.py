import socket
import json
from helpers.wheel import WHEEL

def start_server():
    # 创建socket对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 设置服务器地址和端口
    host = '0.0.0.0'
    port = 1145
    
    # 绑定地址
    server_socket.bind((host, port))
    
    # 开始监听
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")
    
    # 初始化WHEEL对象
    wheel = WHEEL()
    
    while True:
        # 接受客户端连接
        client_socket, addr = server_socket.accept()
        print(f"Connected by {addr}")
        
        try:
            # 接收数据
            data = client_socket.recv(1024).decode('utf-8')
            if data:
                # 解析JSON
                try:
                    json_data = json.loads(data)
                    print("Received JSON message:")
                    print(json.dumps(json_data, indent=2))
                    
                    # 获取方向字段
                    direction = json_data.get('direction', '').lower()
                    
                    # 根据方向执行相应的wheel方法
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
                
            # 关闭客户端连接
            client_socket.close()
        except Exception as e:
            print(f"Error: {e}")
            client_socket.close()

if __name__ == "__main__":
    start_server()
