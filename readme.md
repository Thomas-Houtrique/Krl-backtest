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

Si vous souhaitez que le script ne demande plus un identifiant de stratégie et les backtests automatiquement, indiquer y à update_strat
Exemple : 
```yaml
update_strat: y
```

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

Si vous voulez tester toutes les paires même les non recommandées, répondez "y" à la première question au lancement du script et suivez les instructions

Si vous voulez tester des exchanges en particulier :
Exemple :
```yaml
exchanges:
- BINANCE
- FTX
```

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

Si votre compte Kryll n'a pas de protection Google Authenticator (2FA), vous pouvez mettre n pour cette option.
```yaml
# set to "n" if you don't have 2FA on your kryll account 
ask_2fa: y
```

Lorsque vous avez Chrome et Firefox installés sur votre PC, le script demande lequel vous souhaitez utiliser. Cette option permet de le définir en configuration pour que la question ne soit plus posé au lancement.
```yaml
# browser choice, replace your_browser by chrome or firefox if you have both on your system
browser: your_browser
```

**Exemple complet de fichier de config : voir le fichier config-sample.yaml**

### Paramétrage avancé (config.json)

Ces options permettent principalement de définir dans le fichier de configuration toutes les réponses aux questions qui sont demandés à son lancement.

Au démarrage du script, il est demandé si on souhaite le configurer pour activer le backtesting de toutes les paires (et pas seulement les paires recommandées par chaque stratégies) et si on souhaite activer le mode verbeux (information pour le debug en console). Cette option permet de désactiver cette question, par défaut, seuls les paires recommandées seront backtestées et le mode verbeux désactivé. Il est possible de définir aussi en config ces paramètres (voir ci-après)
```yaml
# set to "n" to not ask configuration when starting the script
ask_config: y
```

Si ask_config: n, on peut mettre sur y l'option suivante pour que toute les paires soient testées et pas seulement celles recommandées pour chaque stratégie.
```yaml
# set to "y" to test all pairs instead of only recommanded pairs - if ask_config is "y", this option is ignored
every_pairs: n
```

Si ask_config: n, on peut mettre sur y l'option suivante pour afficher dans la console les informations de debuggage. Il est recommandé de la mettre que sur y à la demande des développeurs pour résoudre des problèmes.
```yaml
# set to "y" to display debug information in console - if ask_config is "y", this option is ignored
verbose: n
```

## FAQ
-Si vous avez des problèmes de connexion aborted avec le script, pensez à télécharger la version du chromedriver en adéquation avec la version de chrome que vous avez installé : https://chromedriver.chromium.org/downloads

## License
[GNU General Public License v3.0](https://choosealicense.com/licenses/gpl-3.0/)
