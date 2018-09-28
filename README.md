[//]: # ( [![PyPI package](https://img.shields.io/pypi/v/wc_rules.svg)](https://pypi.python.org/pypi/wc_rules) )
[![Documentation](https://readthedocs.org/projects/wc-rules/badge/?version=latest)](http://docs.karrlab.org/wc_rules)
[![Test results](https://circleci.com/gh/KarrLab/wc_rules.svg?style=shield)](https://circleci.com/gh/KarrLab/wc_rules)
[![Test coverage](https://coveralls.io/repos/github/KarrLab/wc_rules/badge.svg)](https://coveralls.io/github/KarrLab/wc_rules)
[![Code analysis](https://api.codeclimate.com/v1/badges/d9cf39851e6a81bd4878/maintainability)](https://codeclimate.com/github/KarrLab/wc_rules)
[![License](https://img.shields.io/github/license/KarrLab/wc_rules.svg)](LICENSE)
![Analytics](https://ga-beacon.appspot.com/UA-86759801-1/wc_rules/README.md?pixel)

# wc_rules
Rule-based modeling for whole-cell models.

## Developer notes:
To install dependencies, first install Docker, then do
```
docker pull karrlab/wc_rules_deps:dev
```
To work on a local wc_rules repo, do
```
docker run --rm -it -v local/path/to/wc_rules:/codebase/wc_rules --name containername karrlab/wc_rules_deps:dev
#: pip install -e /codebase/wc_rules
```
