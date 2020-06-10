"""
@author  JungBok Cho
@version 1.0

GEDCOM parser design

Create empty dictionaries of individuals and families
Ask user for a file name and open the gedcom file
Read a line
Skip lines until a FAM or INDI tag is found
    Call functions to process those two types
Print descendant chart when all lines are processed

Processing an Individual
Get pointer string
Make dictionary entry for pointer with ref to Person object
Find name tag and identify parts (surname, given names, suffix)
Find FAMS and FAMC tags; store FAM references for later linkage
Skip other lines

Processing a family
Get pointer string
Make dictionary entry for pointer with ref to Family object
Find HUSB WIFE and CHIL tags
    Add included pointer to Family object
    [Not implemented ] Check for matching references in referenced Person object
        Note conflicting info if found.
Skip other lines

Print info from the collect of Person objects
Read in a person number
Print pedigree chart
"""


#-----------------------------------------------------------------------
import GEDtest


class Person():
    # Stores info about a single person
    # Created when an Individual (INDI) GEDCOM record is processed.
    #-------------------------------------------------------------------

    def __init__(self, ref):
        # Initializes a new Person object, storing the string (ref) by
        # which it can be referenced.
        self._id = ref
        self._asSpouse = []  # use a list to handle multiple families
        self._asChild = None
        self._birthdate = ''
        self._birthplace = ''
        self._deathdate = ''
        self._deathplace = ''

    def addName(self, names):
        # Extracts name parts from a list of name and stores them
        self._given = names[0]
        self._surname = names[1]
        self._suffix = names[2]

    def addBirthDate(self, BirthDate):
        # Add birth date
        self._birthdate = BirthDate

    def addBirthPlace(self, BirthPlace):
        # Add birth place
        self._birthplace = BirthPlace

    def addDeathDate(self, DeathDate):
        # Add death date
        self._deathdate = DeathDate

    def addDeathPlace(self, DeathPlace):
        # Add death place
        self._deathplace = DeathPlace

    def addIsSpouse(self, famRef):
        # Adds the string (famRef) indicating family in which this person
        # is a spouse, to list of any other such families
        self._asSpouse += [famRef]

    def addIsChild(self, famRef):
        # Stores the string (famRef) indicating family in which this person
        # is a child
        self._asChild = famRef

    def printDescendants(self, prefix=''):
        # print info for this person and then call method in Family
        print(prefix,end='')
        print(self)
        # recursion stops when self is not a spouse
        for fam in self._asSpouse:
            families[fam].printFamily(self._id,prefix)

    def name (self):
        # returns a simple name string 
        return self._given + ' ' + self._surname.upper() \
               + ' ' + self._suffix

    def __str__(self):
        # returns a string representing all info in the Person instance
        toString = self.name()
        if not self._suffix:
            toString = toString[0:len(toString) - 1]
        if self._birthdate != '':
            toString += ', n: ' + self._birthdate[0:len(self._birthdate) - 1]
            if self._birthplace != '':
                toString += ' ' + self._birthplace[0:len(self._birthplace) - 1]
        if self._deathdate != '':
            toString += ', d: ' + self._deathdate[0:len(self._deathdate) - 1] \
                        + ' ' + self._deathplace[0:len(self._deathplace) - 1]
        return toString

    def isDescendant(self, descendant):
        # check if the identified person is an descendant of self
        if self._id == descendant:
            return True
        else:
            if self.helperIsDescendant(descendant):
                return True
            else:
                return False

    def helperIsDescendant(self, descendant):
        # helper function of isDescendant function
        for fam in self._asSpouse:
            for child in families[fam]._children:
                if persons[child]._id == descendant:
                    return True
                else:
                    if persons[child].helperIsDescendant(descendant):
                        return True

    def printAncestors(self, space):
        # 1st version of printing every ancestor of self
        if not self._asChild:
            print("0", self)
        else:
            self.helperPrintAncestors(space, 0)

    def helperPrintAncestors(self, space, num):
        # helper function of the printAncestors function, using post-order method
        if num != 0:
            space += '   '
        if self._asChild:
            persons[families[self._asChild]._husband].helperPrintAncestors(space, num + 1)
            persons[families[self._asChild]._wife].helperPrintAncestors(space, num + 1)
            print(space + str(num), persons[self._id])
        else:
            print(space + str(num), persons[self._id])

    def printAncestorsV2(self, space):
        # 2nd version of printing every ancestor of self
        if not self._asChild:
            print("0", self)
        else:
            self.helperPrintAncestorsV2(space, 0)

    def helperPrintAncestorsV2(self, space, num):
        # helper function of the printAncestorsV2 function, using in-order method
        if num != 0:
            space += '   '
        if self._asChild:
            persons[families[self._asChild]._husband].helperPrintAncestorsV2(space, num + 1)
            print(space + str(num), persons[self._id])
            persons[families[self._asChild]._wife].helperPrintAncestorsV2(space, num + 1)
        else:
            print(space + str(num), persons[self._id])

    def printCousins(self, n = 1):
        # print nth cousins of the person
        parentList = list()
        toExcludeList = list()
        siblingList = list()
        cousinList = list()

        parentList = self.getParent(parentList, toExcludeList, n)
        siblingList = self.getSibling(parentList, toExcludeList, siblingList)
        for child in siblingList:
            persons[child].getCousin(cousinList, n)
        self.printCousinResult(cousinList, n)

    def getParent(self, parentList, toExcludeList, n):
        # get parents of the person
        if self._asChild is not None:
            if n > 0:
                if n == 1:
                    toExcludeList.append(families[self._asChild]._husband)
                    toExcludeList.append(families[self._asChild]._wife)
                persons[families[self._asChild]._husband].getParent(parentList, toExcludeList, n - 1)
                persons[families[self._asChild]._wife].getParent(parentList, toExcludeList, n - 1)
                return parentList
            elif n == 0:
                return parentList.append(self._asChild)
        else:
            return []

    def getSibling(self, parentList, toExcludeList, siblingList):
        # get sibling of the parent
        for child in parentList:
            for sibling in families[child]._children:
                if sibling not in toExcludeList:
                    siblingList.append(sibling)
        return siblingList

    def getCousin(self, cousinList, n):
        # get cousins of the person
        if self._asSpouse:
            for child in self._asSpouse:
                for cousin in families[child]._children:
                    if n > 1:
                        persons[cousin].getCousin(cousinList, n - 1)
                    else:
                        cousinList.append(cousin)

    def printCousinResult(self, cousinList, n):
        # print the cousins found
        if str(n)[-1] == '1':
            print(str(n) + 'st cousins for ' + self.name())
        elif str(n)[-1] == '2':
            print(str(n) + 'nd cousins for ' + self.name())
        elif str(n)[-1] == '3':
            print(str(n) + 'rd cousins for ' + self.name())
        else:
            print(str(n) + 'th cousins for ' + self.name())

        if cousinList:
            for cousin in cousinList:
                print(" ", persons[cousin])
        else:
            print('  No cousins')

