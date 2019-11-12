import math

def num_string(x, n=3):
    return ('{}'.format(x + 10**n))[1:]

class ChannelConfig(object):

    def __init__(self, nchans, chans=None, addref=True, istart=0):

        self.addref = addref
        self.istart = istart
        
        if chans is None:
            nchars = math.ceil(math.log10(nchans+istart))
            self.chans = ["CHAN{}".format(num_string(i+istart, nchars)) for i in range(nchans)]
        else:
            self.chans = [chans[i] for i in range(nchans)]

        if addref:
            self.chans.append("REF")

        self.nconn = len(self.chans)
        self.nch = nchans
        self.selected = [False for i in range(self.nconn)]

    def isavailable(self, chidx):
        return not self.selected[chidx]
    
    def check(self, chidx):
        self.selected[chidx] = True

    def uncheck(self, chidx):
        self.selected[chidx] = False

    def findfirst(self):
        for i in range(self.nch):
            if not self.selected[i]:
                self.selected[i] = True
                return i
        return -1
    
    def names(self):
        return self.chans
    
    def nchans(self):
        return self.nch

    def save_config(self):
        return dict(kind='channel', nchans=self.nch, chans=self.chans, use=self.selected)
    

