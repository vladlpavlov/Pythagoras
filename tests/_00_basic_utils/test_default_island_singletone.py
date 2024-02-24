from pythagoras._00_basic_utils.default_island_singleton import (
    DefaultIsland, DefaultIslandType)

def test_singleton_instance():
    """Test that all instances of DefaultIslandType are actually the same instance."""
    island1 = DefaultIsland
    island2 = DefaultIslandType()
    assert island1 is island2, "DefaultIslandType should only have one instance."

def test_representation():
    """Test the string representation of the DefaultIsland instance."""
    assert repr(DefaultIsland) == "DefaultIsland", (
        "The representation of DefaultIsland should be 'DefaultIsland'.")
