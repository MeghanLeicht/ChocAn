"""Examples of the dataclass library."""
from dataclasses import dataclass, field, FrozenInstanceError
from typing import Any


# A traditional class works like this:
class TraditionalPerson:
    """A person class, constructed in the traditional way."""

    name: str
    age: int

    def __init__(self, name: str, age: int):
        """Boilerplate init function."""
        self.name = name
        self.age = age

    def __eq__(self, other: Any):
        """Manually assert equality between each member."""
        return (self.name == other.name) and (self.age == other.age)


# This requires a ton of boilerplate, and leaves room for a lot of mistakes.

trad_person_a = TraditionalPerson("Ron", 10)
trad_person_b = TraditionalPerson("Ron", 10)
assert trad_person_a == trad_person_b


# A dataclass works like this:
@dataclass
class DataclassPerson:
    """The same person class, but using @dataclass."""

    name: str
    age: int


# It works exactly the same as the traditional version, with way less boilerplate / room for error.
dataclass_person_a = DataclassPerson("George", 11)
dataclass_person_b = DataclassPerson("George", 11)
assert dataclass_person_a == dataclass_person_b


# Class functions still work the same
@dataclass
class TalkingPerson:
    """A person that can talk."""

    name: str
    age: int

    def talk(self) -> None:
        """Say hi."""
        print(f"Hello! My name is {self.name} and I'm {self.age} years old.")


randy = TalkingPerson("Randy", 25)
randy.talk()


# You can assign members yourself if you want to.
@dataclass
class BarPatron:
    """A person with an extra bool for being above drinking age."""

    name: str
    age: int
    can_drink: bool = field(
        init=False
    )  # Tells the dataclass not to assign the memeber in __init__

    def __post_init__(self):
        """Set the can_drink member based on age."""
        # This function is called automatically after the dataclass's auto-generated init function.
        self.can_drink = self.age >= 21


sally = BarPatron("Sally", 19)
if sally.can_drink:
    print(f"{sally.name} can drink because she's {sally.age}")
else:
    print(f"{sally.name} is too young to drink!")


# You can fix this with a dataclass option called 'frozen'
@dataclass(frozen=True)
class FrozenBarPatron:
    """A bar patron whose members can't be changed after initializing."""

    name: str
    age: int
    can_drink: bool = field(
        init=False
    )  # This tells the dataclass not to assign the memeber in __init__

    def __post_init__(self):
        """Set the can_drink member based on age (in a weird workaround way)."""
        object.__setattr__(self, "can_drink", self.age >= 21)


bobby = FrozenBarPatron("Bobby", 12)
try:
    bobby.can_drink = True
except FrozenInstanceError:
    print("Silly bobby, you can't change your members after they're initialized!")
assert bobby.can_drink is False
