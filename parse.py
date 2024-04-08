import sys
import re
# XML tree library
import xml.etree.ElementTree as ET     

# Exceptions
class HeaderEx(Exception):
    pass


class OpcodeEx(Exception):
    pass


class LexicalEx(Exception):
    pass


class HelperEx(Exception):
    pass


def main():
    arguments = sys.argv

    # --help parameter handling 
    if len(arguments) == 2 and arguments[1] == "--help":
        print("\t\t ========================================\n \
\t\tThe filter script (parse.py in Python 3.10) \n \
\t\t ========================================\n\
\tParse.py reads the source code in IPPcode24 from the standard input, \n\
\t\tchecks the lexical and syntactic correctness \nof the code and prints the XML\
representation of the program to the standard output")
        sys.exit(0)
    elif len(arguments) > 2 and arguments[1] == "--help":
        raise HelperEx("The --help parameter cannot be combined with any other parameter")

    contents = sys.stdin.read()

    # Script body
    components, rawXML = lexer(contents)
    syntaxer(components)
    genXML(rawXML)
    return 0


def lexer(contents):
    contents = contents.replace('\r', '')
    lines = contents.split('\n')
    lexer_out = []
    to_syntaxer = []
    headerFound = False
    header_pattern = r"^\s*\.IPPcode24(\s*#.*)?$"

    for line in lines:
# << Tokenization
        tokens = []
        placeholder = ""
        chars = list(line)

        for char in chars:
            if char == ' ':
                if placeholder:
                    tokens.append(placeholder)
                    placeholder = ""
# Comments handling
            elif char == "#":
                break
            else:
                placeholder += char
        if placeholder:
            tokens.append(placeholder.rstrip('\r'))
# >>
            
# Regular expression patterns for token type detection      
        label_usage = ['LABEL', 'CALL', 'JUMP', 'JUMPIFEQ', 'JUMPIFNEQ']
        frame_pattern = r'\b(GF|LF|TF)@'
        variable_name_pattern = r'[a-zA-Z_\-$&%*!?][a-zA-Z_\-$&%*!?0-9]*$'
        symb_pattern = r'\b(string@|int@|bool@|nil@)'
        type_pattern = r'\b(int|nil|bool|string)$'
        opcode_pattern = r"[a-zA-Z0-9]+"

        items = []
        items2syntaxer = []
        
# << Token type detection
        if tokens:
            if not headerFound:
                if not re.match(header_pattern, tokens[0]):
                    raise HeaderEx("The header is incorrect or missing")
                else:
                    headerFound = True
            else:
                if re.match(header_pattern, tokens[0]):
                    raise LexicalEx("Too many headers")
            if re.match(opcode_pattern, tokens[0]):
                items.append(("opcode", tokens[0].upper()))
                items2syntaxer.append(("opcode", tokens[0].upper()))

            for token in tokens[1:]:
                match = re.match(frame_pattern, token)
                if match:
                    variable_name = token[len(match.group(0)):]
                    if re.match(variable_name_pattern, variable_name):
                        items.append(("var", token))
                        items2syntaxer.append("var")
                    else:
                        raise LexicalEx(f"Incorrect variable name: {token}")
                elif re.match(symb_pattern, token):
                    match = re.match(symb_pattern, token)
                    if match:
                        symbol_type = match.group(1)
                        value = token[len(symbol_type):]
                        valueCheck(symbol_type, value)
                        items.append((symbol_type[:-1], value))
                        items2syntaxer.append(symbol_type[:-1])
                elif re.match(type_pattern, token):
                    if items[-1][1] in label_usage:
                        items.append(("label", token))
                        items2syntaxer.append("label")
                        continue
                    items.append(("type", token))
                    items2syntaxer.append("type")
                elif re.match(variable_name_pattern, token):
                    items.append(("label", token))
                    items2syntaxer.append("label")
                else:
                    raise LexicalEx(f"Unknown argument: {token}")
# >>
        if items:
            lexer_out.append(items)
            to_syntaxer.append(items2syntaxer)
            if not (headerFound):
                raise HeaderEx("The header is incorrect or missing")
    return to_syntaxer, lexer_out


def syntaxer(components):

