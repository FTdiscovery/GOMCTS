import numpy as np
from TTTEnvironment import TTTEnvironment


# w stands for # of wins, n stands for number of times node has been visited.
# N stands for number of times parent node is visited, and c is just an exploration constant that can be tuned.
# Q is the evaluation from 0 to 1 of the neural network
# L is a number of value 0 or 1. If the move is legal, then this value is 1. If the move is not, then this value is 0.
def UCT_Algorithm(w, n, c, N, q, L):
    # Provides a win rate score from 0 to 1
    selfPlayEvaluation = 0.5
    selfPlayEvaluation = np.divide(w, n, out=np.zeros_like(w), where=n!=0)
    nnEvaluation = q
    winRate = (nnEvaluation + selfPlayEvaluation) / 2

    # Exploration
    exploration = c * np.sqrt(np.log(N) / n)

    UCT = winRate + exploration
    return UCT * L


#UCT Algorithm used by Alpha Zero. Use this for now!!
def PUCT_Algorithm(w, n, c, N, q, L):
    # Provides a win rate score from 0 to 1
    selfPlayEvaluation = 0.5
    selfPlayEvaluation = np.divide(w, n, out=np.zeros_like(w), where=n != 0)
    nnEvaluation = q
    winRate = (nnEvaluation + selfPlayEvaluation) / 2

    # Exploration
    exploration = c * np.sqrt(N)/(1+n)

    UCT = winRate + exploration
    return UCT * L



