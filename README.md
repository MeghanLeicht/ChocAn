# For Developers


## Development Environment
ChocAn Simulator development / testing should be done using a virutalenv virtual environment.  
### Setting up a virtual environment

1. Install the virtual environment and dependencies. (make sure you have Python 3.11 installed). 

```
make install
```

2. Activate the environment in your shell (you'll need to do this whenever you open a new shell)

```
source ./.venv/bin/activate
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
# Optional[type] accepts 'type' or 'None'.
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

### Error Handling
In order to ensure full test overage, errors should be handled explicitly and separately. 
```python
#Bad:
try:
    rases_key_or_type_error()
except Exception as e:
    raise e

#Still bad, because incomplete testing can show full coverage:
try:
    rases_key_or_type_error()
except (KeyError, TypeError) as e:
    raise e

#Good:
try:
    rases_key_or_type_error()
except KeyError as err_key:
    raise err_key
except TypeError as err_type:
    raise err_type
```
## Commits

### 1. Before submitting
Code should be tested, formatted and checked for test coverage before submitting for code review.

To check testing & formatting:
```
pre-commit run --all-files
```
To check test coverage (Coverage should be 100%):

```
make test
```
If coverage is less than 100%, you can use coverage's html option to generate
a graphical view
```
coverage run -m pytest
coverage html
# Open the new file at "./htmlcov/index.html" in your browser. 
```

### 2. Push your code
- Push to the branch that is relevant to your work.
- Never push directly to main.

### 3. Submit a merge request
1.  Submit a [merge request](https://gitlab.cecs.pdx.edu/cs-314-term-project/term-project/-/merge_requests/new) through gitlab to merge your code with main.
2.  Post a link to your request in the discord 'merge requests' channel 