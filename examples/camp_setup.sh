#!/bin/bash

# set -e  # Exit on any error

echo "🔐 Set password"
read -p "Enter password: " -s PASSWORD
echo ""

USERNAME=$(whoami)
JUPYTER_CONFIG_DIR="/home/$USERNAME/.jupyter"

echo "🔒 Change user password"
echo "pi:$PASSWORD" | sudo chpasswd

echo "🧩 Enable VNC / I2C / SPI"
sudo raspi-config nonint do_vnc 0
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0

sudo apt update
sudo apt install -y vim libcap-dev ffmpeg portaudio19-dev


echo "🌐 Configure pip to use Tsinghua mirror"
pip3 config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

echo "⬆️ Upgrade pip"
pip3 install --upgrade pip --break-system-packages

echo "📦 Install Python packages (system-wide)"
pip3 install --break-system-packages \
    jupyterlab \
    matplotlib \
    adafruit-circuitpython-servokit \
    opencv-python \
    rpi-lgpio \
    spidev \
    numpy \
    pillow \
    openai \
    pyaudio \
    soundfile \
    dashscope \
    pydub \
    simpleaudio \
    scipy \
    sounddevice \
    playsound \
    picamera2 \
    jupyter_server  # Required for password hashing

HASHED_PASS=$(python3 -c "from jupyter_server.auth import passwd; print(passwd('$PASSWORD'))")

echo "📝 Write Jupyter config"
mkdir -p "$JUPYTER_CONFIG_DIR"
cat <<EOF > "$JUPYTER_CONFIG_DIR/jupyter_lab_config.py"
c = get_config()
c.ServerApp.open_browser = False
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.password = u'$HASHED_PASS'
EOF

echo "🛠️ Create systemd service to start JupyterLab at boot"
mkdir -p /home/$USERNAME/Workspace
sudo bash -c "cat <<EOF > /etc/systemd/system/jupyterlab.service
[Unit]
Description=Jupyter Lab (System Python)
After=network.target

[Service]
Type=simple
User=$USERNAME
ExecStart=/home/$USERNAME/.local/bin/jupyter-lab --notebook-dir=/home/$USERNAME/Workspace --ip=0.0.0.0 --port=8888 --no-browser
WorkingDirectory=/home/$USERNAME/Workspace
Restart=always

[Install]
WantedBy=multi-user.target
EOF"

echo "🔁 Enable and start JupyterLab service"
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable jupyterlab
sudo systemctl start jupyterlab

echo "✅ All done! Access JupyterLab at: http://<your-ip>"

amixer sset 'Master' 100%

