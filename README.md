# For Developers


## Development Environment
ChocAn Simulator development / testing should be done using a virutalenv virtual environment.  
**Note: If using python3 in these commands is causing any issues, try using python3.11 instead.**
### Setting up a virtual environment
1. Install the virtualenv package (make sure you're using Python 3.11)

```
sudo apt-get install virtualenv
```

2. Set up a virtual environment
```
python3 -m virtualenv ./.venv
```

3. Activate the environment in your shell (you'll need to do this whenever you open a new shell)

```
source ./.venv/bin/activate
```

4. Install requirements from requirements.txt and requirements-dev.txt

```
python3 -m pip install -r ./requirements.txt
python3 -m pip install -r ./requirements-dev.txt (installs requirements.txt and requirements-dev.txt)
```

5. Install choc_an_simulator

```
python3 -m pip install -e .
```

## Code Standards

### Type hinting

Function argument and return types must have type hinting. Some examples below:

Basic hints:
```python
def add_ints(a: int, b: int) -> int:
    """Add two ints together"""
    return a + b
```
Data structures:
```python
#You can use Use hints like 'List', 'Dict', 'Set', etc.
#Use the 'Any' hint when any type is allowed
from typing import List, Any
def combine_lists(a: List[Any], b: List[Any]) -> List[Any]:
    """Combine two lists into one"""
    return a + b
```
Optional arguments:
```python
# Optiona[type] accepts 'type' or 'None'.
from typing import Optional
def print_stats(name: str, age: Optional[int]) -> None:
    """Print some stats"""
    print(f"Name: {name}")
    if age is not None:
        print(f"Age: {age}")
```

### Docstrings

All functions should have docstrings that adhere to the [PEP-0257 convention](https://peps.python.org/pep-0257/). 

Check formatting with: ```pre-commit run pydocstring```


## Commits

### 1. Before submitting
Code should be tested, formatted and checked for test coverage before submitting for code review.

To check testing & formatting:
```
pre-commit run --all-files
```
To check test coverage (Coverage should be 100%):

``````
coverage run -m pytest
coverage report
``````

### 2. Push your code
- Push to the branch that is relevant to your work.
- Never push directly to main.

### 3. Submit a merge request
1.  Submit a [merge request](https://gitlab.cecs.pdx.edu/cs-314-term-project/term-project/-/merge_requests/new) through gitlab to merge your code with main.
2.  Post a link to your request in the discord 'merge requests' channel 