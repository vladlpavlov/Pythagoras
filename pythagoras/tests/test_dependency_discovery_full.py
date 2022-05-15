import random
from dataclasses import dataclass, field
from typing import Dict, List

import libcst as cst
from hypothesis import given, strategies as st

from pythagoras._dependency_discovery import _name_is_used_in_source


@dataclass
class MockFunction:
    name: str
    dependencies: List[str]

    @property
    def model(self):
        return cst.FunctionDef(
            name=cst.Name(value=self.name),
            params=cst.Parameters(params=[]),
            body=cst.IndentedBlock(
                body=[
                    cst.SimpleStatementLine(
                        body=[
                            cst.Expr(
                                value=cst.Call(
                                    func=cst.Name(
                                        value=dependency,
                                    ),
                                ),
                            ),
                        ],
                    )
                    for dependency in self.dependencies
                ]
            ),
        )


@dataclass
class MockModule:
    functions: List[str]
    connections: Dict[str, List[str]] = field(init=False)

    def __post_init__(self):
        self.connections = {
            f: random.sample(self.functions[: n + 1], random.randint(0, n + 1))
            for n, f in enumerate(self.functions)
        }

    @property
    def model(self):
        return cst.Module(
            body=[MockFunction(f, self.connections[f]).model for f in self.functions]
        )

    @property
    def funcs(self):
        return [MockFunction(f, self.connections[f]) for f in self.functions]


# Only lowercase latin characters allowed
names = st.text(
    alphabet=st.characters(
        min_codepoint=0x61,
        max_codepoint=0x7A,
    ),
    min_size=1,
)

modules = st.builds(MockModule, st.lists(names))


@given(module=modules)
def test_name_is_used_in_source(module):
    for function in module.funcs:
        code = cst.parse_module("").code_for_node(function.model)
        assert all(_name_is_used_in_source(dep, code) for dep in function.dependencies)