class MonteCarlo():

    # We will use three lists:
    # seenStates stores the gameStates that have been seen. This is a library.
    # parentSeen stores the times that the current gameState has been seen
    # Each game state corresponds to arrays of the possible moves (<=9)
    # There are 3 points information stored for each of the children
    # - win count, number of times visited, and neural network evaluation
    # This is helpful because we get to use numpy stuffs.

    def __init__(self):
        # This is a dictionary. Information will be updated as playouts start. ['stateToString': 0]
        # 0 corresponds to position 0 on all the other arrays, 1 corresponds to position 1...hmmm.
        self.dictionary = {
            '0000000000000000000': 0  # empty board corresponds to position 0 on numpy arrays
        }
        #self.gameStateSeen = np.zeros(9) Commented because it seems obsolete

        self.childrenStateSeen = np.zeros((1, 9))  # This is a 2D array
        self.childrenStateWin = np.zeros((1, 9))  # This is a 2D array
        self.childrenNNEvaluation = np.random.rand(1, 9)  # This is a 2D array

    def addToDictionary(self, position):
        self.dictionary[position]=len(self.dictionary)

    def simulation(self, originalPosition):
        # We store the information in the simulation in a temporary array, before adding everything to the database.
        turns = 0

        OstatesExplored = np.array([['0000000000000000000']])  # Store it as an array of directories for the seen stuff
        OactionsDone = np.zeros((1,9))
        XstatesExplored = np.array([['0000000000000000000']])  # Store it as an array of directories for the seen stuff
        XactionsDone = np.zeros((1,9))

        position = originalPosition

        #if game state is seen before,

        end=2 #0 if draw, 1 if X won, -1 if O won, 2 if keep going

        while(end==2):

            board = TTTEnvironment()
            board.state = TTTEnvironment.stringToState(board, position)
            TTTEnvironment.setValues(board)

            if position not in self.dictionary:
                self.initializePosition(position)

            nextPosition = list(position)

            """
            print("STATE: " + position)
            print(board.Xstate)
            print(board.Ostate)
            """

            #move = self.debugChooseMove(turns)
            move = self.chooseMove(position, board.legalMove())

            if ((int(board.turn)) % 2) == 0:  # If it's X to move
                nextPosition[move] = '1'
            if ((int(board.turn)) % 2) == 1:  # If it's O to move
                nextPosition[move + 9] = '1'
            nextPosition[-1] = str(1-int(nextPosition[-1]))

            nextPosition = ''.join(nextPosition)


            if ((int(board.turn)) % 2) == 0: # If it's X to move
                if turns != 0:
                    currentPosArray = np.array([[(position)]])
                    newAction=np.zeros((1,9))
                    newAction[0, move]=1
                    XstatesExplored=np.concatenate((XstatesExplored, currentPosArray), axis=0)
                    XactionsDone=np.concatenate((XactionsDone,newAction),axis=0)
                else:
                    XstatesExplored[0,0] = position
                    XactionsDone[0,move]=1
                #change tic tac toe board

            if ((int(board.turn)) % 2) == 1: # If it's O to move
                if turns != 0:
                    currentPosArray = np.array([[(position)]])
                    newAction = np.zeros((1, 9))
                    newAction[0, move] = 1
                    OstatesExplored = np.concatenate((OstatesExplored, currentPosArray), axis=0)
                    OactionsDone = np.concatenate((OactionsDone, newAction), axis=0)
                else:
                    OstatesExplored[0,0] = position
                    OactionsDone[0,move] = 1
                # change tic tac toe board
            turns += 1
            position = nextPosition

            board.state = TTTEnvironment.stringToState(board, position)
            TTTEnvironment.setValues(board)
            end=TTTEnvironment.check_Win(board)

        if end==1:
            for x in range(len(XstatesExplored)):
                dictionaryValue=self.dictionary[XstatesExplored[x,0]]
                self.childrenStateSeen[dictionaryValue]+=XactionsDone[x]
                self.childrenStateWin[dictionaryValue]+=XactionsDone[x]

            for x in range(len(OstatesExplored)):
                dictionaryValue=self.dictionary[OstatesExplored[x,0]]
                self.childrenStateSeen[dictionaryValue]+=OactionsDone[x]
                #no childrenStateWin because you lost

            #print('X wins')

        if end==-1:
            for x in range(len(XstatesExplored)):
                dictionaryValue=self.dictionary[XstatesExplored[x,0]]
                self.childrenStateSeen[dictionaryValue] += XactionsDone[x]
                # no childrenStateWin because you lost

            #print('O wins')

            for x in range(len(OstatesExplored)):
                dictionaryValue=self.dictionary[OstatesExplored[x,0]]
                self.childrenStateSeen[dictionaryValue] += OactionsDone[x]
                self.childrenStateWin[dictionaryValue] += OactionsDone[x]

        if end==0:
            for x in range(len(XstatesExplored)):
                dictionaryValue=self.dictionary[XstatesExplored[x,0]]
                self.childrenStateSeen[dictionaryValue]+=XactionsDone[x]
                self.childrenStateWin[dictionaryValue] += 0.5*XactionsDone[x]

            for x in range(len(OstatesExplored)):
                dictionaryValue=self.dictionary[OstatesExplored[x,0]]
                self.childrenStateSeen[dictionaryValue]+=OactionsDone[x]
                self.childrenStateWin[dictionaryValue] += 0.5*OactionsDone[x]

            #print('Draw')

        # just debugging
        #print('ends at', nextPosition)
        #print("X:")
        #print(board.Xstate)
        #print("O:")
        #print(board.Ostate)
        #if end==0:
            #print("TOTAL = ")
            #print(np.sum((board.Xstate, board.Ostate), axis=0))

    def runSimulations(self, sims, position):
        for i in range(sims):
            self.simulation(position)
        return self.dictionary

    #choose argmax per (P)UCT Algorithm
    def chooseMove(self, position, legalMoves):
        index = self.dictionary[position]  # This returns a number based on the library

        # here we will assume that there is a legalMove function that works as followed:
        # If the first row of a tic tac toe row is all taken, then it returns [0,0,0,1,1,1,1,1,1]

        moveChoice = PUCT_Algorithm(self.childrenStateWin[index], self.childrenStateSeen[index], 2**0.5*np.ones((1,9)), np.sum(self.childrenStateSeen[index]), self.childrenNNEvaluation[index], legalMoves)
        return np.argmax(moveChoice)

    def initializePosition(self, pos): #adds pos to dictionary and concatenates new layers to MCTS arrays
        self.addToDictionary(pos)
        self.childrenStateSeen = np.concatenate((self.childrenStateSeen,np.zeros((1, 9))), axis=0)
        self.childrenStateWin = np.concatenate((self.childrenStateWin, np.zeros((1, 9))), axis=0)
        self.childrenNNEvaluation = np.concatenate((self.childrenNNEvaluation, np.random.rand(1, 9)), axis=0)

    def intToPos(self, integ):
        number = int(integ)
        number = str(number)
        length=len(number)
        for x in range(19 - length):
            number = '0' + number
        return number

    #returns the index of a move for competitive play
    def competitiveMove(self, position):

        board = TTTEnvironment()
        board.state = TTTEnvironment.stringToState(board, position)
        TTTEnvironment.setValues(board)

        self.runSimulations(3200, position)
        index = self.chooseMove(position, board.legalMove())
        return int(index)

    #returns the index of a move for training
    def trainingMove(self, position):

        board = TTTEnvironment()
        board.state = TTTEnvironment.stringToState(board, position)
        TTTEnvironment.setValues(board)

        self.runSimulations(3200, position)
        index = np.argmax(self.childrenStateSeen[self.dictionary[position]])
        return int(index)


x = MonteCarlo()

#INITIALIZE BOARD
seriousGame = TTTEnvironment()
while seriousGame.check_Win() == 2:
    #MAKES MOVE
    seriousGame.makeMove(x.competitiveMove(seriousGame.stateToString()))
    seriousGame.turn = str((int(seriousGame.turn) + 1) % 2)
    seriousGame.updateState()
    print(seriousGame.Xstate)
    print(seriousGame.Ostate)
    print("-------")

print(seriousGame.check_Win())
print(seriousGame.Xstate)
print(seriousGame.Ostate)


print("\n\n---training data---")
print(x.dictionary)
print(x.childrenStateSeen)
print(x.childrenStateWin)

#print(x.childrenNNEvaluation)
