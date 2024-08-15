import math

class TableEntry:
    def __init__(self, terms, dimension, binaryRepresentation=None):
        self.terms = terms
        self.dim = dimension
        self.binRep = None
        if binaryRepresentation is not None:
            self.binRep = binaryRepresentation
        elif len(terms) == 0:
            self.binRep = ""
        else:
            t1 = self.generateBinaryRep(self)
            self.binRep = t1.getBinaryRep()
    
    def setTerms(self, terms):
        self.terms = terms

    def addTerms(self, terms):
        self.setTerms(self.terms + terms)
        self.removeRepeatedTerms()
        self.terms = self.sortByGrayCode(self.terms)

    def getTerms(self):
        return self.terms

    def setBinaryRep(self, binaryRepresentation):
        self.binRep = binaryRepresentation

    def getBinaryRep(self):
        return self.binRep

    def setDimension(self, dim):
        self.dim = dim

    def getDimension(self):
        return self.dim

    def generateBinaryRep(self, t):
        if not (math.log(len(t.terms), 2)).is_integer():
            return None
        terms = self.sortByGrayCode(t.terms)
        dimension = t.getDimension()
        currBinRep = t.getBinaryRep()
        if len(terms) == 1:
            return TableEntry([terms[0]], dimension, self.numberToBinary(terms[0]))
        elif len(terms) == 2:
            t1 = TableEntry([terms[0]], dimension, self.numberToBinary(terms[0]))
            t2 = TableEntry([terms[1]], dimension, self.numberToBinary(terms[1]))
            return t1.mergeEntry(t2)
        else:
            halfwayPoint = len(terms) // 2
            firstHalf = TableEntry(terms[:halfwayPoint], dimension, currBinRep)
            secondHalf = TableEntry(terms[halfwayPoint:], dimension, currBinRep)
            t1 = self.generateBinaryRep(firstHalf)
            t2 = self.generateBinaryRep(secondHalf)
            t3 = t1.mergeEntry(t2)
            return t3

    def numberToBinary(self, num):
        if num >= 2**self.dim or num < 0:
            return None
        s = bin(num)[2:]
        s = '0' * (self.dim - len(s)) + s
        return s

    def mergeEntry(self, t2):
        mismatches = self.findMismatches(t2.getBinaryRep())
        newEntry = TableEntry(self.getTerms(), self.getDimension(), self.getBinaryRep())
        if len(mismatches) == 0:
            newEntry.setTerms(self.terms + t2.terms)
            newEntry.removeRepeatedTerms()
            return newEntry
        elif len(mismatches) == 1:
            newBinRep = self.replaceAt(newEntry.getBinaryRep(), mismatches[0], "-")
            newEntry.setBinaryRep(newBinRep)
            newEntry.addTerms(t2.getTerms())
            return newEntry
        else:

            return None
    def findMismatches(self, rep):
        mismatches = []
        for i in range(len(self.binRep)):
            if self.binRep[i] != rep[i]:
                mismatches.append(i)
        return mismatches
    
    def is_adjacent(self, t2):
        mismatches = self.findMismatches(t2.getBinaryRep())  # 获取与t2的不匹配位置
        return len(mismatches) <= 1  # 如果不匹配位置的数量不超过1，则返回True
    
    def removeRepeatedTerms(self):
        seen = set()
        self.terms = [x for x in self.terms if not (x in seen or seen.add(x))]

    def replaceAt(self, value, index, replacement):
        return value[:index] + replacement + value[index + len(replacement):]

    def sortByGrayCode(self, terms):
        return sorted(terms, key=lambda x: self.grayCodeLocation(x))

    def grayCodeLocation(self, num):
        mask = num >> 1
        while mask != 0:
            num ^= mask
            mask >>= 1
        return num

# 单元测试代码
import unittest

class TestTableEntry(unittest.TestCase):
    def test_constructor(self):
        terms = [0, 1]
        dimension = 2
        entry = TableEntry(terms, dimension)
        self.assertEqual(len(entry.getTerms()), 2)
        self.assertEqual(entry.getDimension(), dimension)

    def test_addTerms(self):
        entry = TableEntry([], 2)
        entry.addTerms([2, 3])
        self.assertTrue(2 in entry.getTerms() and 3 in entry.getTerms())

    def test_generateBinaryRep(self):
        terms = [0, 1]
        dimension = 2
        entry = TableEntry(terms, dimension)

    def test_mergeEntry(self):
        terms1 = [0]
        terms2 = [1]
        entry1 = TableEntry(terms1, 2, '00')
        entry2 = TableEntry(terms2, 2, '01')
        merged_entry = entry1.mergeEntry(entry2)
        self.assertTrue(0 in merged_entry.getTerms() and 1 in merged_entry.getTerms())

    def test_sortByGrayCode(self):
        entry = TableEntry([2, 3, 0, 1], 2)
        entry.terms = entry.sortByGrayCode(entry.getTerms())
        self.assertEqual(entry.getTerms(), [0, 1, 3, 2])

if __name__ == '__main__':
    unittest.main()