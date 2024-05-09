"""Generate documentation for the package."""

from findpatientzero import engine, gamedata, console  # type: ignore


def format_dict(d: dict, pre: str) -> str:
    output = "{\n"
    for key, value in d.items():
        if type(value) is str and "\n" in (value):
            value = value.split("\n")[0] + " ..."
        output += f"{pre}   {key}: {value},\n"
    output += pre + "}"
    return output


hide_types = [
    "NoneType",
    "NamespaceLoader",
    "_NamespacePath",
    "ModuleSpec",
    "method-wrapper",
    "builtin_function_or_method",
    "GenericAlias",
    "_SpecialForm",
]
hide_names = [
    "__builtins__",
    "__globals__",
    "__file__",
    "__cached__",
    "__loader__",
    "__code__",
    "__dict__",
    "__name__",
    "__class__",
    "EVENTS",
]
print_types = ["int", "float", "str", "bool", "tuple"]
expand_types = {
    "module": ["__annotations__"],
    "function": ["__annotations__", "__module__", "__type_params__"],
    "method": ["__annotations__", "__module__", "__type_params__"],
    "type": ["__annotations__", "__module__", "__type_params__"],
    "EnumType": [],
}


def pre(x): return "   " * x


def document_enum(obj, level=0) -> str:
    output = ""
    level += 1
    for member in obj:
        output += f"{pre(level)}{member.name}: {member.value}\n"
    return f"{pre(level - 1)}{obj.__name__} ({type(obj).__name__}):\n" + output


def document(obj, level=0) -> str:

    output = ""
    level += 1

    # Get the name and type of the object
    obj_name = obj.__name__
    obj_type = type(obj).__name__

    # Get all attributes of the object, sorted by category and name
    attributes = dir(obj)
    dunders, privates, publics = [], [], []
    while attributes:
        attr_name = attributes.pop()
        if attr_name.startswith("__"):
            dunders.append(attr_name)
        elif attr_name.startswith("_"):
            privates.append(attr_name)
        else:
            publics.append(attr_name)
    if obj_type in expand_types:
        attributes = expand_types[obj_type] + sorted(publics)
    else:
        attributes = sorted(dunders) + sorted(privates) + sorted(publics)

    dependencies = set()

    # Document each attribute
    for attr_name in attributes:
        # Get the attribute's value and type
        attr_val = getattr(obj, attr_name)
        attr_type = type(attr_val).__name__

        # Ignore some types and names
        if attr_type in hide_types or attr_name in hide_names:
            continue

        # Recursively document modules from the current package
        if attr_type == "module":
            if attr_val.__package__.startswith(obj_name):
                output += document(attr_val, level)
            elif obj_type == "module":
                dependencies.add(attr_val.__name__)
        # Document functions and enums from the current module
        elif attr_type in expand_types:
            if attr_val.__module__ == obj.__name__:
                if attr_type == "EnumType":
                    output += document_enum(attr_val, level)
                else:
                    output += document(attr_val, level)
            elif type(obj).__name__ == "module":
                dependencies.add(attr_val.__module__)

        # Format the attribute's name, type, and value
        else:
            output += f"{pre(level)}{attr_name} ({attr_type})"
            if attr_type in print_types:
                if attr_name == "__doc__" and "\n" in attr_val:
                    attr_val = attr_val.split("\n")[0] + " ..."
                output += f": {attr_val}" if attr_val else ""
            elif attr_type == "property":
                get = str(attr_val.fget.__annotations__['return'])
                if "'" in get:
                    get = get[get.find("'") + 1:get.rfind("'")]
                output += f": {get}"
            elif attr_type == "dict":
                if len(attr_val) == 0:
                    output += ": {}"
                else:
                    output += f": {format_dict(attr_val, pre(level) + " " * (len(attr_name) + 9))}"
            output += "\n"
    heading = f"{pre(level - 1)}{obj.__name__} ({type(obj).__name__}):\n"
    if dependencies:
        heading += f"{pre(level)}[Dependencies: " + ", ".join(dependencies) + "]\n"
    return heading + output


# Document the package
with open("documentation.txt", "w") as f:
    for module in [engine, gamedata, console]:
        f.write(document(module))
