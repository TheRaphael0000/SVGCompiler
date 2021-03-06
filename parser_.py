#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module used for the syntaxical analysis by "SVGCompiler"
It is not meant to be directly executed for a "normal" use, execute it only for intermediate debugging purposes if you want to see a pdf containing the AST
Sergiy Goloviatinski & Raphaël Margueron, inf3dlm-b, HE-Arc
13.01.19
"""

import ply.yacc as yacc
from lexemes import tokens
import nodes as AST
import sys
import os
from copy import copy

precedence = (
    ('left', 'BOOL_OR'),
    ('left', 'BOOL_AND'),

    ('left', 'BOOL_EQUAL'),
    ('left', 'BOOL_NOT_EQUAL'),

    ('left', 'BOOL_LT'),
    ('left', 'BOOL_GT'),

    ('left', 'INTEGER_MINUS'),
    ('left', 'INTEGER_PLUS'),
    ('left', 'INTEGER_DIVIDE'),
    ('left', 'INTEGER_TIMES'),
    ('left', 'INTEGER_MODULO'),
    ('left', 'INTEGER_RANDOM'),

    ('right', 'UNARYNUMBER'),
    ('right', 'UNARYBOOL')
)

binaryOperators = (
    "INTEGER_DIVIDE"
    "INTEGER_TIMES"
    "INTEGER_MINUS"
    "INTEGER_PLUS"
    "BOOL_EQUAL"
    "BOOL_NOT_EQUAL"
    "BOOL_AND"
    "BOOL_OR"
    "BOOL_LT"
    "BOOL_GT"
    "BOOL_EQUAL"
    "BOOL_NOT_EQUAL"
)

unaryOperators = (
    "INTEGER_MINUS"
    "BOOL_NOT"
)


#  ____  _        _                            _
# / ___|| |_ __ _| |_ ___ _ __ ___   ___ _ __ | |_ ___
# \___ \| __/ _` | __/ _ \ '_ ` _ \ / _ \ '_ \| __/ __|
#  ___) | || (_| | ||  __/ | | | | |  __/ | | | |_\__ \
# |____/ \__\__,_|\__\___|_| |_| |_|\___|_| |_|\__|___/

def p_lines(p):
    '''ABSTRACT_STATEMENT : STATEMENT LINE_BREAK'''
    p[0] = [p[1]]


def p_statements_recursion(p):
    '''ABSTRACT_STATEMENT : ABSTRACT_STATEMENT ABSTRACT_STATEMENT'''
    p[0] = p[1] + p[2]

#  ____  _            _
# | __ )| | ___   ___| | _____
# |  _ \| |/ _ \ / __| |/ / __|
# | |_) | | (_) | (__|   <\__ \
# |____/|_|\___/ \___|_|\_\___/


def p_block_declaration(p):
    '''ABSTRACT_STATEMENT : BRACE_OPEN ABSTRACT_STATEMENT BRACE_CLOSE'''
    p[0] = [AST.BlockNode(p[2])]


def p_block_declaration_empty(p):
    '''ABSTRACT_STATEMENT : BRACE_OPEN BRACE_CLOSE'''  # to allow empty blocks
    p[0] = []

#  ____  _                   _
# / ___|| |_ _ __ _   _  ___| |_ _   _ _ __ ___  ___
# \___ \| __| '__| | | |/ __| __| | | | '__/ _ \/ __|
#  ___) | |_| |  | |_| | (__| |_| |_| | | |  __/\__ \
# |____/ \__|_|   \__,_|\___|\__|\__,_|_|  \___||___/


def p_if(p):
    '''ABSTRACT_STATEMENT : IF BRACKET_OPEN EXPRESSION BRACKET_CLOSE ABSTRACT_STATEMENT'''
    p[0] = [AST.IfNode(p[3], p[5][0], lineno=p.lineno(3))] + \
        p[5][1:
             ]  # <- only take the first ABSTRACT_STATEMENT following the expression (target block) and add the remaining list to the current return list
    # lineno is used to show the linenumber in an error message if the semantic is false


def p_if_else(p):
    '''ABSTRACT_STATEMENT : IF BRACKET_OPEN EXPRESSION BRACKET_CLOSE ABSTRACT_STATEMENT ELSE ABSTRACT_STATEMENT'''
    p[0] = [AST.IfNode(p[3], p[5][0], p[7][0], lineno=p.lineno(3))
            ] + p[7][1:]  # same as p_if


def p_while(p):
    '''ABSTRACT_STATEMENT : WHILE BRACKET_OPEN EXPRESSION BRACKET_CLOSE ABSTRACT_STATEMENT'''
    p[0] = [AST.LoopNode(p[3], p[5][0], lineno=p.lineno(3))
            ] + p[5][1:]  # same as p_if


#  ____  _
# / ___|| |__   __ _ _ __   ___
# \___ \| '_ \ / _` | '_ \ / _ \
#  ___) | | | | (_| | |_) |  __/
# |____/|_| |_|\__,_| .__/ \___|
#                   |_|


def p_expression_shape(p):
    '''EXPRESSION : SQUAREBRACKET_OPEN SHAPE_TYPE DESCRIPTION ATTRIBUTES SQUAREBRACKET_CLOSE'''
    p[0] = AST.ShapeNode(p[2], p[4])


def p_shapetype(p):
    '''SHAPE_TYPE : CIRCLE
    | TRIANGLE
    | RECTANGLE'''
    p[0] = p[1]

#   ____      _
#  / ___|___ | | ___  _ __
# | |   / _ \| |/ _ \| '__|
# | |__| (_) | | (_) | |
#  \____\___/|_|\___/|_|


def p_colorvalue_colorhex(p):
    '''COLOR_VALUE : COLOR_HEX'''
    p[0] = AST.TokenColorNode(p[1])

#     _   _   _        _ _           _
#    / \ | |_| |_ _ __(_) |__  _   _| |_ ___
#   / _ \| __| __| '__| | '_ \| | | | __/ _ \
#  / ___ \ |_| |_| |  | | |_) | |_| | ||  __/
# /_/   \_\__|\__|_|  |_|_.__/ \__,_|\__\___|


def p_attribute(p):
    '''ATTRIBUTES : ATTRIBUTE'''
    p[0] = [p[1]]


def p_attributes(p):
    '''ATTRIBUTES : ATTRIBUTE SEPARATOR ATTRIBUTES'''
    p[0] = [p[1]] + p[3]


def p_attribute_radius(p):
    '''ATTRIBUTE : RADIUS AFFECTATION EXPRESSION'''
    p[0] = AST.RadiusNode(p[3], lineno=p.lineno(2))


def p_attribute_positionX(p):
    '''ATTRIBUTE : POSITIONX AFFECTATION EXPRESSION'''
    p[0] = AST.PositionXNode(p[3], lineno=p.lineno(2))


def p_attribute_positionY(p):
    '''ATTRIBUTE : POSITIONY AFFECTATION EXPRESSION'''
    p[0] = AST.PositionYNode(p[3], lineno=p.lineno(2))


def p_attribute_color(p):
    '''ATTRIBUTE : COLOR AFFECTATION COLOR_VALUE'''
    p[0] = AST.ColorNode(p[3], lineno=p.lineno(2))


def p_attribute_width(p):
    '''ATTRIBUTE : WIDTH AFFECTATION EXPRESSION'''
    p[0] = AST.WidthNode(p[3], lineno=p.lineno(2))


def p_attribute_height(p):
    '''ATTRIBUTE : HEIGHT AFFECTATION EXPRESSION'''
    p[0] = AST.HeightNode(p[3], lineno=p.lineno(2))

#  ____  _        _                            _
# / ___|| |_ __ _| |_ ___ _ __ ___   ___ _ __ | |_
# \___ \| __/ _` | __/ _ \ '_ ` _ \ / _ \ '_ \| __|
#  ___) | || (_| | ||  __/ | | | | |  __/ | | | |_
# |____/ \__\__,_|\__\___|_| |_| |_|\___|_| |_|\__|


def p_statement_draw(p):
    '''STATEMENT : DRAW EXPRESSION'''
    p[0] = AST.DrawNode(p[2], lineno=p.lineno(1))

#  _____                              _
# | ____|_  ___ __  _ __ ___  ___ ___(_) ___  _ __
# |  _| \ \/ / '_ \| '__/ _ \/ __/ __| |/ _ \| '_ \
# | |___ >  <| |_) | | |  __/\__ \__ \ | (_) | | | |
# |_____/_/\_\ .__/|_|  \___||___/___/_|\___/|_| |_|
#            |_|


def p_int_expression_number(p):
    '''EXPRESSION : ABSTRACT_VARIABLE_NAME'''
    p[0] = p[1]


def p_expression_unaryOperation(p):
    '''EXPRESSION : INTEGER_MINUS EXPRESSION %prec UNARYNUMBER
    | BOOL_NOT EXPRESSION %prec UNARYBOOL'''
    p[0] = AST.UnaryOperation(p[1], [p[2]], lineno=p.lineno(1))


def p_expression_binaryOperation(p):
    '''EXPRESSION : EXPRESSION INTEGER_PLUS EXPRESSION
    | EXPRESSION INTEGER_MINUS EXPRESSION
    | EXPRESSION INTEGER_TIMES EXPRESSION
    | EXPRESSION INTEGER_DIVIDE EXPRESSION
    | EXPRESSION INTEGER_MODULO EXPRESSION
    | EXPRESSION INTEGER_RANDOM EXPRESSION
    | EXPRESSION BOOL_EQUAL EXPRESSION
    | EXPRESSION BOOL_NOT_EQUAL EXPRESSION
    | EXPRESSION BOOL_AND EXPRESSION
    | EXPRESSION BOOL_OR EXPRESSION
    | EXPRESSION BOOL_LT EXPRESSION
    | EXPRESSION BOOL_GT EXPRESSION'''
    p[0] = AST.BinaryOperation(p[2], [p[1], p[3]], p.lineno(2))


def p_expression_bracket(p):
    '''EXPRESSION : BRACKET_OPEN EXPRESSION BRACKET_CLOSE'''
    p[0] = p[2]


def p_expression_number(p):
    '''EXPRESSION : NUMBER'''
    p[0] = AST.TokenNumberNode(p[1])  # already converted in int in lexemes.py


def p_expression_true(p):
    '''EXPRESSION : BOOL_VALUE'''
    p[0] = AST.TokenBooleanNode(p[1])
    # the true/false detection could be done in the lexemes instead of here like for the numbers


# __     __         _       _     _
# \ \   / /_ _ _ __(_) __ _| |__ | | ___  ___
#  \ \ / / _` | '__| |/ _` | '_ \| |/ _ \/ __|
#   \ V / (_| | |  | | (_| | |_) | |  __/\__ \
#    \_/ \__,_|_|  |_|\__,_|_.__/|_|\___||___/


def p_abstract_variable_name(p):
    '''ABSTRACT_VARIABLE_NAME : VARIABLE_NAME'''
    p[0] = AST.TokenVariableNameNode(p[1])


def p_statement_declaration_boolean(p):
    '''STATEMENT : BOOLEAN ABSTRACT_VARIABLE_NAME'''
    p[0] = AST.DeclarationNode(AST.TypeBooleanNode(), p[2])


def p_statement_declaration_integer(p):
    '''STATEMENT : INTEGER ABSTRACT_VARIABLE_NAME'''
    p[0] = AST.DeclarationNode(AST.TypeIntegerNode(), p[2])


def p_statement_declaration_shape(p):
    '''STATEMENT : SHAPE ABSTRACT_VARIABLE_NAME'''
    p[0] = AST.DeclarationNode(AST.TypeShapeNode(), p[2])


def p_statement_affetation(p):
    '''STATEMENT : ABSTRACT_VARIABLE_NAME AFFECTATION EXPRESSION'''
    p[0] = AST.AffectationNode(p[1], p[3], lineno=p.lineno(2))


# We must find a way to create the shorthands without duplicating the code
def p_statement_declaration_affetation_boolean(p):
    '''STATEMENT : BOOLEAN ABSTRACT_VARIABLE_NAME AFFECTATION EXPRESSION'''
    declaration = AST.DeclarationNode(AST.TypeBooleanNode(), p[2])
    affectation = AST.AffectationNode(copy(p[2]), p[4], lineno=p.lineno(2))
    # micro block for the shorthand (can't use the list syntax because it's a STATEMENT (one-line), and not a ABSTRACT_STATEMENT)
    p[0] = AST.BlockNode([declaration, affectation], "declaraffect")


def p_statement_declaration_affetation_integer(p):
    '''STATEMENT : INTEGER ABSTRACT_VARIABLE_NAME AFFECTATION EXPRESSION'''
    declaration = AST.DeclarationNode(AST.TypeIntegerNode(), p[2])
    affectation = AST.AffectationNode(copy(p[2]), p[4], lineno=p.lineno(2))
    p[0] = AST.BlockNode([declaration, affectation], "declaraffect")


def p_statement_declaration_affetation_shape(p):
    '''STATEMENT : SHAPE ABSTRACT_VARIABLE_NAME AFFECTATION EXPRESSION'''
    declaration = AST.DeclarationNode(AST.TypeShapeNode(), p[2])
    affectation = AST.AffectationNode(copy(p[2]), p[4], lineno=p.lineno(2))
    p[0] = AST.BlockNode([declaration, affectation], "declaraffect")


# allow useless expression like : > 1 + 2
def p_useless_expression(p):
    '''STATEMENT : EXPRESSION'''
    p[0] = p[1]


def p_error(p):
    print(f"Parsing Error at line {p.lineno} : {p}")
    yacc.yacc().errok()


def parse(program):
    blocks = yacc.parse(program, debug=False, tracking=True)
    programs = []
    for block in blocks:
        instructions = []
        if block is AST.BlockNode:  # unbox block if the program is a block
            instructions = block.children
        else:
            instructions = block
        programs.append(AST.ProgramNode(instructions))
    return programs, AST.errorList


yacc.yacc(outputdir='./generated')

if __name__ == '__main__':
    fileName = sys.argv[1]
    prog = open(fileName).read()
    programs, errorList = parse(prog)
    i = 0
    for program in programs:
        print("Program", i)
        print(program)
        graph = program.makegraphicaltree()
        name = os.path.splitext(fileName)[0] + "-p" + str(i) + ".pdf"
        graph.write_pdf(name)
        i += 1
