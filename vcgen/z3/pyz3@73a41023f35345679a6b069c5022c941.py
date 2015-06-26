from z3 import *
import PySide

s1,s2,s3,f1,f2,f3=Reals('s1 s2 s3 f1 f2 f3')

solve( s1+f1==0,
	s1+f2>0,
	s1+f2<80,
	s1+f3>=90,
	s2+f1>0,
	s2+f2>0,
	s2+f3>90,
	s3+f3==100
	)