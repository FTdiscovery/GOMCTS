import numpy as np

class GoEnvironment:

    def __init__(self):
        self.board = np.zeros((9,9,2))
        self.plies_before_board = np.zeros((3,9,9,2))
        self.turns = 0
        self.alphabet = 'ABCDEFGHJ'
        self.wStones = []
        self.wSurStones = []
        self.bStones = []
        self.bSurStones = []
        self.wChains = []
        self.wSurChains = []
        self.bChains = []
        self.bSurChains = []
        self.illegalKo = 999
        self.turnOfIllegalKo = 999

        self.gamelog = ';FF[4]\nGM[1]\nDT[2018-01-10]\nPB[EKALGO]\nPW[EKALGO]\nBR[30k]\nWR[30k]\nRE[]\nSZ[9]\nKM[7.5]\nRU[chinese]'

    def addToGameLog(self, i, j, black):
        alphabet = "abcdefghi"
        if black:
            self.gameLog += '\n;B[' + alphabet.split("")[i] + alphabet.split("")[j] + ']'
        else:
            self.gameLog+='\n;W['+alphabet.split("")[i]+alphabet.split("")[j]+']'

    def output(self, a):
        if a[0] == 1:
            return '●'
        elif a[1] == 1:
            return 'O'
        return '+'

    def flipAction180(self, move):
        directory = self.alphabet.index(move[:1])
        return self.alphabet.split("")[8-directory]+(10-int(move[1:]))

    def flipAction90CC(self, move):
        column = self.alphabet.index(move[:1])-5
        row = int(move[1:])-5
        newCol = -row+5
        newRow = column+5
        return self.alphabet.split("")[newCol-1]+(newRow+1)

    def flipAction90C(self,move):
        column = self.alphabet.index(move[:1]) - 5
        row = int(move[1:]) - 5
        newCol = row + 5
        newRow = -column + 5
        return self.alphabet.split("")[newCol - 1] + (newRow - 1)

    def mirrorY(self, move):
        directory = self.alphabet.index(move[:1])
        return self.alphabet.split("")[8-directory]+move[1:]

    def mirrorX(self, move):
        directory = self.alphabet.index(move[:1])
        return self.alphabet.split("")[directory] + (20 - int(move[1:]))

    def printBoard(self):
        print('CURRENT STATE:\n\n   A  B  C  D  E  F  G  H  J')
        for i in range(9):
            if i>5:
                print(9-i, ' ', end='')
            else:
                print(9-i, ' ', end='')
            for j in range(9):
                print(self.output(self.board[i][j]),' ', end='')
            print('\n')


    def customMove(self, move, colour):
        directory = np.zeros(2)
        directory[0] = int(self.alphabet.index(move[:1]))
        directory[1] = 9-int(move[1:])
        if colour == 'B':
            turn = 0
        elif colour == 'W':
            turn = 1
        self.board[int(directory[1])][int(directory[0])][turn] = 1

    def BoardToState(self):
        for i in range(len(self.plies_before_board)):
            state = np.concatenate(self.board.flatten(), self.plies_before_board[i].flatten())

        return state

    def updateBoard(self):
        self.turnOfIllegalKo = 999
        self.illegalKo = 999
        self.wStones.clear()
        self.wSurStones.clear()
        self.bStones.clear()
        self.bSurStones.clear()
        self.locateChains()
        if self.turns%2==0:
            self.captureDeadStonesB()
        else:
            self.captureDeadStonesW()

    def surroundReq(self,i,j): #return liberties of each stone
        ba = []
        if i!=0:
            ba.append(((i-1)*9+j))
        if j!=0:
            ba.append((i)*9+j-1)
        if j!=8:
            ba.append((i)*9+j+1)
        if i!=8:
            ba.append((i+1)*9+j)

        return ba

    def searchSurroundings(self, i, j, k):
        required = 4
        stoneSurround = 0
        i=int(i)
        j=int(j)
        k=int(k)
        if i==0:
            required-=1
        elif self.board[i-1][j][k]==1 and self.board[i-1][j][k-1]==0:
            stoneSurround+=1
        if j==0:
            required-=1
        elif self.board[i][j-1][k]==1 and self.board[i][j-1][1-k]==0:
            stoneSurround+=1
        if i==8:
            required-=1
        elif self.board[i+1][j][k]==1 and self.board[i+1][j][1-k]==0:
            stoneSurround+=1
        if j==8:
            required-=1
        elif self.board[i][j+1][k]==1 and self.board[i][j+1][1-k]==0:
            stoneSurround+=1
        if stoneSurround == required:
            self.illegalKo = (i*9)+j
            self.turnOfIllegalKo = self.turns
            self.board[i][j][1 - k] = 0
            self.board[i][j][k] = 0
            print('Captured stone ' , ((i * 9) + j))

    def locateChains(self):
        for i in range(9):
            for j in range(9):
                array = np.ones(9*i+j)
                if self.board[i][j][1]==1:
                    self.wStones.append(array)
                    self.wSurStones.append(self.surroundReq(i,j))
                if self.board[i][j][0]==1:
                    self.bStones.append(array)
                    self.bSurStones.append(self.surroundReq(i,j))

        white_stone_map = np.ones((9,9))
        black_stone_map = np.ones((9,9))
        for i in range(9):
            for j in range(9):
                white_stone_map[i][j] = int(self.board[i][j][1])
                black_stone_map[i][j] = int(self.board[i][j][0])

        self.wChains = self.findChains(white_stone_map)
        self.bChains = self.findChains(black_stone_map)
        self.wSurChains = self.surArray(self.wChains)
        self.bSurChains = self.surArray(self.bChains)


    def followChain(self, board, i, j, c=[]):
        chain = list(c)  # This just forces it to pass by value. ignore when porting to javab
        if i >= len(board) or i < 0 or j >= len(board[0]) or j < 0:
            return chain
        if board[i][j] == 0 or i * 9 + j in chain:
            return chain
        chain.append(i * 9 + j)
        chain1 = self.followChain(board, i + 1, j, chain)
        chain2 = self.followChain(board, i, j + 1, chain1)
        chain3 = self.followChain(board, i - 1, j, chain2)
        chain4 = self.followChain(board, i, j - 1, chain3)
        return chain4

    def findChains(self, board):
        chains = []
        for i in range(9):
            for j in range(9):
                elem = board[i][j]
                if elem == 1:
                    if (j != 0 and board[i][j - 1] == 1) or (i != 0 and board[i - 1][j] == 1):
                        continue
                    chain = self.followChain(board, i, j)
                    if len(chain) > 1:
                        chains.append(chain)
        return chains

    def surArray(self, chains):
        output = []
        for i in range(len(chains)):
            output.append(self.surroundings(chains[i]))
        return output


    def surroundings(self, chain):
        wrongsurroundings = []
        print('chain',chain)
        for i in range(len(chain)):
            wrongsurroundings.append((self.surroundReq(int(int(chain[i]/9)),int(int(chain[i]%9)))))

        print('wrongsurroundings',wrongsurroundings)
        flat_sur = []

        for x in wrongsurroundings:
            for y in x:
                flat_sur.append(int(y))

        unique_list = []

        for i in flat_sur:
            if i not in unique_list:
                unique_list.append(i)


        sur = []

        for i in range(len(unique_list)):
            print(np.in1d([unique_list[i]],chain))
            if np.in1d([unique_list[i]],chain) == False:
                sur.append(unique_list[i])


        return sur

    def ifSurroundedByW(self, require):
        covered = 0
        for i in range(len(require)):
            if self.board[int(require[i]/9)][int(require[i]%9)][1]==1:
                covered+=1
        return covered == len(require)

    def ifSurroundedByB(self, require):
        covered = 0
        print('require', require)
        print('ifsurroundedbyb',require)
        for i in range(len(require)):
            if self.board[int(require[i]/9)][int(require[i]%9)][0]==1:
                covered+=1
        print('covered',covered)
        return covered == len(require)

    def removeStones(self, stones):
        print('hi',stones)
        for i in range(len(stones)):
            self.board[int(stones[i] / 9)][int(stones[i] % 9)][0] = 0;
            self.board[int(stones[i] / 9)][int(stones[i] % 9)][1] = 0;

    def captureDeadStonesW(self):
        print('wchain', self.wChains)
        print('wchain length', len(self.wChains))
        print('wsurchain',self.wSurChains)
        for i in range(len(self.wChains)):
            if self.ifSurroundedByB(self.wSurChains[i]):
                self.removeStones(self.wChains[i])
                print('Captured chain ' , self.wChains[i])

        for i in range(len(self.wStones)):
            self.searchSurroundings(self.wStones[i][0]/9,self.wStones[i][0]%9, 0)

    def captureDeadStonesB(self):
        print('bchain',self.bChains)
        for i in range(len(self.bChains)):
            if self.ifSurroundedByW(self.bSurChains[i]):
                self.removeStones(self.bChains[i])
                print('Captured chain ' , self.bChains[i])

        for i in range(len(self.bStones)):
            self.searchSurroundings(self.bStones[i][0]/9,self.bStones[i][0]%9, 1)

    def inaccStones(self, stones, wrongSurround):
        ky = []
        for i in range(len(wrongSurround)):
            if np.in1d(stones, wrongSurround[i]) == False:
                ky.append(wrongSurround[i])
        return ky

    def printAllChains(self):
        print('\n----\nFOR BLACK:\n---- ')
        for i in range(len(self.bChains)):
            print(self.bChains[i])
            print('Surrounding Stones: ' , self.bSurChains[i])
        print('\n-----\nFOR WHITE:\n---- ')
        for i in range(len(self.wChains)):
            print(self.wChains[i])
            print('Surrounding Stones: ' , self.wSurChains[i])


go = GoEnvironment()
go.customMove('A3','B')
go.customMove('B3','B')
go.customMove('C3','B')
go.customMove('D3','W')
go.customMove('A4','W')
go.customMove('A2','W')
go.customMove('B4','W')
go.customMove('B2','W')
go.customMove('C4','W')
go.customMove('C2','W')

go.printBoard()
go.locateChains()
print(go.wChains)
print(go.bChains)
print(go.wSurChains)
print(go.bSurChains)

go.updateBoard()
go.printBoard()

