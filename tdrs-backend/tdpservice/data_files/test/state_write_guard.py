"""Conservative syntax checks for state writes outside the lifecycle controller."""

import ast


def _contains_state(
    node: ast.AST | None,
    bindings: dict[str, ast.AST],
    seen: frozenset[str] = frozenset(),
) -> bool:
    if isinstance(node, ast.Name) and node.id not in seen:
        return _contains_state(bindings.get(node.id), bindings, seen | {node.id})
    if isinstance(node, ast.Constant):
        return node.value == "state"
    if isinstance(node, ast.Dict):
        return any(_contains_state(key, bindings, seen) for key in node.keys) or any(
            _contains_state(value, bindings, seen)
            for key, value in zip(node.keys, node.values)
            if key is None
        )
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        return any(_contains_state(item, bindings, seen) for item in node.elts)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id == "dict":
            return _writes_state(node, bindings, seen)
    return False


def _writes_state(
    call: ast.Call,
    bindings: dict[str, ast.AST],
    seen: frozenset[str] = frozenset(),
) -> bool:
    return any(keyword.arg == "state" for keyword in call.keywords) or any(
        _contains_state(keyword.value, bindings, seen)
        for keyword in call.keywords
        if keyword.arg in {None, "defaults", "create_defaults"}
    ) or any(_contains_state(arg, bindings, seen) for arg in call.args)


def _state_write_call(call: ast.Call, bindings: dict[str, ast.AST]) -> bool:
    if isinstance(call.func, ast.Name) and call.func.id == "setattr":
        return len(call.args) > 1 and _contains_state(call.args[1], bindings)
    if not isinstance(call.func, ast.Attribute):
        return False
    if call.func.attr in {"update", "update_or_create", "get_or_create", "create"}:
        return _writes_state(call, bindings)
    if call.func.attr in {"bulk_update", "bulk_create", "save"}:
        fields = [
            keyword.value
            for keyword in call.keywords
            if keyword.arg in {"fields", "update_fields"}
        ]
        if call.func.attr == "bulk_update" and len(call.args) > 1:
            fields.append(call.args[1])
        return any(_contains_state(field, bindings) for field in fields)
    return False


def state_write_lines(source: str, allowed_attributes: frozenset[str] = frozenset()) -> list[int]:
    """Find direct assignments and common ORM state writes, including named fields."""
    tree = ast.parse(source)
    bindings = {
        target.id: node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    }
    bindings.update({
        node.target.id: node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.value is not None
    })
    violations = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.ctx, ast.Store)
            and node.attr == "state"
            and ast.unparse(node) not in allowed_attributes
        ):
            violations.add(node.lineno)
        if isinstance(node, ast.Call) and _state_write_call(node, bindings):
            violations.add(node.lineno)
    return sorted(violations)
