#!/usr/bin/env python

# Bevorzugen Sie Setuptools immer vor Distultis
from setuptools import setup, find_packages
# Um eine konsistente Kodierung zu verwenden 
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Erhalten Sie die lange Beschreibung des README Files
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='neo-ico-template',
    
    # Die Versionen sollten die Regeln von PEP440 einhalten. Für Diskussionen über Single-Sourcing,
    # die verschiedenen Versionen von Setup.py und den Projekt Code, gehen Sie auf
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.1.0',

    description='A Python Template for an NEP5 Token',
    long_description=long_description,

    # Die Project Hauptwebseite.
    url='https://github.com/neonexchange/neo-ico-template',

    # Author Details
    author='Thomas Saunders',
    author_email='tom@neonexchange.org',

    # Wählen Sie Ihre Lizenz
    license='GPL3',

    # Sehen Sie auf https://pypi.python.org/pypi?%3Aaction=list_classifiers nach
    classifiers=[
        # Wie Entwickelt ist das Projekt ? Standardwerte sind
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Stellen Sie fest für wenn Ihr Projekt entwickelt wurde
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Wählen Sie die gewünschte Lizenz aus. (Sollte gleich der "Lizenz" oben sein)
        'License :: OSI Approved :: MIT License',

        # Geben Sie an welche Python Versionen Sie unterstützen. Insbesondere, versichern 
        # Sie sich das Sie angeben ob Sie Python2, Python3 oder beide unterstützen.
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    # Auf was bezieht sich Ihr Projekt?
    keywords='NEP5 ICO Token NEO .avm blockchain development dApp',

    # Falls Ihr Projekt einfach ist können Sie die Pakete hier manuell angeben.
    # Ansonsten können Sie find_packages() benutzen.
#    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # Alternativ falls Sie nur ein my_module.py verteilen wollen, löschen Sie das Kommentarzeichen vor:
    py_modules=["nex"],

    # Listen Sie hier run-time Abhängigkeiten auf. Wenn Sie das Projekt installieren,
    # werden diese von pip installiert. Für die Analyse von „install_requires“ vs pip's requirements Dateien 
    # sehen Sie hier nach:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['neo-boa',],


    python_requires='>=3.4, <3.6',

    # Listen Sie hier weitere Abhängigkeitsgruppen auf.
    # (z.B Entwicklungsabhängigkeiten). Sie können diese mithilfe folgender
    # Syntax installieren: 
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['twine','wheel','sphinx','autopep8','pep8','sphinx-rtd-theme'],
        'test': ['coverage'],
    },

    # Falls es Dateien in Ihrem Packages gibt die installiert werden müssen, 
    # benennen Sie diese hier. Falls Sie Python 2.6 oder niedriger verwenden,
    # müssen diese auch in der MANIFEST.in enthalten sein.
    #package_data={
    #    'sample': ['package_data.dat'],
    #},

    # Obwohl 'package_data' der bevorzugte Ansatz ist, müssen Sie in manchen Fällen
    # eventuell die Dateien außerhalb des Packages platzieren. Sehen Sie dazu:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In diesem Fall, wird 'data_file' in '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])] installiert.

    # Um ausführbare Scripts bereitzustellen, benutzen Sie Einstiegspunkte in den Einstellungen
    # mit dem Keyword „Scripts“. Einstiegspunkte stellen cross-plattform Unterstützung bereit 
    # und erlauben es pip die richtige Form der ausführbaren Datei für die Zielplattform zu erstellen.
    #entry_points={
    #    'console_scripts': [
    #        'sample=sample:main',
    #    ],
    #},
)
