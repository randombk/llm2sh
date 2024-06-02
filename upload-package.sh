#!/bin/bash
python3 -m build --sdist .
twine upload dist/llmdo-$(cat .latest-version.generated.txt).tar.gz