# end of class Person

#-----------------------------------------------------------------------

class Family():
    # Stores info about a family
    # Created when an Family (FAM) GEDCOM record is processed.
    #-------------------------------------------------------------------

    def __init__(self, ref):
        # Initializes a new Family object, storing the string (ref) by
        # which it can be referenced.
        self._id = ref
        self._husband = None
        self._wife = None
        self._children = []
        self._marriagedate = ''
        self._marriageplace = ''

    def addHusband(self, personRef):
        # Stores the string (personRef) indicating the husband in this family
        self._husband = personRef

    def addWife(self, personRef):
        # Stores the string (personRef) indicating the wife in this family
        self._wife = personRef

    def addChild(self, personRef):
        # Adds the string (personRef) indicating a new child to the list
        self._children += [personRef]

    def addMarriageDate(self, MarriageDate):
        # Add marriage date
        self._marriagedate = MarriageDate[0:len(MarriageDate)-1]

    def addMarriagePlace(self, MarriagePlace):
        # Add marriage place
        self._marriageplace = MarriagePlace[0:len(MarriagePlace)-1]

    def printFamily(self, firstSpouse, prefix):
        # Used by printDecendants in Person to print spouse
        # and recursively invole printDescendants on children
        if prefix != '': prefix = prefix[:-2]+'  '
        if self._husband == firstSpouse:
            if self._wife:  # make sure value is not None
                print(prefix + '+', end='')
                print(persons[self._wife], end='')
                if self._marriagedate:
                    print(', m: ', end='')
                    print(self._marriagedate, end=' ')
                    print(self._marriageplace)
        else:
            if self._husband:  # make sure value is not None
                print(prefix + '+', end='')
                print(persons[self._husband])
        for child in self._children:
             persons[child].printDescendants(prefix+'|--')

    def __str__(self):
        # toString method
        if self._husband: # make sure value is not None
            husbString = ' Husband: ' + self._husband
        else: husbString = ''
        if self._wife: # make sure value is not None
            wifeString = ' Wife: ' + self._wife
        else: wifeString = ''
        if self._children != []: childrenString = ' Children: ' + ','.join(self._children)
        else: childrenString = ''
        return husbString + wifeString + childrenString

