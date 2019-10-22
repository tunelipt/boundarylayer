import numpy as np



def discr(n, r):

    if r==1:
        dx = 1.0 / (n-1)
        return dx * np.arange(n) #[dx * x for x in range(n)]

    m = n-1
    a0 = (1.0 - r) / (1.0 - (r**m))
    v = np.zeros(n)#  [0 for x in range(n)]
    for i in range(1,n):
        v[i] = v[i-1] + a0* r ** (i-1.0)
    return(v)



def applydiscr(d, x1, x2):
    l = float(x2 - x1)
    return d*l + x1 #[x * l + x1 for x in d]


def pointdistr(x1=0.0, x2=1.0, n=11, r=1.0):

    d = discr(n, r)
    return applydiscr(d, x1, x2)


def parsenumlst(s):
    plst = []
    for r in s.split():
        plst = plst + parserange(r)
    return plst

def parseddot(s):
    if s.find("~") >= 0:
        raise RuntimeError("Can not mix : with ~")
    
    d1 = s.find(':')
    if d1 < 0:
        return [float(d1)]
    x1 = float(s[:d1])
    
    d2 = s.find(':', d1+1)

    if d2 < 0:
        x2 = float(s[(d1+1):])
        dx = 1.0
    else:
        x2 = float(s[(d1+1):d2])
        dx = float(s[(d2+1):])

    #return x1, x2, dx
    return np.linspace(x1, x2, (x2-x1)/dx+1)

def parsetilde(s):

    if s.find(':') >= 0:
        raise RuntimeError("Can not mix : with ~")

    
            
            
    d1 = s.find('~')
    if d1 < 0:
        return np.array([float(d1)])
    x1 = float(s[:d1])
    
    d2 = s.find('~', d1+1)
    
    if d2 < 0:
        x2 = float(s[(d1+1):])
        return [x1,x2]
    else:
        x2 = float(s[(d1+1):d2])

    d3 = s.find('~', d2+1)

    if d3 < 0:
        n = int(s[(d2+1):])
        r = 1.0
    else:
        n = int(s[(d2+1):d3])
        r = float(s[(d3+1):])

    d = discr(n,r)

    return applydiscr(d, x1, x2)

    

    
    
def parserange(s):
    
    if s.find(':') >= 0:
        return [float(x) for x in parseddot(s)]
    elif s.find('~') >= 0:
        return [float(x) for x in parsetilde(s)]
    else:
        return [float(s)]


    
    

