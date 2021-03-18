# Kryll auto backtest

## Installation

[Télécharger le repository github](https://github.com/Thomas-Houtrique/Krl-backtest/archive/main.zip) et l'extraire sur votre bureau.

Normalement vous avez reçu un token, il est personnel, ne le partagez pas, ça permet au script de communiquer avec le site pour envoyer les backtests.

## Windows
**il vous faut absolument Google Chrome ou Firefox** sur votre machine.\
- Dans le fichier config.yaml présent dans le répertoire dist, remplacez your_token par votre token 
- Exécutez dist/auto_test.exe
- Répondez aux différentes questions
- Un navigateur va s'ouvrir sur la page de login, identifiez vous.
- Ensuite laissez tranquillement tourner le script.

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

Par défaut il va automatiquement à l'exécution aller récupérer toutes les strats de la marketplace, les backtester dans un ordre aléatoire, sur les paires recommandées uniquement, sur différentes périodes.

Si vous voulez tester des strats en particulier.
- Mettez le paramètre update_strat à la valeur "n"
- Dans strat_ids il faut mettre uniquement les identifiants de strat que vous voulez tester.

Si vous voulez tester toutes les paires même les non recommandées, répondez "y" à la première question au lancement du script et suivez les instructions
```yaml
token: token
strat_ids:
- 5d65371ad9d67b9dbe83xxx
- 5d65371ad9d67b9dbe83xxx

email: xxx@xx.com
password: solarwinds123
update_strat: y
```
**L'auto login ne fonctionne que sur Firefox**


## License
[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)