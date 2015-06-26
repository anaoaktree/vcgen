import sys, time
from imp_parser import *
from imp_lexer import *
from imp_vcgen import *


from argparse import *

sys.path.append(".")
import z3



def find_proc(ast,name):
	if proc(ast) and ast.name==name:
		return ast
	elif compound(ast):
		y=find_proc(ast.first,name)
		x=find_proc(ast.second,name)
		if x:
			return x
		return y
	else:
		return None


def start(text):
	print "-----------------------------"
	print "Time/s|\tTask"
	print "-----------------------------"

	init = time.time()
	lex_result = imp_lex(text)

	#Tokens result from the lexer
	tokens=lex_result[0]
	conds=lex_result[1]

#####################################################
# Parses the tokens of the program into valid types for the ast#
	parse_result = imp_parse(tokens)
	if not parse_result:
		return ["error"]
	else:
		print "{0:.3f} |Building AST... ".format(time.time()-init)
		ast = parse_result.value
		print "{0:.3f} |Generating Verification Conditions... ".format(time.time()-init)
		conditions=parse_conds(conds)
		if conditions:
			conds=conditions.value
			return [i+"\n" for i in vcgen(ast,conds[0], conds[1],True)]
		else:
			return ["No conditions"]
