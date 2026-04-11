"""node class for cantus firmus and first species counterpoint"""
class TreeNode():
    def __init__ (self,nodenote,accept):
        self.nodenote = nodenote
        self.children = []
        self.accept = accept
        self.parent = None
        self.leapCount = 0