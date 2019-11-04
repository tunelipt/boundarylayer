
class ChannelConfig(object):

    def __init__(self, nchans, chans=None, istart=1):
        if chans is None:
            self.chans = ["Chan {}".format(i + istart) for i in range(nchans)]
        else:
            self.chans = [chans[i] for i in range(nchans)]

        self.nch = nchans
        self.selected = [False for i in range(self.nch)]

    def available(self, chidx):
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
    

