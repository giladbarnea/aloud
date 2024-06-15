#!/usr/bin/env python3
import ast
import os
import subprocess
from pathlib import Path


def os_system(cmd: str, **extra_env_vars) -> int:
    return subprocess.call(cmd, shell=True, env={**os.environ, **{k: str(v) for k, v in extra_env_vars.items()}})


CLASS_RENAMES: dict[str, str] = {
    'Model': 'Chat',
    'Detail': 'ImageDetail',
}


class ClassRenamer(ast.NodeTransformer):
    def visit_ClassDef(self, node):
        if node.name in CLASS_RENAMES:
            node.name = CLASS_RENAMES[node.name]
        return self.generic_visit(node)

    def visit_Name(self, node):
        if node.id in CLASS_RENAMES:
            node.id = CLASS_RENAMES[node.id]
        return self.generic_visit(node)

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and node.value.id in CLASS_RENAMES:
            node.value.id = CLASS_RENAMES[node.value.id]
        return self.generic_visit(node)


def rename_class_in_file(file_path: str):
    file_path = Path(file_path)
    tree = ast.parse(file_path.read_text())

    renamer = ClassRenamer()
    modified_tree = renamer.visit(tree)

    file_path.write_text(ast.unparse(modified_tree))


def main():
    os_system(
        'datamodel-codegen --use-title-as-name --field-constraints --collapse-root-models '
        '--target-python-version 3.11 --strict-nullable --use-unique-items-as-set '
        '--output-model-type pydantic_v2.BaseModel --use-schema-description --use-annotated '
        '--use-generic-container-types --reuse-model --use-union-operator '
        '--use-standard-collections --enable-faux-immutability --enum-field-as-literal=one '
        '--input schemas/create-chat-completion-request.json --input-file-type jsonschema '
        '--output schemas/models.py',
    )
    rename_class_in_file('schemas/models.py')
    return os_system('poe lint')


if __name__ == '__main__':
    main()
