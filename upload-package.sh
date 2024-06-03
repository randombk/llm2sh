#!/bin/bash
python3 -m build --sdist .
twine upload dist/llm2sh-$(cat .latest-version.generated.txt).tar.gz
