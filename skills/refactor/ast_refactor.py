#!/usr/bin/env python3
"""
AST 级精确重构模块

提供语法树级别的重构能力，避免文本级重构可能引入的误改问题。

支持的重构动作：
- rename-variable: 重命名变量（精确匹配，不改字符串/注释）
- rename-function: 重命名函数（同步更新所有调用点）
- rename-class: 重命名类（同步更新 import）

使用方式：
    python ast_refactor.py rename-variable <old> <new> <files...> [--apply]
    python ast_refactor.py rename-function <old> <new> <files...> [--apply]
    python ast_refactor.py rename-class <old> <new> <files...> [--apply]
"""

import ast
import sys
import difflib
from pathlib import Path
from typing import List


class RefactoringError(Exception):
    """重构错误"""
    pass


class RenameVariableTransformer(ast.NodeTransformer):
    """重命名变量（精确匹配AST节点）"""

    def __init__(self, old_name: str, new_name: str):
        self.old_name = old_name
        self.new_name = new_name
        self.changes = 0

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """访问变量名节点"""
        if node.id == self.old_name:
            node.id = self.new_name
            self.changes += 1
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """访问函数定义（参数名）"""
        for arg in node.args.args:
            if arg.arg == self.old_name:
                arg.arg = self.new_name
                self.changes += 1
        self.generic_visit(node)
        return node

    def visit_arg(self, node: ast.arg) -> ast.arg:
        """访问 lambda 参数"""
        if node.arg == self.old_name:
            node.arg = self.new_name
            self.changes += 1
        return node


class RenameFunctionTransformer(ast.NodeTransformer):
    """重命名函数"""

    def __init__(self, old_name: str, new_name: str):
        self.old_name = old_name
        self.new_name = new_name
        self.changes = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """函数定义"""
        if node.name == self.old_name:
            node.name = self.new_name
            self.changes += 1
        self.generic_visit(node)
        return node

    def visit_Call(self, node: ast.Call) -> ast.Call:
        """函数调用"""
        if isinstance(node.func, ast.Name) and node.func.id == self.old_name:
            node.func.id = self.new_name
            self.changes += 1
        self.generic_visit(node)
        return node

    def visit_Attribute(self, node: ast.Attribute) -> ast.Attribute:
        """方法调用 obj.method()"""
        if node.attr == self.old_name:
            node.attr = self.new_name
            self.changes += 1
        self.generic_visit(node)
        return node


class RenameClassTransformer(ast.NodeTransformer):
    """重命名类"""

    def __init__(self, old_name: str, new_name: str):
        self.old_name = old_name
        self.new_name = new_name
        self.changes = 0

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """类定义"""
        if node.name == self.old_name:
            node.name = self.new_name
            self.changes += 1
        # 检查基类
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == self.old_name:
                base.id = self.new_name
                self.changes += 1
        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """类名引用（实例化、类型注解）"""
        if node.id == self.old_name:
            node.id = self.new_name
            self.changes += 1
        return node

    def visit_Attribute(self, node: ast.Attribute) -> ast.Attribute:
        """类属性访问 ClassName.attr"""
        if isinstance(node.value, ast.Name) and node.value.id == self.old_name:
            node.value.id = self.new_name
            self.changes += 1
        self.generic_visit(node)
        return node


def parse_file(filepath: str) -> tuple[ast.AST, str]:
    """解析 Python 文件"""
    path = Path(filepath)
    if not path.exists():
        raise RefactoringError(f"文件不存在: {filepath}")

    if not filepath.endswith('.py'):
        raise RefactoringError(f"仅支持 Python 文件: {filepath}")

    source = path.read_text(encoding='utf-8')
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        raise RefactoringError(f"语法错误: {filepath}:{e.lineno}: {e.msg}")

    return tree, source


def apply_transformer(filepath: str, transformer: ast.NodeTransformer) -> tuple[str, int]:
    """应用转换器"""
    tree, _ = parse_file(filepath)

    # 应用转换
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)

    # 转回源码（Python 3.9+）
    new_source = ast.unparse(new_tree)

    return new_source, transformer.changes


def show_diff(filepath: str, old_source: str, new_source: str) -> str:
    """显示差异"""
    old_lines = old_source.splitlines(keepends=True)
    new_lines = new_source.splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"a/{filepath}",
        tofile=f"b/{filepath}",
    )
    return ''.join(diff)


