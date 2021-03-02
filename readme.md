# Kryll auto backtest

## Installation

[Télécharger le repository github](https://github.com/Thomas-Houtrique/Krl-backtest/archive/main.zip) et l'extraire sur votre bureau.

## Windows
**il vous faut absolument Google Chrome ou Firefox** sur votre machine.\
- Lancer l'executable qui se trouve dans le dossier *dist*
- Entrer le token que @Torkium vous a donné
- Entrer l'id de la stratégie que vous voulez backtester
- Entrer votre login et votre mot de passe sur la page internet et appuyer sur une touche dans le terminal.\

## Mac OSX
**il vous faut absolument Firefox** sur votre machine.\
- Ouvir un terminal et coller ceci :
```bash
python3 -m pip install requests pyyaml selenium
sudo python3 chemin/vers/auto_test.py
```
- Entrer le token que @Torkium vous a donné
- Entrer l'id de la stratégie que vous voulez backtester
- Entrer votre login et votre mot de passe sur la page internet et appuyer sur une touche dans le terminal.\

## Linux / Raspberry pi
**il vous faut absolument Chromium** sur votre machine.\
- Ouvir un terminal et coller ceci :
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3
python3 -m pip install requests pyyaml selenium
sudo apt-get install chromium-chromedriver
sudo python3 auto_test.py
```
- Entrer le token que @Torkium vous a donné
- Entrer l'id de la stratégie que vous voulez backtester
- Entrer votre login et votre mot de passe sur la page internet et appuyer sur une touche dans le terminal.\

# Config File
```yaml
token: token
strat_ids:
- 5d65371ad9d67b9dbe83xxx
- 5d65371ad9d67b9dbe83xxx

email: xxx@xx.com
password: solarwinds123
```

## License
[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)