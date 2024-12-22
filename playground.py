class RegexParser:
    class Node:
        pass

    class ConcatNode(Node):
        def __init__(self, children):
            self.children = children

        def __repr__(self):
            return f"ConcatNode({self.children})"

    class AltNode(Node):
        def __init__(self, children):
            self.children = children

        def __repr__(self):
            return f"AltNode('{self.children})"

    class CharNode(Node):
        def __init__(self, char):
            self.char = char

        def __repr__(self):
            return f"CharNode('{self.char}')"

    class GroupNode(Node):
        def __init__(self, group_id, child):
            self.group_id = group_id
            self.child = child

        def __repr__(self):
            return f"GroupNode({self.group_id}, {self.child})"

    class ExprRefNode(Node):
        def __init__(self, ref_id):
            self.ref_id = ref_id

        def __repr__(self):
            return f"ExprRefNode({self.ref_id})"

    class StrRefNode(Node):
        def __init__(self, ref_id):
            self.ref_id = ref_id

        def __repr__(self):
            return f"StrRefNode({self.ref_id})"

    def __init__(self, regex):
        self.indent = 0
        self.regex = regex
        self.index = 0
        self.group_id = 1

    def parse(self):
        return self._parse_alt()

    def _parse_concat(self):
        nodes = []
        while self.index < len(self.regex):
            if self.regex[self.index] == '|':
                break
            elif self.regex[self.index] == ')':
                break
            else:
                nodes.append(self._parse_atom())
        return self.ConcatNode(nodes) if len(nodes) > 1 else nodes[0]

    def _parse_alt(self):
        nodes = [self._parse_concat()]
        while self.index < len(self.regex) and self.regex[self.index] == '|':
            self.index += 1
            nodes.append(self._parse_concat())
        return self.AltNode(nodes) if len(nodes) > 1 else nodes[0]

    def _parse_group(self, capturable=True):
        if capturable:
            self.index += 1  # Skip '('
            group_id = self.group_id
            self.group_id += 1
        else:
            self.index += 3
        child = self._parse_alt()
        if self.index >= len(self.regex) or self.regex[self.index] != ')':
            raise ValueError("Unmatched '(' in regex")
        self.index += 1  # Skip ')'

        if capturable:
            return self.GroupNode(group_id, child)
        else:
            return self.GroupNode(-1, child)

    def _parse_atom(self):
        if self.regex[self.index] == '(':
            if self.regex[self.index + 1] == '\\':
                self.index += 2
                if self.index < len(self.regex) and self.regex[self.index].isdigit():
                    ref_id = int(self.regex[self.index])
                    self.index += 1
                    return self.StrRefNode(ref_id)

            elif self.regex[self.index + 1] == '?':
                self.index += 2
                if self.index < len(self.regex) and self.regex[self.index].isdigit():
                    ref_id = int(self.regex[self.index])
                    self.index += 1  # Skip ')'
                    return self.ExprRefNode(ref_id)
                elif self.index < len(self.regex) and self.regex[self.index] == ':':
                    self.index -= 2
                    return self._parse_group(capturable=False)
            else:
                return self._parse_group()

        else:
            char = self.regex[self.index]
            self.index += 1
            return self.CharNode(char)


# Пример использования
# +:
# (aa|bb)(?1)
# (a|(bb))(a|(?2))
# (a|(bb))(a|(?3))
# (a|(b|c))d
# ((a|b)c)*
# (a(?=b))c
# (a*|(?:b|c))d
# (?=a)b
# a(?=b|c)d
# (a(?1)b|c)
# (?1)(a|(b|c))
#
# -:
# a|b)
# (?3)(a|(b|c))
# ((a)(b)(c)(d)(e)(f)(g)(h)(i)(j))
# (a)(?2)
# (?=(a))
# (?=a(?=b))
regex = '(a|(bb))(a|(?3))'
parser = RegexParser(regex)
result = parser.parse()


def print_concat_node(node, indent=0):
    if isinstance(node, RegexParser.ConcatNode):
        print(f"{' ' * indent}ConcatNode\n{' ' * indent}(")
        for child in node.children:
            print_node(child, indent + 4)
        print(f"{' ' * indent})")
    else:
        raise ValueError("Передан неверный тип. Ожидался объект типа ConcatNode.")


def print_alt_node(node, indent=0):
    if isinstance(node, RegexParser.AltNode):
        print(f"{' ' * indent}AltNode\n{' ' * indent}(")
        for child in node.children:
            print_node(child, indent + 4)
        print(f"{' ' * indent})")
    else:
        raise ValueError("Передан неверный тип. Ожидался объект типа AltNode.")


def print_group_node(node, indent=0):
    if isinstance(node, RegexParser.GroupNode):
        print(f"{' ' * indent}GroupNode\n{' ' * indent}({node.group_id},")
        print_node(node.child, indent + 4)
        print(f"{' ' * indent})")
    else:
        raise ValueError("Передан неверный тип. Ожидался объект типа GroupNode.")


def print_node(node, indent=0):
    if isinstance(node, RegexParser.ConcatNode):
        print_concat_node(node, indent)
    elif isinstance(node, RegexParser.AltNode):
        print_alt_node(node, indent)
    elif isinstance(node, RegexParser.GroupNode):
        print_group_node(node, indent)
    elif isinstance(node, RegexParser.CharNode):
        print(f"{' ' * indent}CharNode('{node.char}')")
    elif isinstance(node, RegexParser.ExprRefNode):
        print(f"{' ' * indent}ExprRefNode({node.ref_id})")
    elif isinstance(node, RegexParser.StrRefNode):
        print(f"{' ' * indent}StrRefNode({node.ref_id})")
    else:
        raise ValueError("Неизвестный тип узла")


print(regex)
print(result)
print_node(result)
