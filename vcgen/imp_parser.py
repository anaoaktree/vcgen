# Copyright (c) 2011, Jay Conrod.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Jay Conrod nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL JAY CONROD BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


"""
This is the file that parses the tokens of the language. For more information on how this works check jayconrod.com
"""


from imp_lexer import *
from combinators import *
from imp_ast import *

# Basic parsers
def keyword(kw):
    return Reserved(kw, RESERVED)

def annotation(kw):
    return Annotation(kw,ANNOTATION)

num = Tag(INT) ^ (lambda i: int(i))
id = Tag(ID)



# Top level parser for the program
def imp_parse(tokens):
    ast = parser()(tokens, 0)
    return ast

def parser():
    return Phrase(stmt_list()) 

#Parser for anotations
def parse_conds(tokens):
    conds = parserconds()(tokens, 0)
    return conds
    
def parserconds():
    return Phrase(annotations_list()) 

def annotations_list():
    separator = annotation('post') ^ (lambda x: lambda l, r: [l,r])
    return Exp(annotations(), separator)
   

# Statements
def stmt_list():
    separator = keyword(';') ^ (lambda x: lambda l, r: CompoundStatement(l, r))
    return Exp(stmt(), separator)


#Checks id a stream of tokens is an assignment, conditional, loop, procedure or array
def stmt():
    return assign_stmt() | \
           if_stmt()     | \
           while_stmt()  | \
           proc()|\
           array_assignment()


def annotations():
    return precond_annotation()| \
            postcond_annotation()

           


def proc():
    def process(parsed):
        ((((((pre,post),_),name),_),body),_)=parsed
        return Procedure(name,body,pre,post)
    return Opt(precond_annotation()+postcond_annotation())+keyword('proc') + id + keyword(':')+ Lazy(stmt_list) + \
           keyword('end') ^ process

           
def precond_annotation():
    def process(parsed):
        (_,exp)=parsed
        return PreCondition(exp)
    return annotation('pre') + bexp() ^ process
    
    
def postcond_annotation():
    def process(parsed):
        (_,exp)=parsed
        return PostCondition(exp)
    return  Opt(annotation('post')) + bexp() ^ process
    
##  ARRAYS
    
def array_assignment():
    def process(parsed):
        (((((name,_),index),_),_),val)=parsed
        return ArrayAssignment(name,index,val)
    return id + keyword('[') + aexp() + keyword(']') + keyword(':=') + aexp() ^process

##--------------------------------------------------
def assign_stmt():
    def process(parsed):
        ((name, _), exp) = parsed
        return AssignStatement(name, exp)
    return id + keyword(':=') + aexp() ^ process

def if_stmt():
    def process(parsed):
        (((((_, condition), _), true_stmt), false_parsed), _) = parsed
        if false_parsed:
            (_, false_stmt) = false_parsed
        else:
            false_stmt = Skip()
        return IfStatement(condition, true_stmt, false_stmt)
    return keyword('if') + bexp() + \
           keyword('then') + Lazy(stmt_list) + \
           Opt(keyword('else') + Lazy(stmt_list)) + \
           keyword('end') ^ process

def while_stmt():

    def process(parsed):
        (((((_, condition), _),loop_inv), body), _) = parsed
        if loop_inv:
            ((_,inv),_)=loop_inv
        else:
            inv='skip'
        return WhileStatement(condition, body,inv)
    return keyword('while') + bexp() + keyword('do') + \
        Opt(keyword('{')+ bexp() + keyword('}')) + \
           Lazy(stmt_list) + \
           keyword('end') ^ process
           
# Boolean expressions
def bexp():
    return precedence(bexp_term(),
                      bexp_precedence_levels,
                      process_logic)

def bexp_term():
    return bexp_not()   | \
           bexp_relop() | \
           bexp_group() |\
           bexp_forall() |\
           bexp_exists()


def bexp_forall():
    def process(parsed):
        (((_,var),_),bexp)=parsed
        return ForallBexp(var,bexp)
    return keyword('forall') + id + keyword(':')+ Lazy(bexp) ^ process


def bexp_exists():
    def process(parsed):
        ((((_,var),_),bexp),_)=parsed
        return ExistsBexp(var,bexp)
    return keyword('exists') + id + keyword(':')+ Lazy(bexp) ^ process


def bexp_not():
    return keyword('not') + Lazy(bexp_term) ^ (lambda parsed: NotBexp(parsed[1]))

def bexp_relop():
    relops = ['<', '<=', '>', '>=', '==', '!=']
    return aexp() + any_operator_in_list(relops) + aexp() ^ process_relop

def bexp_group():
    return keyword('(') + Lazy(bexp) + keyword(')') ^ process_group

# Arithmetic expressions
def aexp():
    return precedence(aexp_term(),
                      aexp_precedence_levels,
                      process_binop)

def aexp_term():
    return array_select() | aexp_value() | aexp_group()

def aexp_group():
    return keyword('(') + Lazy(aexp) + keyword(')') ^ process_group

##ARRAY SELECT
def array_select():
    def process(parsed):
        (((name,_),index),_)=parsed
        return ArraySelect(name,index)
    return id + keyword('[') + Lazy(aexp) + keyword(']') ^ process


def aexp_value():
    return (num ^ (lambda i: IntAexp(i))) | \
           (id  ^ (lambda v: VarAexp(v)))
           
    

# An IMP-specific combinator for binary operator expressions (aexp and bexp)
def precedence(value_parser, precedence_levels, combine):
    def op_parser(precedence_level):
        return any_operator_in_list(precedence_level) ^ combine
    parser = value_parser * op_parser(precedence_levels[0])
    for precedence_level in precedence_levels[1:]:
        parser = parser * op_parser(precedence_level)
    return parser

# Miscellaneous functions for binary and relational operators
def process_binop(op):
    return lambda l, r: BinopAexp(op, l, r)

def process_relop(parsed):
    ((left, op), right) = parsed
    return RelopBexp(op, left, right)

#Changed here to return only BooleanOp
def process_logic(op):
    if op == 'and':
        return lambda l, r: AndBexp(l, r)
    elif op == 'or':
        return lambda l, r: OrBexp(l, r)
    elif  op == 'implies':
        return lambda l, r: ImpBexp(l, r)
    elif  op == '<->':
        return lambda l, r: BimpBexp(l, r)
    else:
        raise RuntimeError('unknown logic operator: ' + op)


def process_group(parsed):
    ((_, p), _) = parsed
    return p

def any_operator_in_list(ops):
    op_parsers = [keyword(op) for op in ops]
    parser = reduce(lambda l, r: l | r, op_parsers)
    return parser

# Operator keywords and precedence levels
aexp_precedence_levels = [
    ['*', '/'],
    ['+', '-'],
]

bexp_precedence_levels = [
    ['and'],
    ['or'],
    ['implies']
]
