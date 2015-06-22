# -*- coding: utf-8 -*-
"""

This file contains the classes for the AST types and the methods to traverse it.

Note that it was adapted from the interpreter by Jay Conrod at http://jayconrod.com/

----------------------------------------------------------------------------
The most important methods defined for the interaction with the solver are:

def replace(self,x,y):
        '''
        Method that handles assignment x:=y.
        Returns a new instance with the value of x replaced by y.
        '''
        pass


    def exp(self):
        '''
        Transforms an expression into a form consistent with Z3 solver.


        The return value can be:
            -> a string (Z3 recognizes strings as expressions with eval command);
            -> Z3 BoolRef function, such as And, Or, Implies or Not.
        '''
        pass
----------------------------------------------------------------------------
"""

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
import sys
from equality import *
from z3 import *

#####################################

class Statement(Equality):
    pass

class Aexp(Equality):
    pass

class Bexp(Equality):
    pass

class ArrayExp(Equality):
    pass




######################################

class Skip(Statement):
    """
    Class that handles skips in the language
    """
    def __init__(self):
        pass
    def __repr__(self):
        return "skip"

class AssignStatement(Statement):
    """
    Class that handles assignements
    """
    def __init__(self, name, aexp):
        self.name = VarAexp(name)
        self.aexp = aexp

    def __repr__(self):
        return '%s:= %s' % (self.name, self.aexp)
        
class ArrayVar(Aexp):
    """
    Class that handles arrays
    """
    def __init__(self, name):
        self.name=name
        self.name = "Array('%s', IntSort(), IntSort())" % name
        self.var= name

    def __repr__(self):
        return self.var

    def  exp(self):
        """
    ** Transforms an expression into a form consistent with Z3 solver.

    ** The return value is a string (Z3 recognizes strings as expressions with eval command);
        """
        return self.name # Sends variable to Z3 context
'''
    def replace(self, x, y):
        """
    ** Method that handles assignment x:=y.

    ** Returns a new instance named y if the current var is x. Otherwise just returns itself.
        """

        if x==self:
            if isinstance(y, BinopAexp):
                return y
        #if type(self.var)!=str:
         # this verification handles composed types such as (x+10) of type BinopAexp
       #     return BinopAexp
      #  elif x.var==self.var:
      #      return 
        return self

'''

class Procedure:
    """
    Class that handles procedures
    """
    def __init__(self,name,body, pre=True, post=True):
        self.name =name
        self.body =body
        self.pre =pre
        self.post =post

    def __repr__(self):
        return "proc %s" % self.name


        
class ArrayAssignment(Statement):
    def __init__(self,name,index,value):
        self.name=ArrayVar(name)
        self.var=name
        self.index=index
        self.value=value
        self.selec=ArraySelect(name,index)
    
    def __repr__(self):
        return '%s[%s]:= %s'%(self.name,self.index,self.value)
    

    def exp(self):
        return Store(eval(self.name.exp()), self.index.exp(),self.value.exp())


class ArraySelect(Statement):
    def __init__(self,name,index):
        self.name=ArrayVar(name)
        self.index=index
        self.var=name

    def __repr__(self):
        return '%s[%s]'%(self.name,self.index)

        
    def replace(self,x,y):
        """
    ** Method that handles assignment x:=y.

    ** Returns a new instance named y if the current array is x. Otherwise just returns itself.
        """
        if isinstance(x,ArrayAssignment):
            if x.var==self.var and x.index==self.index:
                return y
        if self.index==x:
            return ArraySelect(self.var,y)
        return self

    def exp(self):
        """
    ** Transforms an expression into a form consistent with Z3 solver.

    ** The return value is a string (Z3 recognizes strings as expressions with eval command);
        """
        return '%s[%s]' % (self.name.exp(),self.index.exp())

            
        
class CompoundStatement(Statement):
    """
    Class that handles separators (with a comma)
    """
    def __init__(self, first, second):
        self.first = first
        self.second = second

            
    def __repr__(self):
       return'CompoundStatement(%s, %s)' % (self.first, self.second)
        


class IfStatement(Statement):
    """
    Class that handles conditional statements
    """
    def __init__(self, condition, true_stmt, false_stmt):
        self.condition = condition
        self.true_stmt = true_stmt
        self.false_stmt = false_stmt

    def __repr__(self):
        return '(if %s then  %s else %s)' % (self.condition, self.true_stmt, self.false_stmt)

class WhileStatement(Statement):
    def __init__(self, condition, body,loop_inv):
        self.condition = condition
        self.body = body
        self.inv=LoopInvariant(loop_inv)


    def __repr__(self):
        return 'while %s do %s %s end' % (self.condition, self.inv, self.body)    


class IntAexp(Aexp):
    def __init__(self, i):
        self.i = i

    def replace(self,x,y):
        """
    ** Method that handles assignment x:=y.

    ** Returns the same instance because int values cannot be replaced.
        """
        return self

    def exp(self):
        """
    ** Transforms an expression into a form consistent with Z3 solver.

    ** The return value is a string (Z3 recognizes strings as expressions with eval command);
        """
        return str(self.i)  

    def __repr__(self):
        return '%s' % self.i    
        


