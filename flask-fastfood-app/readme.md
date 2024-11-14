
# Tech


> `MySQL 5.7`

> `Python Flask`

> `HTML CSS`

> `JS`


<br />

<br />

# Pre-requisite

```python
python -m venv venv
```

```powershell
venv/Scripts/activate
```

```python
pip install -r requirements.txt
```

<br />

> [!note] 
> Front-end Template [Feane](https://themewagon.com/themes/free-bootstrap-4-html5-restaurant-website-template-feane/) 
> Login Template [Form](https://codepen.io/ianpirro/pen/nXRmWm)

<br />

# Build and Deploy

> [!note]
> *OS* : *Ubuntu 22.04* 

<br />

Follow this step by step to deploy on your own webserver

```bash
git clone https://github.com/snickerdoodless/main_project.git
```

```bash
sudo apt update ; sudo apt-get install -y apache2 libapache2-mod-wsgi-py3 mysql-server git unzip python3-dev python3-pip pkg-config libmysqlclient-dev  
```

```bash
cd snickerdoodless/main_project
```

```bash
git checkout flaskapp
```

```bash
cd flask-fastfood-webapp
```


<br />

> [!important]
>  Setup the root password and adjust on config.py

<br />

```bash
sudo mysql -u root -p -e "CREATE DATABASE feane;"
```

```bash
sudo mysqldump -u root -p feane < feane.sql
```

```bash
sudo tee /etc/apache2/sites-available/flaskapp.conf << EOL
<VirtualHost *:80>
    ServerName localhost
    ServerAdmin webmaster@localhost

    WSGIDaemonProcess flaskapp python-path=/var/www/flaskapp/
    WSGIProcessGroup flaskapp
    WSGIScriptAlias / /var/www/flaskapp/wsgi.py

    <Directory /var/www/flaskapp>
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/flaskapp-error.log
    CustomLog ${APACHE_LOG_DIR}/flaskapp-access.log combined
</VirtualHost>
EOL
```

```bash
sudo mkdir -p /var/www/flaskapp
```

```bash
cd /var/www/flaskapp
```

```bash
sudo mv ~/snickerdoodless/main_project/flask-fastfood-app/* . 
```

```bash
sudo pip install --upgrade pip setuptools
```

```bash
sudo pip install -r requirements.txt --ignore-installed blinker
```

```bash
sudo chown -R www-data:www-data /var/www/flaskapp 
```

```bash
sudo chmod -R 755 /var/www/flaskapp
```

```bash
sudo a2ensite flaskapp
```

```bash
sudo a2dissite 000-default.conf
```

```bash
sudo a2enmod wsgi
```

```bash
sudo systemctl enable apache2
```

```bash
sudo systemctl restart apache2
```

