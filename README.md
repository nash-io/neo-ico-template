<p align="center">
  <img
    src="http://neonexchange.org/img/NEX-logo.svg"
    width="125px;">
    
</p>
<h3 align="center">Neo ICO Template</h3>
<p align="center">A template for NEP5 Compliant Tokens on the NEO platform</p>
<hr/>

#### Considerations

An article describing this template is available here:

https://medium.com/neon-exchange/nex-ico-template-4ca7ba19fc8b

#### Requirements

Usage requires Python 3.4 or 3.5.


#### Installation

Clone the repository and navigate into the project directory. 
Make a Python 3 virtual environment and activate it via

```shell
python3 -m venv venv
source venv/bin/activate
```

or to explicitly install Python 3.5 via

    virtualenv -p /usr/local/bin/python3.5 venv
    source venv/bin/activate

Then install the requirements via

```shell
pip install -r requirements.txt
```

#### Compilation

The template may be compiled as follows

```python
from boa.compiler import Compiler

Compiler.load_and_save('ico_template.py')
```


This will compile your template to `ico_template.avm`


#### Testnet Deployed Details

For testing purposes, this template is deployed on testnet with the following contract script hash:

`0b6c1f919e95fe61c17a7612aebfaf4fda3a2214`

```json
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