class VarAexp(Aexp):
    def __init__(self, name):
        self.name=name
        self.name = "Int('%s')" %name
        self.var= name
        
    def  exp(self):
        """
    ** Transforms an expression into a form consistent with Z3 solver.

    ** The return value is a string (Z3 recognizes strings as expressions with eval command);
        """
        return self.name # Sends variable to Z3 context

    def replace(self, x, y):
       # return y
        """
    ** Method that handles assignment x:=y.

    ** Returns a new instance named y if the current var is x. Otherwise just returns itself.
        """
        if x==self:
            return y
        return self


    def __repr__(self):
        return '%s' % self.var


class BinopAexp(Aexp):
    """
    Handles arithmetic expressions such as 
    x/1, 1-8, y+2 ...
    """
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


    def replace(self,x,y):
        """
    ** Method that handles assignment x:=y.

    ** Returns a new instance with the value of x replaced by y.
        """
        return BinopAexp(self.op,self.left.replace(x,y),self.right.replace(x,y))


    def exp(self):
        """
    ** Transforms an expression into a form consistent with Z3 solver.

    ** The return value is a string (Z3 recognizes strings as expressions with eval command);
        """
        return '(%s %s %s)' % ( self.left.exp(), self.op, self.right.exp())

    def __repr__(self):
        return '(%s %s %s)' % ( self.left, self.op, self.right)



class RelopBexp(Bexp):
    """
    Handles boolean expressions such as 
    x>1, 1<=8, (y+2)<x-1 ...
    """

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right


    def replace(self,x,y):
        """
    ** Method that handles assignment x:=y.

    ** Returns a new instance with the value of x replaced by y.
        """
        return RelopBexp(self.op,self.left.replace(x,y),self.right.replace(x,y))

    def exp(self):
        """
    ** Transforms an expression into a form consistent with Z3 solver.

    ** The return value is a string (Z3 recognizes strings as expressions with eval command);
        """

        return '(%s %s %s)' % (self.left.exp(), self.op, self.right.exp())

    def __repr__(self):
        return '{%s %s %s}' % (self.left, self.op, self.right)    


class AndBexp(Bexp):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def replace(self,x,y):
        """
    ** Method that handles assignment x:=y.

    ** Returns a new instance with the value of x replaced by y.
        """

        return AndBexp(self.left.replace(x,y), self.right.replace(x,y))

    
    def exp(self):
        """
    Transforms an expression into a form consistent with Z3 solver.

    The return value is the And(x,y) BoolRef funtion, where x and y are of 
    type Bool or type String and then evaluated to Bool form.

        """
        right=self.right.exp()
        if type(right)==str:
            right=eval(right)
            if type(right)==bool:
                if right==True:
                    right=true(str(self.right)).exp()
                else:
                    right=false(str(self.right)).exp()
        left=self.left.exp()
        if type(left)==str:
            left=eval(left)
            if type(left)==bool:
            
                if left==True:
                    left=(true(str(self.left))).exp()
                else:
                    left=false(str(self.left)).exp()
        return And(left,right)
     

    def __repr__(self):
        return '[%s /\ %s]' % (self.left, self.right)

class OrBexp(Bexp):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def replace(self,x,y):
        """
    ** Method that handles assignment x:=y.

    ** Returns a new instance with the value of x replaced by y.
        """
        return OrBexp(self.left.replace(x,y), self.right.replace(x,y))

    def exp(self):
        """
    ** Transforms an expression into a form consistent with Z3 solver.

    ** The return value is the Or(x,y) BoolRef funtion, where x and y are of 
    type Bool or type String and then evaluated to Bool form.

        """
        right=self.right.exp()
        if type(right)==str:
            right=eval(right)
        left=self.left.exp()
        if type(left)==str:
            left=eval(left)
        return Or(left,right)

    def __repr__(self):
        return '[%s \/ %s]' % (self.left, self.right)


class ImpBexp(Bexp):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def replace(self,x,y):
        """
    ** Method that handles assignment x:=y.

    ** Returns a new instance with the value of x replaced by y.
        """
        return ImpBexp(self.left.replace(x,y), self.right.replace(x,y))


    def exp(self):
        """
    ** Transforms an expression into a form consistent with Z3 solver.

    ** The return value is the Implies(x,y) BoolRef funtion, where x and y are of 
    type Bool or type String and then evaluated to Bool form.

        """
        right=self.right.exp()
        if type(right)==str:
            right=eval(right)
        left=self.left.exp()
        if type(left)==str:
            left=eval(left)
        return Implies(left, right)


    def __repr__(self):
        return '{%s --> %s}' % (self.left,self.right)   


