# BackPlusScript

## Installation

[Télécharger le repository github](https://github.com/Thomas-Houtrique/BackPlusScript/archive/main.zip) et l'extraire sur votre bureau.

Normalement vous avez reçu un token, il est personnel, ne le partagez pas, ça permet au script de communiquer avec le site pour envoyer les backtests.

## Windows
**il vous faut absolument Google Chrome ou Firefox** sur votre machine.
- Dans le fichier config.yaml présent dans le répertoire dist, remplacez your_token par votre token 
- Exécutez dist/auto_test.exe
- Répondez aux différentes questions
- Un navigateur va s'ouvrir sur la page de login, identifiez vous.
- Ensuite laissez tranquillement tourner le script.
- /!\ : en cas de problème, vérifier que le fichier dist/config.yaml est correct, que le format correspond au config_sample.yaml, que votre token est bon

## Mac OSX
**il vous faut absolument Firefox** sur votre machine.
- Dans le fichier config.yaml présent dans le répertoire principal, remplacez your_token par votre token 
- Ouvir un terminal et coller ceci :
```bash
python3 -m pip install requests pyyaml selenium tqdm selenium-wire
sudo python3 chemin/vers/auto_test.py
```
- Répondez aux différentes questions
- Un navigateur va s'ouvrir sur la page de login, identifiez vous.
- Ensuite laissez tranquillement tourner le script.
- /!\ : en cas de problème, vérifier que le fichier dist/config.yaml est correct, que le format correspond au config_sample.yaml, que votre token est bon

## Linux / Raspberry pi
**il vous faut absolument Chromium** sur votre machine.
- Dans le fichier config.yaml présent dans le répertoire principal, remplacez your_token par votre token 
- Ouvir un terminal et coller ceci :
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3
python3 -m pip install requests pyyaml selenium tqdm selenium-wire
sudo apt-get install chromium-chromedriver
sudo python3 auto_test.py
```
- Répondez aux différentes questions
- Un navigateur va s'ouvrir sur la page de login, identifiez vous.
- Ensuite laissez tranquillement tourner le script.
- /!\ : en cas de problème, vérifier que le fichier dist/config.yaml est correct, que le format correspond au config_sample.yaml, que votre token est bon

# Config File

Par défaut il va automatiquement à l'exécution aller récupérer toutes les strats de la marketplace, les backtester dans un ordre aléatoire, sur les paires recommandées uniquement, sur différentes périodes.

Si vous voulez tester des strats en particulier :
- Mettez le paramètre update_strat à la valeur "n"
- Dans strat_ids il faut mettre uniquement les identifiants de strat que vous voulez tester
Exemple : 
```yaml
update_strat: n
strat_ids:
- 5d65371ad9d67b9dbe83xxx
- 5d65371ad9d67b9dbe83xxx
```
L'identifiant de la strat se trouve dans l'url de la strat sur la page de la strat.

Si vous voulez tester des paires en particulier :
-Remplissez/ajoutez la section "pair" dans le fichier de configuration
-Listez les paires que vous voulez tester
Exemple :
```yaml
pair:
- BTC/USDT
- ETH/BTC
```
Les paires recommandées seront testées dans tous les cas en + des paires listées

Si vous voulez tester des accumulations en particulier :
-Remplissez/ajoutez la section "pair" dans le fichier de configuration
-Listez les paires que vous voulez tester
Exemple :
```yaml
accu:
- USDT
- BTC
```
Les paires recommandées seront testées dans tous les cas en + des accumulations listées

Si vous voulez lancer le script en cachant le navigateur, vous pouvez le lancer en headless :
-Remplissez/ajoutez les sections "headless", "email" et "password" dans le fichier de configuration
-Mettez le paramètre headless à "y"
-Renseignez votre mail de connexion kryll dans le paramètre "email"
-Renseignez votre mot de passe de connexion kryll dans le paramètre "password"
Exemple :
```yaml
headless: y
email: your_kryll_email@gmail.com
password: your_kryll_password
```
Les paires recommandées seront testées dans tous les cas en + des accumulations listées

Si vous voulez tester toutes les paires même les non recommandées, répondez "y" à la première question au lancement du script et suivez les instructions

Exemple complet de fichier de config
```yaml
# replace your_token by your token
token: your_token
# Set to "y" if you activate autologin and want to hide browser
headless: n
# set to y if you want to auto update strat list
update_strat: y
# strat to test. Automatically updated if update_strat is set to y
strat_ids:
- 5cd021a7a2b4ea1b142a01a7c
- 5ea5eba876621921e1ab037f
- 5dc70e5fb9a8334b7d9b4716
- 5c58b255812598100207aaaf
- 5e4915c0567b48b089605ee1
- 5c4f25a24ca41aa0d326f956
```

## FAQ
-Si vous avez des problèmes de connexion aborted avec le script, pensez à télécharger la version du chromedriver en adéquation avec la version de chrome que vous avez installé : https://chromedriver.chromium.org/downloads

## License
[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)
