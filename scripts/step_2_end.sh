# In activated conda env:
echo "Activating conda environment"
conda activate openwpm

echo "Adding possible missing libraries..."

# OpenWPM is aware that some dependencies might miss
# https://github.com/openwpm/OpenWPM/issues/660
sudo apt install libgtk-3-0
sudo apt install libx11-xcb1
sudo apt install libdbus-glib-1-2
sudo apt install libxt6

# XPCOMGlueLoad error for file /root/Projects/OpenWPM/firefox-bin/libmozgtk.so:
# libgtk-3.so.0: cannot open shared object file: No such file or directory
# https://stackoverflow.com/questions/50768064/firefox-cannot-open-libgtk-3-so-0-how-to-circumvent
apt-get install packagekit-gtk3-module

# XPCOMGlueLoad error for file /root/Projects/OpenWPM/firefox-bin/libxul.so:
# libdbus-glib-1.so.2: cannot open shared object file: No such file or directory
# https://askubuntu.com/questions/923841/problem-after-reinstall-firefox
# sudo apt install libdbus-glib-1-2 

# XPCOMGlueLoad error for file /root/Projects/OpenWPM/firefox-bin/libxul.so:
# libasound.so.2: cannot open shared object file: No such file or directory
sudo apt install libasound2

echo "Installing OpenWPM custom requirements..."

sudo apt install xvfb
sudo apt install tqdm

echo "Installing crawling and monitoring tools..."

sudo apt install tmux
sudo apt install htop # System Monitor
sudo apt install duf # Disk Space

echo "Updating"

sudo apt update
sudo apt upgrade