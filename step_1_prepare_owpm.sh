echo "STEP 1 - START"
echo "Updating environment..."
sudo apt update
sudo apt upgrade

echo "Installing Mambaforge..."
wget "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh"
bash Mambaforge-$(uname)-$(uname -m).sh
# When prompted press enter, q to quit reading
# To take effect close current shell
conda config --set auto_activate_base false

echo "STEP 1 - COMPLETE"
echo "NEXT STEP -> run install.sh from within OpenWPM/"
echo "please reboot"