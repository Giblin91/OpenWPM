echo '----------------------------------------------------------'
echo '----------------------------------------------------------'
echo "STEP 2 - START"

# In activated conda env:
echo "Activating conda environment"
echo '----------------------------------------------------------'
echo '----------------------------------------------------------'

# Make conda available to shell script
eval "$(conda shell.bash hook)"
conda config --set auto_activate_base false
conda activate openwpm

echo "Updating"

sudo apt update
sudo apt upgrade

echo '----------------------------------------------------------'
echo '----------------------------------------------------------'
echo "Adding possible missing libraries..."
echo '----------------------------------------------------------'
echo '----------------------------------------------------------'

# OpenWPM is aware that some dependencies might miss
# https://github.com/openwpm/OpenWPM/issues/660
sudo apt install libgtk-3-0 -y
sudo apt install libx11-xcb1 -y
sudo apt install libdbus-glib-1-2 -y
sudo apt install libxt6 -y

# XPCOMGlueLoad error for file /root/Projects/OpenWPM/firefox-bin/libmozgtk.so:
# libgtk-3.so.0: cannot open shared object file: No such file or directory
# https://stackoverflow.com/questions/50768064/firefox-cannot-open-libgtk-3-so-0-how-to-circumvent
apt-get install packagekit-gtk3-module -y

# XPCOMGlueLoad error for file /root/Projects/OpenWPM/firefox-bin/libxul.so:
# libdbus-glib-1.so.2: cannot open shared object file: No such file or directory
# https://askubuntu.com/questions/923841/problem-after-reinstall-firefox
# sudo apt install libdbus-glib-1-2 

# XPCOMGlueLoad error for file /root/Projects/OpenWPM/firefox-bin/libxul.so:
# libasound.so.2: cannot open shared object file: No such file or directory
sudo apt install libasound2 -y

sudo apt install npm

echo '----------------------------------------------------------'
echo '----------------------------------------------------------'
echo "Installing OpenWPM custom requirements..."
echo '----------------------------------------------------------'
echo '----------------------------------------------------------'

sudo apt install xvfb -y
conda install tqdm -y

echo '----------------------------------------------------------'
echo '----------------------------------------------------------'
echo "Installing crawling and monitoring tools..."
echo '----------------------------------------------------------'
echo '----------------------------------------------------------'

sudo apt install tmux -y
sudo apt install htop -y # System Monitor
sudo apt install duf -y # Disk Space

echo "STEP 2 - COMPLETE"