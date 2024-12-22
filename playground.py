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
                    self.index += 2
                    return self.StrRefNode(ref_id)

            elif self.regex[self.index + 1] == '?':
                self.index += 2
                if self.index < len(self.regex) and self.regex[self.index].isdigit():
                    ref_id = int(self.regex[self.index])
                    self.index += 2  # Skip ')'
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
#'(a(?1))(\\1)(q|ww|e)'


#
# -:
# a|b)
# (?3)(a|(b|c))
# ((a)(b)(c)(d)(e)(f)(g)(h)(i)(j))
# (a)(?2)
# (?=(a))
# (?=a(?=b))
regex = '(a(?1)b|c)'
parser = RegexParser(regex)
structure = parser.parse()

class Validator:
    def __init__(self, structure):
        self.structure = structure

    def validate(self):
        q1 = self.structure.group_id < 10
        return q1


v = Validator(structure)
if not v.validate():
    print('incorrect expression')
    exit()
else:
    print('correct expression')




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
print(structure)
print_node(structure)


class RaiseError(Exception):
    pass


class CFGBuilder:
    def __init__(self, node_representations):
        self.node_representations = node_representations
        self.group_nonterm = {}
        self.ncg_index = 1
        self.alt_index = 1
        self.star_index = 1
        self.char_index = 1
        self.group_index = 1
        self.concat_index = 1
        self.rules = {}
        self.processors = {
            'CharNode': self.process_char_node,
            'GroupNode': self.process_group_node,
            'ConcatNode': self.process_concat_node,
            'AltNode': self.process_alt_node,
            'ExprRefNode': self.ref_node,
            'StrRefNode': self.ref_node
        }

    def build(self, node):
        start = 'S'
        self.rules[start] = [[self.process_node(node)]]
        return start, self.rules

    def process_node(self, node):
        node_type = node.__class__.__name__
        if node_type in self.processors:
            return self.processors[node_type](node)
        else:
            raise RaiseError(f"Неизвестный тип узла {node_type}")

    def process_char_node(self, node):
        nt = self.generate_unique_nt('Char')
        self.rules.setdefault(nt, []).append([node.char])
        return nt

    def process_group_node(self, node):
        nt = self.group_nonterm.get(node.group_id)
        if nt is None:
            if node.group_id != -1:
                nt = f"G{node.group_id}"
            else:
                nt = self.generate_unique_nt('Ncg')
                self.ncg_index += 1
            self.group_nonterm[node.group_id] = nt
        sub_nt = self.process_node(node.child)
        self.rules.setdefault(nt, []).append([sub_nt])
        return nt

    def process_concat_node(self, node):
        nt = self.generate_unique_nt('C')
        seq_nts = [self.process_node(ch) for ch in node.children]
        self.rules.setdefault(nt, []).append(seq_nts)
        return nt

    def process_alt_node(self, node):
        nt = self.generate_unique_nt('A')
        for branch in node.children:
            br_nt = self.process_node(branch)
            self.rules.setdefault(nt, []).append([br_nt])
        return nt

    def contains_group(self, node, ref_id):
        if isinstance(node, RegexParser.GroupNode) and node.group_id == ref_id:
            return True

        if isinstance(node, (RegexParser.ConcatNode, RegexParser.AltNode)):
            return any(self.contains_group(child, ref_id) for child in node.children)

    def ref_node(self, node):
        ref_id = node.ref_id
        if ref_id not in self.group_nonterm:
            self.group_nonterm[ref_id] = f"G{ref_id}"
        return self.group_nonterm[ref_id]

    def generate_unique_nt(self, prefix):
        if prefix == 'Ncg':
            name = f"Ncg{self.ncg_index}"
            self.ncg_index += 1
            return name
        elif prefix == 'A':
            name = f"R{self.alt_index}"
            self.alt_index += 1
            return name
        elif prefix == 'C':
            name = f"{prefix}{self.concat_index}"
            self.concat_index += 1
            return name
        elif prefix == 'Char':
            name = f"{prefix}{self.char_index}"
            self.char_index += 1
            return name


c = CFGBuilder(structure)
start, rules = c.build(structure)
for nt in rules:
    for rule_output in rules[nt]:
        print(f"{nt} -> {''.join(rule_output)}")