# Operand dictionary
    opcode_operands = {
        "MOVE": ["var", "symb"],
        "CREATEFRAME": [],
        "PUSHFRAME": [],
        "POPFRAME": [],
        "DEFVAR": ["var"],
        "CALL": ["label"],
        "RETURN": [],

        "PUSHS": ["symb"],
        "POPS": ["var"],

        "ADD": ["var", "symb", "symb"],
        "SUB": ["var", "symb", "symb"],
        "MUL": ["var", "symb", "symb"],
        "IDIV": ["var", "symb", "symb"],
        "LT": ["var", "symb", "symb"],
        "GT": ["var", "symb", "symb"],
        "EQ": ["var", "symb", "symb"],
        "AND": ["var", "symb", "symb"],
        "OR": ["var", "symb", "symb"],
        "NOT": ["var", "symb"],
        "STRI2INT": ["var", "symb", "symb"],
        "INT2CHAR": ["var", "symb"],

        "READ": ["var", "type"],
        "WRITE": ["symb"],

        "CONCAT": ["var", "symb", "symb"],
        "STRLEN": ["var", "symb"],
        "GETCHAR": ["var", "symb", "symb"],
        "SETCHAR": ["var", "symb", "symb"],

        "TYPE": ["var", "symb"],

        "LABEL": ["label"],
        "JUMP": ["label"],
        "JUMPIFEQ": ["label", "symb", "symb"],
        "JUMPIFNEQ": ["label", "symb", "symb"],
        "EXIT": ["symb"],

        "DPRINT": ["symb"],
        "BREAK": []
    }

# Types included in the <symb> term
    symb_def = ["var", "string", "nil", "int", "bool"]

    for line in components:
        opcode = line[0][1]
        if opcode in opcode_operands:
            operands_definition = opcode_operands[opcode]
            provided_operands = line[1:]
# Operand count check
            if len(operands_definition) != len(provided_operands):
                raise LexicalEx(f"Incorrect number of operands for opcode {opcode}")
# Operand type check
            for i in range(0, len(operands_definition)):
                if operands_definition[i] == "symb":
                    if not (provided_operands[i] in symb_def):
                        raise LexicalEx(f"Incorrect types of operands for opcode {opcode}")
                elif operands_definition[i] != provided_operands[i]:
                    raise LexicalEx(f"Incorrect types of operands for opcode {opcode}")

        else:
            raise OpcodeEx(f"Unknown Operational Code \"{opcode}\"")


def genXML(input):
    root = ET.Element("program")
    root.set("language", "IPPcode24")

    for i, component in enumerate(input, start=1):
        opcode_temp, *operands = component
        opcode = opcode_temp[1]

        instruction_element = ET.SubElement(root, "instruction")
        instruction_element.set("order", str(i))
        instruction_element.set("opcode", opcode)

        for j, (operand_type, operand_value) in enumerate(operands, start=1):
            arg_element = ET.SubElement(instruction_element, "arg" + str(j))
            arg_element.set("type", operand_type)
            if operand_value:
                arg_element.text = operand_value
# Handling of the shortened writing of an empty constant in XML
            else:
                arg_element.text = " "

    ET.indent(root, space="\t")
    xml_string = ET.tostring(root, encoding="UTF-8", xml_declaration=True).decode("utf-8")
    xml_string = xml_string.replace('> <', '><')
    print(xml_string)

    return


def valueCheck(type, value):

# Regular expression patterns for value checking
    dec_integer_pattern = r"[+-]?[0-9]+$"
    hex_integer_pattern = r"[+-]?0x[0-9a-fA-F]+[a-zA-Z_\-@$&%*!?]*"
    oct_integer_pattern = r"[+-]?0o[0-7]+[a-zA-Z_\-@$&%*!?]*"
    string_value_pattern = r"(?:\\[0-9]{3}|[^\\\s#]|\\[^0-9\\])*$"
    
    if type == 'int@':
        if not ((re.match(dec_integer_pattern, value)) or (re.match(hex_integer_pattern, value)) or (
                re.match(oct_integer_pattern, value))):
            raise LexicalEx(f"The integer type cannot have a value of {value}")
    elif type == "bool@":
        if not (value == "true" or value == "false"):
            raise LexicalEx(f"The boolean type cannot have a value of {value}")
    elif type == "nil@":
        if not (value == "nil"):
            raise LexicalEx(f"The nil type cannot have a value of {value}")
    elif type == "string@":
        if not (re.match(string_value_pattern, value)):
            raise LexicalEx(f"The string type cannot have a value of {value}")
    return


if __name__ == '__main__':
    try:
        main()
    except HelperEx as e:
        print(f" Error: {e}", file=sys.stderr)
        sys.exit(10)
    except HeaderEx as e:
        print(f" Error: {e}", file=sys.stderr)
        sys.exit(21)
    except OpcodeEx as e:
        print(f" Error: {e}", file=sys.stderr)
        sys.exit(22)
    except LexicalEx as e:
        print(f" Error: {e}", file=sys.stderr)
        sys.exit(23)
    except Exception as e:
        print(f" Unexpected Error : {e}", file=sys.stderr)
        sys.exit(99)
    else:
        sys.exit(0)