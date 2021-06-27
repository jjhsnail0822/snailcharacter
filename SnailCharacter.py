import random
import copy
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageOps

class SnailCharacter:
    char=[] # SnailCharacter 2-dim list
    __length=9 # width and height of the character
    __num_sets=0 # number of the connected sets
    __rank=[] # lists of the number of rank of each set
    __closed_curves=[] # lists of the number of closed curves of each sets
    __closed_curves_branch=[] # lists of the number of branches of closed curves of each sets
    __form=[] # LQTOXPHRB
    verified=False # if character verification was implemented properly

    # initialization
    def __init__(self, char_input=False, character_form=False, show_process=False):
        while True:
            if char_input: # if the input is manual
                self.char=char_input
                self.__num_sets=self.count_connected_sets()
                if self.__num_sets<1 or self.__num_sets>5: # if not 1<=set<=5, exit
                    return
                if self.is_proper()==False: # if not properly created
                    return
                if show_process:
                    print(self.__form)
                break
            else: # random character generation
                self.create_random_basic_char()
                self.__num_sets=self.count_connected_sets()
                if self.__num_sets<1 or self.__num_sets>5: # creating character until 1<=set<=5
                    continue
                if self.is_proper()==False: # if not properly created
                    continue
                if character_form: # if demanded special character form
                    if self.__form!=list(character_form):
                        if show_process:
                            print(self.__form)
                        continue
                    else:
                        break
                else:
                    break
        self.verified=True
    
    # returns manual unconfirmed character
    # use independently
    def create_manual_basic_char(bit_long_int, char_length=9):
        return_char=[[0]*char_length for i in range(char_length)] # character initialization
        bit_count=0 # for manual points
        for i in range(char_length):
            for j in range(char_length):
                if (i&1==0) and (j&1==0): # base points
                    return_char[i][j]=1
                elif ((i&1==0) and (j&1==1)) or ((i&1==1) and (j&1==0)): # manual points
                    return_char[i][j]=(bit_long_int>>bit_count)&1
                    bit_count+=1
        return return_char

    # creating random unconfirmed character
    def create_random_basic_char(self):
        self.char=[[0]*self.__length for i in range(self.__length)] # character initialization
        for i in range(self.__length):
            for j in range(self.__length):
                if (i&1==0) and (j&1==0): # base points
                    self.char[i][j]=1
                elif ((i&1==0) and (j&1==1)) or ((i&1==1) and (j&1==0)): # random points
                    self.char[i][j]=random.randint(0,1)

    # returns number of connected sets in the character
    def count_connected_sets(self):
        count=0
        checkmap=copy.deepcopy(self.char)
        def search(x,y): # recursive search
            if checkmap[y][x]==0:
                return False
            checkmap[y][x]=0
            if x>0:
                search(x-1,y)
            if x<self.__length-1:
                search(x+1,y)
            if y>0:
                search(x,y-1)
            if y<self.__length-1:
                search(x,y+1)
            return True
        for y in range(self.__length):
            for x in range(self.__length):
                if search(x,y):
                    count+=1
        return count

    # is the character properly created?
    # also sets __rank, __closed_curves, __form
    def is_proper(self, connected_sets_test=False):
        if connected_sets_test: # if you need to test the number of connected sets
            num_sets=self.count_connected_sets()
            if num_sets<1 or num_sets>5:
                return False
        self.__rank=[[0]*5 for i_ in range(5)] # lists of the number of ranks of each set
        checkmap=copy.deepcopy(self.char)
        def search_rank(x,y,index): # recursive rank searching
            if checkmap[y][x]==0:
                return False
            checkmap[y][x]=0
            self.__rank[index][self.count_rank(x,y)]+=1
            if x>0:
                search_rank(x-1,y,index)
            if x<self.__length-1:
                search_rank(x+1,y,index)
            if y>0:
                search_rank(x,y-1,index)
            if y<self.__length-1:
                search_rank(x,y+1,index)
            return True
        for i in range(self.__num_sets):
            breakpoint=False # for breaking 2 loops
            for y in range(self.__length):
                for x in range(self.__length):
                    if search_rank(x,y,i): # continue to next i
                        breakpoint=True
                        break
                if breakpoint:
                    break
        for set_rank in self.__rank:
            if set_rank[3]>2: # if rank3 exist more than 2
                return False
            if set_rank[4]>1: # if rank4 exists more than 1
                return False
            if set_rank[4]==1 and set_rank[3]!=0: # if rank4 exists, there is no rank3
                return False
            if set_rank[0]==0 and set_rank[1]==0 and set_rank[2]>8 and set_rank[3]==0 and set_rank[4]==0: # closed curve with no branches can only have 8 rank2s
                return False
            if set_rank[0]==0 and set_rank[1]==0 and set_rank[2]==11 and set_rank[3]==2: # closed curve cannot be attached each other
                return False
            if set_rank[0]==0 and set_rank[1]==0 and set_rank[2]==14 and set_rank[3]==0 and set_rank[4]==1: # same as above
                return False
        checkmap=copy.deepcopy(self.char)
        visitmap=[] # for searching algorithm
        visit_branch=[] # for searching branches
        self.__closed_curves=[] # initialization
        self.__closed_curves_branch=[] # initialization
        def search_closed_curve(x,y,index,visit=1): # recursive closed curve searching
            if checkmap[y][x]==0: # connected set already visited or confirmed
                if visitmap[y][x]==0: # already confirmed
                    return False
                else: # already visited
                    self.__closed_curves[index].append(visit-visitmap[y][x]) # found closed curve
                    # counting branches of the curve
                    branches=0
                    for i in range(visitmap[y][x],visit):
                        if visit_branch[i]>=3:
                            branches+=1
                    self.__closed_curves_branch[index].append(branches)
                    return False
            checkmap[y][x]=0
            visitmap[y][x]=visit
            visit_branch[visit]=self.count_rank(x,y)
            # do not go backward
            if x>0 and (visitmap[y][x-1]<visit-1 or visitmap[y][x-1]==0):
                search_closed_curve(x-1,y,index,visit+1)
            if x<self.__length-1 and (visitmap[y][x+1]<visit-1 or visitmap[y][x+1]==0):
                search_closed_curve(x+1,y,index,visit+1)
            if y>0 and (visitmap[y-1][x]<visit-1 or visitmap[y-1][x]==0):
                search_closed_curve(x,y-1,index,visit+1)
            if y<self.__length-1 and (visitmap[y+1][x]<visit-1 or visitmap[y+1][x]==0):
                search_closed_curve(x,y+1,index,visit+1)
            return True
        for i in range(self.__num_sets):
            breakpoint=False # for breaking 2 loops
            self.__closed_curves.append([]) # appending for index of set
            self.__closed_curves_branch.append([]) # appending for index of set
            visitmap=[[0]*self.__length for i_ in range(self.__length)] # initializing visitmap
            visit_branch=[0]*(self.__length*self.__length+1) # initializing visit_branch
            for y in range(self.__length):
                for x in range(self.__length):
                    if search_closed_curve(x,y,i): # continue to next i
                        breakpoint=True
                        break
                if breakpoint:
                    break
        for i, curves_list in enumerate(self.__closed_curves): # closed curve verification
            if not curves_list:
                continue
            if len(curves_list)>2: # closed curve does not exist more than 2
                return False
            if self.__rank[i][4]>0: # closed curve cannot accompany rank4
                return False
            for curve in curves_list:
                if curve!=8: # only allowed 3-pixel wide closed curve
                    return False
        for branches_list in self.__closed_curves_branch: # branch verification
            if not branches_list:
                continue
            for branch in branches_list:
                if branch>1: # only allowed 0 or 1 branch in 1 closed curve
                    return False
        # form applying
        self.__form=[]
        for i in range(self.__num_sets):
            if self.__rank[i][0]|self.__rank[i][3]|self.__rank[i][4]==0 and not self.__closed_curves[i]:
                self.__form.append('L')
            if self.__rank[i][0]==1:
                self.__form.append('Q')
            if self.__rank[i][3]==1 and not self.__closed_curves[i]:
                self.__form.append('T')
            if self.__rank[i][3]==0 and len(self.__closed_curves[i])==1:
                self.__form.append('O')
            if self.__rank[i][4]==1:
                self.__form.append('X')
            if self.__rank[i][3]==1 and len(self.__closed_curves[i])==1:
                self.__form.append('P')
            if self.__rank[i][3]==2 and not self.__closed_curves[i]:
                self.__form.append('H')
            if self.__rank[i][3]==2 and len(self.__closed_curves[i])==1:
                self.__form.append('R')
            if self.__rank[i][3]==2 and len(self.__closed_curves[i])==2:
                self.__form.append('B')
        self.sorting_form() # sorting character properties
        return True

    # returns value of that coordinate
    def point(self,x,y):
        if x<0 or x>=self.__length or y<0 or y>=self.__length:
            return 0
        else:
            return self.char[y][x]

    # counting rank of the point
    def count_rank(self,x,y):
        return self.point(x-1,y)+self.point(x+1,y)+self.point(x,y-1)+self.point(x,y+1)

    # sorting character properties in order 'LQTOXPHRB'
    def sorting_form(self):
        sortlist=['L','Q','T','O','X','P','H','R','B']
        for i in range(len(self.__form)-1):
            for j in range(i+1, len(self.__form)):
                if sortlist.index(self.__form[i])>sortlist.index(self.__form[j]):
                    self.__form[i],self.__form[j]=self.__form[j],self.__form[i]
                    self.__rank[i],self.__rank[j]=self.__rank[j],self.__rank[i]
                    self.__closed_curves[i],self.__closed_curves[j]=self.__closed_curves[j],self.__closed_curves[i]
                    self.__closed_curves_branch[i],self.__closed_curves_branch[j]=self.__closed_curves_branch[j],self.__closed_curves_branch[i]

    # returns form in string
    def get_form(self):
        return "".join(self.__form)

    # showing the character in python raw list
    def show_list(self):
        print(self.char)

    # showing the character in text output
    def show_text(self):
        for i in self.char:
            for j in i:
                print(j,end='')
            print()

    # showing the character directly in image
    def show_image(self):
        plt.title("".join(self.__form))
        plt.imshow(self.char, cmap='binary')
        plt.show()

    # saving into image file, png 144*144px
    # todo
    def save_image(self,path=False,random_index=True):
        if random_index:
            filename="".join(self.__form)+str(random.random())+'.png'
        else:
            filename="".join(self.__form)+'.png'
        img=Image.fromarray(np.logical_not(np.uint8(np.array(self.char)).astype(int)*255))
        img=img.resize((144,144))
        if path:
            img.save(path+filename)
        else:
            img.save(filename)

