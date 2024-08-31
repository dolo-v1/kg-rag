sudo systemctl stop ollama
sudo systemctl disable ollama
sudo rm /etc/systemd/system/ollama.service
sudo rm $(which ollama)
sudo rm -rf /usr/share/ollama 
sudo userdel ollama sudo groupdel ollama