# end of class Family

#-----------------------------------------------------------------------
# Global dictionaries used by Person and Family to map INDI and FAM identifier
# strings to corresponding object instances

persons = dict()  # saves references to all of the Person objects
families = dict() # saves references to all of the Family objects

#-----------------------------------------------------------------------

def processGEDCOM(file):

    def getPointer(line):
        # A helper function used in multiple places in the next two functions
        # Depends on the syntax of pointers in certain GEDCOM elements
        # Returns the string of the pointer without surrounding '@'s or trailing
        return line[8:].split('@')[0]

    def processPerson(newPerson):
        nonlocal line
        line = f.readline()
        while line[0] != '0': # process all lines until next 0-level
            tag = line[2:6]  # substring where tags are found in 0-level elements
            if tag == 'NAME':
                names = line[6:].split('/')  #surname is surrounded by slashes
                names[0] = names[0].strip()
                names[2] = names[2].strip()
                newPerson.addName(names)
            elif tag == 'FAMS':
                newPerson.addIsSpouse(getPointer(line))
            elif tag == 'FAMC':
                newPerson.addIsChild(getPointer(line))
            # read to go to next line
            line = f.readline()
            ## add code here to look for other fields
            if tag == 'BIRT' or line[2:6] == 'BIRT':
                line = f.readline()
                if line[2:6] == 'DATE' :
                    newPerson.addBirthDate(line[7:])
                    line = f.readline()
                if line[2:6] == 'PLAC' :
                    newPerson.addBirthPlace(line[7:])
                    line = f.readline()
            if tag == 'DEAT' or line[2:6] == 'DEAT':
                line = f.readline()
                if line[2:6] == 'DATE' :
                    newPerson.addDeathDate(line[7:])
                    line = f.readline()
                if line[2:6] == 'PLAC':
                    newPerson.addDeathPlace(line[7:])
                    line = f.readline()

    def processFamily(newFamily):
        nonlocal line
        line = f.readline()
        while line[0] != '0':  # process all lines until next 0-level
            tag = line[2:6]
            if tag == 'HUSB':
                newFamily.addHusband(getPointer(line))
            elif tag == 'WIFE':
                newFamily.addWife(getPointer(line))
            elif tag == 'CHIL':
                newFamily.addChild(getPointer(line))
            # read to go to next line
            line = f.readline()
            ## add code here to look for other fields 
            if tag == 'MARR' or line[2:6] == 'MARR':
                line = f.readline()
                if line[2:6] == 'DATE' :
                    newFamily.addMarriageDate(line[7:])
                    line = f.readline()
                if line[2:6] == 'PLAC':
                    newFamily.addMarriagePlace(line[7:])
                    line = f.readline()

    ## f is the file handle for the GEDCOM file, visible to helper functions
    ## line is the "current line" which may be changed by helper functions

    f = open (file)
    line = f.readline()
    while line != '':  # end loop when file is empty
        fields = line.strip().split(' ')
        # print(fields)
        if line[0] == '0' and len(fields) > 2:
            # print(fields)
            if (fields[2] == "INDI"):
                ref = fields[1].strip('@')
                ## create a new Person and save it in mapping dictionary
                persons[ref] = Person(ref)
                ## process remainder of the INDI record
                processPerson(persons[ref])

            elif (fields[2] == "FAM"):
                ref = fields[1].strip('@')
                ## create a new Family and save it in mapping dictionary
                families[ref] = Family(ref)
                ## process remainder of the FAM record
                processFamily(families[ref])

            else:    # 0-level line, but not of interest -- skip it
                line = f.readline()
        else:    # skip lines until next candidate 0-level line
            line = f.readline()


def _main():
    print("\nWelcome to Family Tree program!\n")
    filename = input("Type the name of the GEDCOM file: ")
    print()
    processGEDCOM(filename)
    GEDtest.runtests(persons, families)


if __name__ == '__main__':
    _main()

