
update e upgrade 
wget
python3 

baixar script wget https://raw.githubusercontent.com/Badcebola/blockcebola/refs/heads/main/bloqueiocb.py
entrar na contrab e adicionar a linha "* * * * * cd /etc/unbound && /usr/bin/python3 bloqueiocb.py"

apt install ufw
ufw allow from 10.0.0.0/8
ufw allow from 172.16.0.0/12
ufw allow from 192.168.0.0/16
ufw allow from 177.72.220.0/22
ufw allow from 2804:2ef8::/32
ufw allow from 170.246.136.0/22
ufw deny in to any port 80
ufw allow from any
ufw enable