class BimpBexp(Bexp):
    def __init__(self, left,right):
        self.left = left
        self.right= right

    def replace(self,x,y):
        """
    ** Method that handles assignment x:=y.

    ** Returns a new instance with the value of x replaced by y.
        """

        return BimpBexp(self.left.replace(x,y), self.right.replace(x,y))


    def exp(self):
        """
    ** Transforms an expression into a form consistent with Z3 solver.

    ** The return value is the x=y BoolRef funtion, where x and y are of 
    type Bool or type String and then evaluated to Bool form.

        """
        right=self.right.exp()
        if type(right)==str:
            right=eval(right)
        left=self.left.exp()
        if type(left)==str:
            left=eval(left)
        return '%s = %s' %(left,right)

    def __repr__(self):
        return '(%s <--> %s)' % (self.left,self.right)

class ForallBexp(Bexp):
    def __init__(self,var,bexp):
        self.var=VarAexp(var)
        self.expr=bexp

    def replace(self,x,y):
        """
    ** Method that handles assignment x:=y.

    ** Returns a new instance with the value of x replaced by y.
        """
        return ForallBexp(self.var.replace(x,y),self.expr.replace(x,y))

    def __repr__(self):
        return "$forall %s : %s$" % (self.var,self.expr)


    def exp(self):
        """
    ** Transforms an expression into a form consistent with Z3 solver.

    ** The return value is the ForAll(x,bexp) BoolRef funtion, where x is of 
    type Int and bexp a BoolRef value.

        """
        expr=self.expr.exp()
        if type(expr)==str:
            expr=eval(expr)
        return ForAll(eval(self.var.exp()), expr)



class ExistsBexp(Bexp):
    def __init__(self,var,bexp):
        self.var=VarAexp(var)
        self.expr=bexp

    def replace(self,x,y):
        """
    ** Method that handles assignment x:=y.

    ** Returns a new instance with the value of x replaced by y.
        """
        return ExistsBexp(self.var.replace(x,y),self.expr.replace(x,y))

    def __repr__(self):
        return "$exists %s : %s$" % (self.var,self.expr)


    def exp(self):
        """
    ** Transforms an expression into a form consistent with Z3 solver.

    ** The return value is the Exists(x,bexp) BoolRef funtion, where x is of 
    type Int and bexp a BoolRef value.

        """

        expr=self.expr.exp()
        if type(expr)==str:
            expr=eval(expr)
        return Exists(eval(self.var.exp()), expr)



class NotBexp(Bexp):
    def __init__(self,expr):
        self.expr=expr

    def replace(self,x,y):
        """
    ** Method that handles assignment x:=y.

    ** Returns a new instance with the value of x replaced by y.
        """
        return NotBexp(self.expr.replace(x,y))

    def exp(self):
        """
    ** Transforms an expression into a form consistent with Z3 solver.

    ** The return value is the Not(x) BoolRef funtion, where x is of 
    type Bool or type String and then evaluated to Bool form.

        """
        expr=self.expr.exp()
        if type(expr)==str:
            expr=eval(expr)
        return Not(expr)

    def __repr__(self):
        return '~(%s)' % self.expr

class true(Bexp):
    def __init__(self,expr):
        self.expr=expr

    def exp(self):
        return BoolSort().cast(True)

    def __repr__(self):
        return 'true(%s)'%self.expr

    def replace(self,x,y):
        return self


class false(Bexp):
    def __init__(self,expr):
        self.expr=expr

    def exp(self):
        return BoolSort().cast(False)

    def __repr__(self):
        return 'false(%s)'%expr

    def replace(self,x,y):
        return self


        
        
class PreCondition(Statement):
    def __init__(self,condition):
        self.pre=condition

    def replace(self,x,y):
        """
    ** Method that handles assignment x:=y.

    ** Returns a new instance with the value of x replaced by y.
        """
        return PreCondition(self.pre.replace(x,y))

    def exp(self):
        """
    ** Transforms an expression into a form consistent with Z3 solver.

    ** Computes the exp value of the precondition.

        """
        return self.pre.exp()
       
    def __repr__(self):
        return "(%s)" %self.pre

        
        
class PostCondition(Statement):
    def __init__(self,condition):
        self.post=condition


    def exp(self):
        """
    ** Transforms an expression into a form consistent with Z3 solver.

    ** Computes the exp value of the postcondition.

        """
        return self.post.exp()

    def replace(self,x,y):
        """
    ** Method that handles assignment x:=y.

    ** Returns a new instance with the value of x replaced by y.
        """
        return PostCondition(self.post.replace(x,y))
    
   
    def __repr__(self):
        return "(%s)" % self.post

   
        #This is statement to be easier to select in Result
class LoopInvariant(Statement):
    def __init__(self, condition):
        self.inv=condition

    def replace(self,x,y):
        """
    ** Method that handles assignment x:=y.

    ** Returns a new instance with the value of x replaced by y.
        """
        return LoopInvariant(self.inv.replace(x,y))


    def exp(self):
        """
    ** Transforms an expression into a form consistent with Z3 solver.

    ** Computes the exp value of the loop invariant.

        """
        return self.inv.exp()

    def __repr__(self):
        return "(%s)"% self.inv
            