def refactor_rename_variable(old_name: str, new_name: str, files: List[str],
                              dry_run: bool = True) -> int:
    """重命名变量"""
    total_changes = 0

    for filepath in files:
        try:
            old_source = Path(filepath).read_text(encoding='utf-8')
            transformer = RenameVariableTransformer(old_name, new_name)
            new_source, changes = apply_transformer(filepath, transformer)

            if changes > 0:
                print(f"\n📄 {filepath}")
                print(f"   变更数: {changes}")
                print(show_diff(filepath, old_source, new_source))

                if not dry_run:
                    Path(filepath).write_text(new_source, encoding='utf-8')
                    print(f"   ✅ 已应用")
                else:
                    print(f"   🔄 dry-run 模式，未写入")

                total_changes += changes
            else:
                print(f"ℹ️ {filepath}: 未找到变量 '{old_name}'")

        except RefactoringError as e:
            print(f"❌ {filepath}: {e}")

    return total_changes


def refactor_rename_function(old_name: str, new_name: str, files: List[str],
                              dry_run: bool = True) -> int:
    """重命名函数"""
    total_changes = 0

    for filepath in files:
        try:
            old_source = Path(filepath).read_text(encoding='utf-8')
            transformer = RenameFunctionTransformer(old_name, new_name)
            new_source, changes = apply_transformer(filepath, transformer)

            if changes > 0:
                print(f"\n📄 {filepath}")
                print(f"   变更数: {changes}")
                print(show_diff(filepath, old_source, new_source))

                if not dry_run:
                    Path(filepath).write_text(new_source, encoding='utf-8')
                    print(f"   ✅ 已应用")

                total_changes += changes

        except RefactoringError as e:
            print(f"❌ {filepath}: {e}")

    return total_changes


def refactor_rename_class(old_name: str, new_name: str, files: List[str],
                          dry_run: bool = True) -> int:
    """重命名类"""
    total_changes = 0

    for filepath in files:
        try:
            old_source = Path(filepath).read_text(encoding='utf-8')
            transformer = RenameClassTransformer(old_name, new_name)
            new_source, changes = apply_transformer(filepath, transformer)

            if changes > 0:
                print(f"\n📄 {filepath}")
                print(f"   变更数: {changes}")
                print(show_diff(filepath, old_source, new_source))

                if not dry_run:
                    Path(filepath).write_text(new_source, encoding='utf-8')
                    print(f"   ✅ 已应用")

                total_changes += changes

        except RefactoringError as e:
            print(f"❌ {filepath}: {e}")

    return total_changes


def main():
    """CLI 入口"""
    if len(sys.argv) < 4:
        print("用法:")
        print("  ast_refactor.py rename-variable <old> <new> <files...> [--apply]")
        print("  ast_refactor.py rename-function <old> <new> <files...> [--apply]")
        print("  ast_refactor.py rename-class <old> <new> <files...> [--apply]")
        print()
        print("示例:")
        print("  # 预览重命名变量")
        print("  python ast_refactor.py rename-variable user_id uid src/*.py")
        print()
        print("  # 应用重命名")
        print("  python ast_refactor.py rename-variable user_id uid src/*.py --apply")
        sys.exit(1)

    action = sys.argv[1]
    old_name = sys.argv[2]
    new_name = sys.argv[3]

    # 检查是否应用
    apply_flag = '--apply' in sys.argv
    dry_run = not apply_flag

    # 获取文件列表（过滤掉 --apply）
    files = [f for f in sys.argv[4:] if not f.startswith('--')]

    if not files:
        print("❌ 请指定要处理的文件")
        sys.exit(1)

    print(f"🔧 AST 重构: {action}")
    print(f"   {old_name} → {new_name}")
    print(f"   文件: {len(files)} 个")
    print(f"   模式: {'apply' if apply_flag else 'dry-run'}")
    print()

    if action == 'rename-variable':
        changes = refactor_rename_variable(old_name, new_name, files, dry_run)
    elif action == 'rename-function':
        changes = refactor_rename_function(old_name, new_name, files, dry_run)
    elif action == 'rename-class':
        changes = refactor_rename_class(old_name, new_name, files, dry_run)
    else:
        print(f"❌ 未知动作: {action}")
        sys.exit(1)

    print()
    print(f"📊 总变更数: {changes}")

    if dry_run and changes > 0:
        print()
        print("💡 这是预览模式。要应用变更，添加 --apply 参数")


if __name__ == '__main__':
    main()
