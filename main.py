#Sloan Kim Parser 2.2
import re
import sys

#tree
class Tree:
  def __init__(self,op=None,preop=None,midop=None,postop=None):
    if op!=None:
      self.op = op
    else:
      self.op = None

    if preop!=None and isinstance(preop, Tree):
        self.preop = preop
    else:
      self.preop = None

    if midop!=None and isinstance(midop, Tree):
      self.midop = midop
    else:
      self.midop = None
    
    if postop!=None and isinstance(postop, Tree):
      self.postop = postop
    else:
      self.postop = None

  def printTree(self, num):
    if self is not None:
      for i in range(1,num): 
        outfile.write("      ")
      if re.fullmatch(r'if', self.op):
        outfile.write('IF-STATEMENT\n')
      elif re.fullmatch(r'while', self.op):
        outfile.write('WHILE-LOOP\n')
      elif re.fullmatch(NUM, self.op):
        outfile.write('NUMBER ' + self.op + '\n')
      elif re.fullmatch(IDE, self.op):
        outfile.write('IDENTIFIER ' + self.op + '\n')
      else:
        outfile.write('SYMBOL ' + self.op + '\n')
  
    if self.preop:
      self.preop.printTree(num+1)
    if self.midop:
      self.midop.printTree(num+1)
    if self.postop:
      self.postop.printTree(num+1)
    
  def listPreorder(self):
    if self.op:
      list.append(self.op)
      if self.preop:
        self.preop.listPreorder()
      if self.postop:
        self.postop.listPreorder()

#parser
class Parser:
  def __init__(self,tokens):
    self.tokens=tokens
    self.index=-1
    self.advance()

  def advance(self, ):
    if self.index+1<len(self.tokens):
      self.index+=1
      self.current=self.tokens[self.index]
      return self.current
    else:
      return None

  def parse(self):
    res=self.statement()
    return res

  def statement(self):
    ast = self.baseStatement()
    if self.current is not None:
      while re.fullmatch(r'\;', self.current):
        op= self.current
        self.advance()
        ast=Tree(op, ast, None, self.baseStatement())
      return ast
      
  def baseStatement(self):
    if re.fullmatch(r'if',self.current):
      return self.ifStatement()
    elif re.fullmatch(r'while',self.current):
      return self.whileStatement()
    elif re.fullmatch(r'skip',self.current):
      op=self.current
      self.advance()
      return Tree(op,None,None,None)
    else:
      return self.assignment()

  def assignment(self):
    if re.fullmatch(IDE, self.current):
      preop=Tree(self.current,None,None,None)
      self.advance()
      if re.fullmatch(r':=',self.current):
        op=self.current
        self.advance()
        return Tree(op,preop,None,self.expression())
      else:
        raise Exception("Missing :=", outfile.write("Missing :="))
    else:
      raise Exception("Assignment starts with identifier", outfile.write("Assignment starts with identifier"))

  def ifStatement(self):
    op=self.current
    self.advance()
    preop=self.expression()
    if re.fullmatch(r'then', self.current):
      self.advance()
      midop=self.statement()
      if re.fullmatch(r'else',self.current):
        self.advance()
        postop=self.statement()
        if re.fullmatch(r'endif', self.current):
          self.advance()
          return Tree(op,preop,midop,postop)
        else:
          raise Exception("Missing endif",outfile.write("Missing endif"))
      else:
        raise Exception("Missing else",outfile.write("Missing else"))
    else:
      raise Exception("Missing then",outfile.write("Missing then"))

  def whileStatement(self):
    op=self.current
    self.advance()
    preop=self.expression()
    if re.fullmatch(r'do', self.current):
      self.advance()
      postop=self.statement()
      if re.fullmatch(r'endwhile',self.current):
        self.advance()
        return Tree(op,preop,None,postop)
      else:
        raise Exception("Missing endwhile", outfile.write("Missing endwhile"))
    else:
      raise Exception("Missing do", outfile.write("Missing do"))

  def expression(self):
    ast = self.term()
    if self.current is not None:
      while re.fullmatch(r'\+',self.current):
        op=self.current
        self.advance()
        ast=Tree(op,ast,None,self.term())
      return ast

  def term(self):
    ast = self.factor()
    if self.current is not None:
      while re.fullmatch(r'\-',self.current):
        op=self.current
        self.advance()
        ast=Tree(op,ast,None,self.factor())
      return ast

  def factor(self):
    ast = self.piece()
    if self.current is not None:
      while re.fullmatch(r'/',self.current):
        op=self.current
        self.advance()
        ast=Tree(op,ast,None,self.piece())
      return ast

  def piece(self):
    ast = self.element()
    if self.current is not None:
      while re.fullmatch(r'\*',self.current):
        op=self.current
        self.advance()
        ast=Tree(op,ast,None,self.element())
      return ast

  def element(self):
    if re.fullmatch(r'\(',self.current):
      self.advance()
      ast = self.expression()
      if re.fullmatch(r'\)',self.current):
        self.advance()
        return ast
      else:
        raise Exception("Missing )", outfile.write("Missing )"))
    else:
      if re.fullmatch(NUM, self.current):
        op=self.current
        self.advance()
        return Tree(op,None,None,None)
      elif re.fullmatch(IDE, self.current):
        op=self.current
        self.advance()
        return Tree(op,None,None,None)


