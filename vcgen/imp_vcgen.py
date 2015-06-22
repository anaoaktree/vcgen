# -*- coding: utf-8 -*-
"""

This file contains the VCGen algorithm as described in the class. 

It also implements the weakest preconditions and strongest postcondition strategies,
 as well as safety verification.


See the report for further references.

"""
from imp_ast import *

skip = lambda x: isinstance(x,Skip)
compound = lambda x: isinstance(x,CompoundStatement)
assign = lambda x: isinstance(x,AssignStatement)
ifstmt = lambda x: isinstance(x,IfStatement)
whilestmt = lambda x: isinstance(x,WhileStatement)
arrayassign = lambda x: isinstance(x,ArrayAssignment)
proc = lambda x: isinstance(x,Procedure)
forall = lambda x: isinstance(x,ForallBexp)
exists = lambda x: isinstance(x,ExistsBexp)
#----------------------------------------------------#

integer =lambda x: isinstance(x,IntAexp)
variable =lambda x: isinstance(x,VarAexp)
div = lambda x: isinstance(x,BinopAexp) and (x.op=="/")
ops = lambda x: isinstance(x,RelopBexp) or isinstance(x,BinopAexp)
notb = lambda x: isinstance(x,NotBexp)
andb = lambda x: isinstance(x,AndBexp)
orb = lambda x: isinstance(x,OrBexp)
arrayselect =lambda x: isinstance(x,ArraySelect)


#Safety verifications
def safe(x):
    if variable(x) or integer(x):
        return true(x)
    if arrayselect(x): #change if dealing with bounded arrays
        return true(x)
    if div(x):
        return AndBexp(NotBexp(RelopBexp("==",x.right,IntAexp(0))),AndBexp(safe(x.left), safe(x.right)))
    elif ops(x):
        return AndBexp(safe(x.left), safe(x.right))
    elif notb(x):
        return safe(x)
    elif andb(x):
        return AndBexp(safe(x.left),ImpBexp(x.left,safe(x.right)))
    elif orb(x):
        return AndBexp(safe(x.left),ImpBexp(NotBexp(x.left),safe(x.right)))

#Safety wp strategy
def wp_safe(ast,cond):
    if compound(ast):
        return wp_safe(ast.first,wp_safe(ast.second, cond))
    elif assign(ast):
        return AndBexp(safe(ast.aexp),cond.replace(ast.name,ast.aexp))
    elif arrayassign(ast):
        return AndBexp(safe(ast.value),cond.replace(ast,ast.value))
    elif whilestmt(ast):
        return ast.inv
    elif ifstmt(ast):
        b=ast.condition
        imp1=ImpBexp(b,wp_safe(ast.true_stmt,cond))
        imp2=ImpBexp(NotBexp(b),wp_safe(ast.false_stmt, cond))
        return AndBexp(safe(b),AndBexp(imp1, imp2))
    else:
        return cond


#Safety VC aux for wp strategy
def wpaux_safe(ast,cond):
    if compound(ast):
        C2=ast.second
        return wpaux_safe(ast.first,wp_safe(C2,cond))+wpaux_safe(C2,cond)
    elif ifstmt(ast):
        return wpaux_safe(ast.true_stmt,cond) + wpaux_safe(ast.false_stmt,cond)
    elif whilestmt(ast):
        I=ast.inv
        b=ast.condition
        C=ast.body
        return [ImpBexp(I,safe(b)),ImpBexp(AndBexp(I,b),wp_safe(C,I)), ImpBexp(AndBexp(I, NotBexp(b)), cond)]+wpaux_safe(C,I)
    else:
        return list()



#Variables for the quantifiers
fresh1=0
fresh0=0
#strongest-post condition strategy - check literature
def sp(ast,cond):
    if compound(ast):
        return sp(ast.second,sp(ast.first, cond))
    elif assign(ast):
        global fresh0
        fresh0+=1
        v=VarAexp('v_'+str(fresh0))
        first=RelopBexp("==",ast.name,ast.aexp.replace(ast.name, v))
        second= cond.replace(ast.name,v)
        return ExistsBexp('v_'+str(fresh0), AndBexp(first,second))
    elif arrayassign(ast):
        global fresh1
        fresh1+=1
        u=VarAexp('u_'+str(fresh1))
        first=RelopBexp("==",ast.selec,ast.value.replace(ast, u))
        second= cond.replace(ast,u)
        return ExistsBexp('u_'+str(fresh1), AndBexp(first,second))
    elif whilestmt(ast):
        return AndBexp(ast.inv,NotBexp(ast.condition))
    elif ifstmt(ast):
        b=ast.condition
        imp1=sp(ast.true_stmt,AndBexp(cond,b))
        imp2=sp(ast.false_stmt,AndBexp(cond,NotBexp(b)))
        return OrBexp(imp1, imp2)
    else:
        return cond


#VCaux with sp strategy
def sp_aux(ast,cond):
    if compound(ast):
        C1=ast.first
        return sp_aux(C1,cond)+sp_aux(ast.second,sp(C1,cond))
    elif whilestmt(ast):
        I=ast.inv
        b=ast.condition
        C=ast.body
        return [ImpBexp(cond,I), ImpBexp(sp(C,AndBexp(I,b)) ,I)]+sp_aux(C,AndBexp(I,b))
    elif ifstmt(ast):
        b=ast.condition
        #Adding the implication as in the paper creates an error and unuseful conditions
        un1 = AndBexp(cond,b)
        un2 = AndBexp(cond,NotBexp(b))
        return sp_aux(ast.true_stmt,AndBexp(cond,b))+sp_aux(ast.false_stmt,AndBexp(cond,NotBexp(b)))
    else:
        return list()


#VCaux com wp
def wp_aux(ast,cond):
   # if proc(ast):
    #    return [ImpBexp(ast.pre, wp(ast.body,ast.post))]+wp_aux(ast.body,ast.post)
    if compound(ast):
        C2=ast.second
        return wp_aux(ast.first,wp(C2,cond))+wp_aux(C2,cond)
    elif ifstmt(ast):
        return wp_aux(ast.true_stmt,cond) + wp_aux(ast.false_stmt,cond)
    elif whilestmt(ast):
        I=ast.inv
        b=ast.condition
        C=ast.body
        return [ImpBexp(AndBexp(I,b),wp(C,I)), ImpBexp(AndBexp(I, NotBexp(b)), cond)]+wp_aux(C,I)
    else:
        return list()




#weakest precondition strategy
def wp(ast,cond):
    if compound(ast):
        return wp(ast.first,wp(ast.second, cond))
    elif assign(ast):
        return cond.replace(ast.name,ast.aexp)
    elif arrayassign(ast):
        return cond.replace(ast,ast.value)
    elif whilestmt(ast):
        return ast.inv
    elif ifstmt(ast):
        b=ast.condition
        imp1=ImpBexp(b,wp(ast.true_stmt,cond))
        imp2=ImpBexp(NotBexp(b),wp(ast.false_stmt, cond))
        return AndBexp(imp1, imp2)
    else:
        return cond
        
    
        
#VCGen for safety check
def vcgen_safe(ast,pre,post,strategy=True):
    return [ImpBexp(pre, wp_safe(ast,post))]+wpaux_safe(ast,post)


#VCGen for wp or sp
def vcgen(ast,pre,post,strategy=True):
    if strategy:
        return [ImpBexp(pre, wp(ast,post))]+wp_aux(ast,post)
    return [ImpBexp(sp(ast,pre),post)]+sp_aux(ast,pre)

