#!/bin/env python3
'''
roll

The highly-customizable dice rolling program.
'''

# ------- Python Library Imports -------

# Standard Library
import argparse
import os
import random
import re
import sys

# Additional Dependencies
try:
    import yaml
except ImportError as e:
    sys.exit('Unable to import PyYAML library - ' + str(e) + '.')
    
# --------------------------------------



# ----------- Initialization -----------

HELP_DESCRIPTION = """
The highly-customizable dice rolling program.
"""

HELP_EPILOG = """

----- Environment Variables -----

The following maps each available environment variable with its corresponding CLI argument:

ROLL_CONFIG_FILE  :  --config-file
"""

EXPR_HELP =  'The dice expression to evaluate. This is a Python-compatable'
EXPR_HELP += ' expression usually containing one ore more "dice rolling expressions",'
EXPR_HELP += ' which are of the form "NdM" or "NDM" where "N" is the number of dice'
EXPR_HELP += ' to roll and "M" is the number of sides on each of the dice. The difference'
EXPR_HELP += ' between "d" and "D" is that "d" will sum the results whereas'
EXPR_HELP += ' "D" will return the result as a string. See the README for more info.'

# Color Sequences
C_BLUE   = '\033[94m'
C_GREEN  = '\033[92m'
C_ORANGE = '\033[93m'
C_RED    = '\033[91m'
C_END    = '\033[0m'
C_BOLD   = '\033[1m'

# Regular Expressions
DICE_REGEX = re.compile(r'(?P<expr>(?P<num>\d*)[dD](?P<sides>\d+))')
SUBTOT_REGEX = re.compile(r'sum\(\[[\d,\s]+\]\)')

# --------------------------------------



# ---------- Private Functions ---------

def _c(instring, color=C_BLUE):
    '''
    Colorizes the specified string.
    '''
    if args.color_output and not color is None:
        return color + instring + C_END
    else:
        return instring


def _parse_arguments():
    '''
    Parses the command-line arguments into a global namespace called "args".
    '''
    argparser = argparse.ArgumentParser(
        description = HELP_DESCRIPTION,
        epilog = HELP_EPILOG,
        usage = 'roll [OPTIONS] EXPRESSION',
        add_help = False,
        formatter_class = lambda prog: argparse.RawDescriptionHelpFormatter(prog, max_help_position=45, width=100)
    )
    argparser.add_argument(
        'expression',
        help = EXPR_HELP,
        nargs = '+'
    )
    argparser.add_argument(
        '-c',
        '--config-file',
        default = os.getenv('ROLL_CONFIG_FILE', os.path.expanduser('~/roll.yaml')),
        dest = 'config_file',
        help = 'Specifies the configuration file to load target definitions from. Defaults to "~/roll.yaml".',
        metavar = 'FILE'
    )
    argparser.add_argument(
        '-h',
        '--help',
        action = 'help',
        help = 'Displays help and usage information.'
    )
    argparser.add_argument(
        '--no-color',
        action = 'store_false',
        dest = 'color_output',
        help = 'Disables color output to stdout/stderr.'
    )
    argparser.add_argument(
        '-v',
        '--verbose',
        action = 'store_true',
        dest = 'verbose',
        help = 'Enables verbose output.'
    )
    global args
    args = argparser.parse_args()


# --------------------------------------



# ---------- Public Functions ----------

def h(lst, n):
    return sorted(lst)[:n]

def l(lst, n):
    return sorted(lst, reverse=True)[:n]

t = sum

s = sum

m = min

M = max

def main():
    '''
    The entrypoint of the script.
    '''
    # Parse command-line arguments
    _parse_arguments()

    expr_str = ' '.join(args.expression)

    if os.path.isfile(args.config_file):
        with open(args.config_file, 'r') as f:
            targets = yaml.load(f.read())

    for target in targets:
        if target in expr_str:
            expr_str = expr_str.replace(target, targets[target])

    dice = DICE_REGEX.findall(expr_str)

    rollstr = expr_str
    pystr = expr_str

    for d in dice:
        if d:
            subexpr = d[0]
            num = int(d[1]) if d[1] else 1
            sides = int(d[2])
            result = [random.randint(1, sides) for i in range(num)]
            if 'd' in subexpr:
                rollstr = rollstr.replace(subexpr, _c('(' + ' + '.join([str(x) for x in result]) + ')'), 1)
                pystr = pystr.replace(subexpr, 'sum(' + str(result) + ')', 1)
            else:
                rollstr = rollstr.replace(subexpr, _c(str(result).replace(' ','')), 1)
                pystr = pystr.replace(subexpr, str(result), 1)
        else:
            print(str(d))

    sums = SUBTOT_REGEX.findall(pystr)

    substr = pystr

    for sm in sums:
        if sm:
            expr = sm
            result = eval(expr)
            substr = substr.replace(expr, _c(str(result)), 1)
            pystr = pystr.replace(expr, str(result), 1)
        else:
            print(str(sm))

    total = eval(pystr)
    if args.verbose:
        print(rollstr + '  ' + _c('-->', C_BOLD) + '  ' + substr + '  ' + _c('=', C_BOLD) + '  ' + str(total))
    else:
        print(rollstr + '  ' + _c('=', C_BOLD) + '  ' + str(total))

# --------------------------------------



# ---------- Boilerplate Magic ---------

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError) as ki:
        sys.stderr.write('Recieved keyboard interrupt!\n')
        sys.exit(100)

# --------------------------------------