#lexer
infile=open( sys.argv[1],'r')
outfile=open( sys.argv[2], 'w')

PAT=r'[a-zA-Z][a-zA-Z0-9]*|[0-9]+|:=|[+\-*\/\(\);]|if|endif|else|then|while|do|endwhile|skip|\S+'

IDE=r'^[a-zA-Z][a-zA-Z0-9]*$'
NUM=r'^[0-9]+$'
KEY=r'^if|endif|else|then|while|do|endwhile|skip$'
SYM=r'^:=|[+\-*\/\(\);]$'

r=re.findall(PAT,infile.read())
outfile.write('\nTokens: \n')
tokens=[]
error=False

for i in r:
  if re.fullmatch(KEY,i):
    outfile.write('KEYWORD '+i+'\n')
    tokens+=[i]
  elif re.fullmatch(NUM,i):
    outfile.write('NUMBER '+i+'\n')
    tokens+=[i]
  elif re.fullmatch(IDE,i):
    outfile.write('IDENTIFIER '+i+'\n')
    tokens+=[i]
  elif re.fullmatch(SYM,i):
    outfile.write('SYMBOL '+i+'\n')
    tokens+=[i]
  else:
    outfile.write('ERROR READING "'+ i[0]+'"\n')
    error=True
    break
    
if error==False:
  outfile.write('\nAST: \n')
  parser=Parser(tokens)
  ast=parser.parse()
  if parser.advance() is not None:
    raise Exception("Wrong syntax, tokens left after parsing",outfile.write("Wrong syntax, tokens left after parsing"))
  else:
    ast.printTree(1)
outfile.write('\n')

#evaluator
list=[]
ast.listPreorder()

while len(list)>1:
  i=0
  while i < len(list):
    if re.fullmatch(NUM, list[i]):
      if re.fullmatch(NUM, list[i-1]):
        if re.fullmatch(SYM, list[i-2]):
          if eval(list[i]) != 0:
            new = str(int(eval(list[i-1]+list[i-2]+list[i])))
          else: 
            raise Exception("The divisor cannot be 0", outfile.write("The divisor cannot be 0"))
            break
          list.pop(i)
          list.pop(i-1)
          list.pop(i-2)
          list.insert(i-2,new)
          i+=1
        else: i+=1
      else: i+=1
    else: i+=1

outfile.write("Output: ")
outfile.write(list[0])

infile.close()
outfile.close()