from tqdm import tqdm

def work(start, end):
    for i in tqdm(range(start,end)):
        sc=SnailCharacter(char_input=SnailCharacter.create_manual_basic_char(i))
        if sc.verified:
            sc.show_image()

from itertools import combinations_with_replacement

formtuple=[]
formlist=[]

for i in range(1,6):
    formtuple+=list(combinations_with_replacement('LQTOXPHRB',i))

for form in formtuple:
    formlist.append("".join(list(form)))

already_exist_forms=[
    'B',
    'H',
    'HB',
    'HR',
    'LH',
    'LLB',
    'LLH',
    'LLLH',
    'LLLLH',
    'LLLLO',
    'LLLLP',
    'LLLLQ',
    'LLLLT',
    'LLLO',
    'LLLOH',
    'LLLOO',
    'LLLOP',
    'LLLPP',
    'LLLQ',
    'LLLQH',
    'LLLQO',
    'LLLQP',
    'LLLQQ',
    'LLLQT',
    'LLLT',
    'LLLTO',
    'LLOH',
    'LLP',
    'LLQOP',
    'LLQP',
    'LLQPP',
    'LLQQH',
    'LLQQP',
    'LLQQQ',
    'LLQT',
    'LLR',
    'LLT',
    'LLTO',
    'LLTOO',
    'LLTTO',
    'LLXH',
    'LOH',
    'LOOOO',
    'LOPH',
    'LOXH',
    'LPP',
    'LQH',
    'LQOH',
    'LQOX',
    'LQPPP',
    'LQQ',
    'LQQH',
    'LQQOH',
    'LQQPP',
    'LQQQO',
    'LQQQX',
    'LQQTH',
    'LQQTO',
    'LQTOH',
    'LQTP',
    'LR',
    'LRR',
    'LT',
    'LTH',
    'LTOH',
    'LTOOO',
    'LTOX',
    'LTR',
    'LTT',
    'LTTTT',
    'OH',
    'OOOOX',
    'OOOR',
    'P',
    'PH',
    'PHH',
    'PR',
    'QHH',
    'QOXH',
    'QPPPP',
    'QQOPH',
    'QQPH',
    'QQQH',
    'QQQQB',
    'QQQQH',
    'QQQTO',
    'QQQTR',
    'QQQTT',
    'QQQXB',
    'QQTP',
    'QTH',
    'QTOOH',
    'QTTO',
    'QTTTT',
    'TH',
    'THH',
    'TOO',
    'TOOH',
    'TOOOO',
    'TR',
    'TTOP',
    'TTTTO',
    'TXP',
    'XPPPP',
    'LLLB',
    'LLLTP',
    'OOHR',
    'LLLHH',
    'LQQTT',
    'QQQOX',
    'PPH',
    'TT',
    'LLOOP',
    'PPP',
    'LLQTO',
    'LTOO',
    'QQTT',
    'LQOOH',
    'QQQPH',
    'LLLP',
    'QQOOH',
    'QQHR',
    'LLQO',
    'LOHR',
    'LQPR',
    'LQHH',
    'QQQBB',
    'TOH']

import os

i=0
while True:
    sc=SnailCharacter()
    if sc.get_form() in already_exist_forms: #or os.path.isfile("./data/"+sc.get_form()+".png"):
        continue
    already_exist_forms.append(sc.get_form())
    i+=1
    #print(i,sc.get_form())
    sc.save_image(path='./data/',random_index=False)