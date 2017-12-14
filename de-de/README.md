<p align="center">
  <img
    src="http://neonexchange.org/img/NEX-logo.svg"
    width="125px;">
    
</p>
<h3 align="center">Neo ICO Template</h3>
<p align="center">Eine Vorlage für NEP5 konforme Tokens auf der NEO Plattform</p>
<hr/>

#### Betrachtungen

Ein Artikel der die Vorlage beschreibt ist hier verfügbar:
https://medium.com/neon-exchange/nex-ico-template-4ca7ba19fc8b

#### Voraussetzungen

Die Benutzung erfordert Python 3.4 oder 3.5


#### Installation

Kopiere das Repository und navigiere in das Project Verzeichnis.
Erstelle eine Python 3 virtuelle Umgebung und aktivere Sie mit

    python3 -m venv venv
    source venv/bin/activate

oder um explizit Python 3.5 zu installieren,


    virtualenv -p /usr/local/bin/python3.5 venv
    source venv/bin/activate


danach installieren Sie die benötigten Abhängigkeiten mit


    pip install -r requirements.txt



#### Kompilieren

Die Vorlage wird folgendermaßen kompiliert

    from boa.compiler import Compiler

    Compiler.load_and_save('ico_template.py')


Dies wird die Vorlage in `ico_template.avm` kompilieren.




#### Testnet implementierungs Details

Die Vorlage ist momentan im Testnet für Testszenarien mit dem Contract Script Hash `0b6c1f919e95fe61c17a7612aebfaf4fda3a2214` implementiert.


```
{
    "code": {
        "parameters": "0710",
        "hash": "0b6c1f919e95fe61c17a7612aebfaf4fda3a2214",
        "returntype": 5,
        "script": ".. omitted .."
    },
    "version": 0,
    "code_version": ".2",
    "name": "NEX Ico Template",
    "author": "localhuman",
    "description": "An ICO Template",
    "properties": {
        "dynamic_invoke": false,
        "storage": true
    },
    "email": "tom@neonexchange.org"
}


```
