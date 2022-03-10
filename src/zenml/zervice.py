from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI

from zenml.enums import StackComponentType
from zenml.io.utils import get_global_config_directory
from zenml.stack import Stack, StackComponent
from zenml.stack_stores import SqlStackStore
from zenml.stack_stores.models import (
    ActiveStackName,
    StackConfiguration,
    StackWrapper,
    Version,
)

app = FastAPI()

# to run this, execute:
# uvicorn zervice:app --reload
# TODO: figure out how to make `zenml service up` start this


root: Path = Path(get_global_config_directory())
url = f"sqlite:///{root / 'service_stack_store.db'}"
print(url)
stack_store = SqlStackStore(url)


@app.get("/")
@app.get("/health")
async def heath() -> str:
    return "OK"


@app.get("/version", response_model=Version)
async def version() -> Version:
    return Version(version=stack_store.version)


@app.get("/stacks/active", response_model=ActiveStackName)
async def active_stack_name() -> ActiveStackName:
    return ActiveStackName(active_stack_name=stack_store.active_stack_name)


@app.get("/stacks/activate/{name}")
async def activate_stack(name: str) -> None:
    stack_store.activate_stack(name)


@app.get("/stacks/configurations/{name}")
async def get_stack_configuration(name: str) -> StackConfiguration:
    return stack_store.get_stack_configuration(name)


@app.get("/stacks/configurations/")
async def stack_configurations() -> Dict[str, StackConfiguration]:
    return stack_store.stack_configurations


@app.post("/components/register")
async def register_stack_component(component: StackComponent) -> None:
    stack_store.register_stack_component(component)


@app.get("/stacks", response_model=List[StackWrapper])
async def stacks():
    return [
        StackWrapper(name=s.name, components=s.components)
        for s in stack_store.stacks
    ]


@app.get("/stacks/{name}", response_model=StackWrapper)
async def get_stack(name: str) -> StackWrapper:
    stack = stack_store.get_stack(name)
    return StackWrapper(name=stack.name, components=stack.components)


@app.post("stacks/register", response_model=Dict[str, str])
def register_stack(self, stack: StackWrapper) -> Dict[str, str]:
    return stack_store.register_stack(
        Stack.from_components(name=stack.name, components=stack.components)
    )


@app.get("stacks/{name}/deregister")
def deregister_stack(self, name: str) -> None:
    stack_store.deregister_stack(name)


@app.get("/components/{component_type}/{name}")
async def get_stack_component(
    self, component_type: StackComponentType, name: str
) -> StackComponent:
    return stack_store.get_stack_component(component_type, name=name)


@app.get("/components/{component_type}")
def get_stack_components(
    component_type: StackComponentType,
) -> List[StackComponent]:
    return stack_store.get_stack_components(component_type)


@app.get("/components/deregister/{component_type}/{name}")
async def deregister_stack_component(
    component_type: StackComponentType, name: str
) -> None:
    return stack_store.deregister_stack_component(component_type, name=name)
