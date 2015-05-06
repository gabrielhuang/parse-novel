'''
Created on May 5, 2015

@author: billyanhuang
'''
class Node():
    def __init__(self, data):
        self.data = data
        self.nextNode = None
        self.prevNode = None

class LinkedList():
    def __init__(self, head=None, tail=None):
        self.head = head
        self.tail = tail
    def append(self, node): #adds new node
        if not self.head:
            self.head = node
            self.tail = node
        else:
            node.nextNode = self.head
            self.head.prevNode = node
            self.head = node
    def refresh(self, node): #takes a node from the list and puts it at the head (for recency)
        if self.head == node:
            pass
        else:
            try:
                node.prevNode.nextNode = node.nextNode
            except:
                pass
            try:
                node.nextNode.prevNode = node.prevNode
            except:
                pass
            node.prevNode = None
            self.append(node)
    def printout(self):
        curnode = self.head
        while (curnode):
            print curnode.data
            if curnode == curnode.nextNode:
                break;
            curnode = curnode.nextNode
        print "---"
        