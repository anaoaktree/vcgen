import sys, time
from imp_parser import *
from imp_lexer import *
from imp_vcgen import *
from ast import *


from argparse import *


parser = ArgumentParser(description = "Verification of conditions of an annotated program")
parser.add_argument('file', type=open, help= "File .imp to process")
group = parser.add_mutually_exclusive_group()
group.add_argument('-s','--safe', dest='safety', help="Generates safety conditions", action="store_true")
group.add_argument('-sp', dest='strongp', help="Uses the strongest postcondition strategy instead of the default weakest precondition", action="store_true")
parser.add_argument('-p','--proc', dest="proc",help="Verifies a certain procedure", nargs=1, type= str)
#parser.add_argument('-vc', dest="vc", help="Prints the Verification Conditions on screen",action="store_true")
#parser.add_argument('--ast-png', dest="ast",help="Saves the AST in the current directory in png format",action="store_true")


args=parser.parse_args()


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


if __name__ == '__main__':
	print "-----------------------------"
	print "Time/s|\tTask"
	print "-----------------------------"

	init = time.time()
	text = args.file.read()


	lex_result = imp_lex(text)
	print lex_result

	tokens=lex_result[0]
	conds=lex_result[1]

#####################################################
# Parses the tokens of the program into valid types for the ast#
	parse_result = imp_parse(tokens)
	if not parse_result:
		sys.stderr.write('Parse error!\n')
		sys.exit(1)

	print "{0:.3f} |Building AST... ".format(time.time()-init)
	ast = parse_result.value
	#print ast

#####################################################
# Checks the use of safety conditions (option -sp)#
	strategy=True
	if args.strongp:
		strategy=False

#####################################################
# Checks the use of safety conditions (options -s, --safe)#
	vcfunc=vcgen
	if args.safety:
		vcfunc=vcgen_safe

######################################################
# Finds a particular procedure to verify (option --proc)#	
	if args.proc:
		func=args.proc[0]
		procedure=find_proc(ast,func)
		if procedure:
			print "{0:.3f} |Generating Verification Conditions for procedure %s... ".format(time.time()-init) % func
			vfs = vcfunc(procedure.body,procedure.pre, procedure.post,strategy)
		else:
			print "The procedure %s was not found" % func
			sys.exit(0)
######################################################
# Generates conditions for the whole program file #	
	else:
		print "{0:.3f} |Generating Verification Conditions... ".format(time.time()-init)
		conditions=parse_conds(conds)
		if conditions:
			conds=conditions.value
			vfs = vcfunc(ast,conds[0], conds[1],strategy)
		else:
			print "There are no conditions to prove. Please check your code"
			sys.exit(0)
	
######################################################
# Sends the conditions generated to Z3 prover through the Solver() and proves them. #	
	result=True
	print "{0:.3f} |Proving Verification Conditions... ".format(time.time()-init)
	s=Solver()
	s.set(mbqi=True)
	s.set(proof_construction=True)
	c=1
	for i in vfs:
		print "     --------------------------------------"
		print "    #%s# %s \n" %(c, i),
		s=Solver()
		z3expr=Not(i.exp())
		s.add(z3expr)
		res=s.check()
		if res==unsat:
			print "    ::PROVED! :)"
		else:
			result=False
			print "    ::FAILED for ",s.model()
		c+=1
	print "     --------------------------------------"

	if result:
		print "{0:.3f} |Your program seems to be correct! :D".format(time.time()-init)
	else:
		print "{0:.3f} |Something is not right.. Check the conditions!".format(time.time()-init)
	"""
	for i in vfs:
		#print " Z3EXP: ",i.exp()
		s=Solver()
		s.add(Not(i.exp()))
		res=s.check()
		if res==sat:
			print "Failed "
			break
	
	print "asserted constraints..."
	for c in s.assertions():
		print c

	res=s.check()
	print "{0:.3f} |".format(time.time()-init),
	if res==unsat:
		print "Proved! :)"
	else:
		m=s.model()
		print "Failed to prove for the following model : ", m

	
		for d in m.decls():
			print "      # %s = %s types: (%s)" % (d.name(), m[d])
		
		for k, v in s.statistics():
			print "%s : %s" % (k, v)
		
		

	if args.showproof:
		print "{0:.3f} |Proving the conditions in Z3... ".format(time.time()-init)

	if args.ast:
		tree=ASTree(Node('init',None,None))
		ast.show(tree,tree.root)
		tree.draw.write('file2.dot')
		tree.draw.layout(prog ='dot')
		tree.draw.draw('file1.png')

	


"""


