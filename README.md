# For Developers

## Development Environment
ChocAn Simulator development / testing should be done using a virutalenv virtual environment.
### Setting up a virtual environment
1) Install the virtualenv package (make sure you're using Python 3.12)

```
sudo apt-get install virtualenv
```

2) Set up a virtual environment

```
python3 -m virtualenv ./.venv
```

3) Activate the environment in your shell (you'll need to do this whenever you open a new shell)

```
source ./.venv/bin/activate
```

4) Install requirements from requirements.txt and requirements-dev.txt

```
pip install -r ./requirements.txt
pip install -r ./requirements-dev.txt
```

## Code Standards

### Type hinting

Function argument and return types must have type hinting. Some examples below:

Basic hints:
```python
def add_ints(a: int, b: int) -> int:
    return a + b
```
Data structures:
```python
#You can use Use hints like 'List', 'Dict', 'Set', etc.
#Use the 'Any' hint when any type is allowed
from typing import List, Any
def combine_lists(a: List[Any], b: List[Any]) -> List[Any]:
    return a + b
```
Optional arguments:
```python
# Optiona[type] accepts 'type' or 'None'.
from typing import Optional
def print_stats(name: str, age: Optional[int]) -> None:
    print(f"Name: {name}")
    if age is not None:
        print(f"Age: {age}")
```
