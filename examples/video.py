import cv2
import subprocess
 
rtmp = 'rtmp://10.31.2.254:1935/live/zhichun?sign=1746263546-2e748b4e7590280ccd429383a2a7aedc'
 
# 读取视频并获取属性
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ 摄像头无法打开")
else:
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    sizeStr = str(size[0]) + 'x' + str(size[1])
     
    command = ['ffmpeg',
        '-y', '-an',
        '-f', 'rawvideo',
        '-vcodec','rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', sizeStr,
        '-r', '25',
        '-i', '-',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        '-f', 'flv',
        rtmp]
     
    pipe = subprocess.Popen(command
        , shell=False
        , stdin=subprocess.PIPE
    )
     
    while cap.isOpened():
        success,frame = cap.read()
        if success:
            '''
    		对frame进行识别处理
    		'''
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break    
            pipe.stdin.write(frame.tostring())
     
    cap.release()
    pipe.terminate()
