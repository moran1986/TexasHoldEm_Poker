from random import randint

class Card:
    NumToRanking = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,
                    '10':10,'J':11,'Q':12,'K':13,'A':14,}
    SuitToRanking = {'DIAMONDS':1, 'CLUBS':2, 'HEARTS':3, 'SPADES':4}

    def __init__(self, number, suit):
        self._number = number.upper()
        self._ranking = Card.NumToRanking[self._number]
        self._suit = suit.upper()
        self._suitRanking = Card.SuitToRanking[self._suit]
    def getNumber(self):
        return self._number
    def getSuit(self):
        return self._suit
    def getRanking(self):
        return self._ranking
    def __repr__(self):
        icon = ""
        if self._suit == "DIAMONDS":
            icon = "of DIAMONDS"
        elif self._suit == "CLUBS":
            icon = "of CLUBS"
        elif self._suit == "HEARTS":
            icon = "of HEARTS"
        elif self._suit == "SPADES":
            icon = "of SPADES"
        else:
            pass #RAISE EXCEPTION HERE
        return (self._number + " " + icon)
    def __lt__(self, other):
        if self._number != other._number:
            return self._ranking < other._ranking
        else:
            return self._suitRanking < other._suitRanking
    def __gt__(self, other):
        if self._number != other._number:
            return self._ranking > other._ranking
        else:
            return self._suitRanking > other._suitRanking
    def __eq__(self, other):
        return  (self._number == other._number and self._suit == other._suit)
    def __hash__(self):
        return hash((self._number, self._ranking, self._suit, self._suitRanking))

class Deck:
    numberRange = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    suitRange = ['DIAMONDS', 'CLUBS', 'HEARTS', 'SPADES']
    def __init__(self):
        self._deck = []
        for numberIndex in range(len(Deck.numberRange)):
            for suitIndex in range(len(Deck.suitRange)):
                self._deck.append(Card(Deck.numberRange[numberIndex],Deck.suitRange[suitIndex]))
        self._count = 0

    def shuffle(self): # Implementation of the inside-out version of the Fisher-Yates algorithm
        temp = self._deck[:]
        for cardIndex in range(len(self._deck)):
            random = randint(0,cardIndex)
            if random != cardIndex:
                temp[cardIndex] = temp[random]
            temp[random] = self._deck[cardIndex]
        self._deck = temp[:]

    def draw(self): # Draws a card from the deck and returns it
        cardDrawn = self._deck[self._count]
        self._count +=1
        return cardDrawn
    def discard(self): # Skips over a card in the deck as if it was discarded
        self._count+=1
    def reset(self): # Shuffles the deck again and resets the count
        Deck.shuffle(self)
        self._count=0
    def __repr__(self): # Prints the deck but should not be implemented by the user in order to abide to poker rules
        raise NotImplementedError
        #Comment above and uncomment below for testing purposes
        #print (self._deck)
        #return (str(len(self._deck)))

class River:
    def __init__(self):
        self._river = []
    def step(self, stepNum, Deck): # depending on the step of the river, draws n cards to the river
        if stepNum == 1:
            for i in range(3):
                self._river.append(Deck.draw())
        elif stepNum == 2 or stepNum == 3:
            Deck.discard()
            self._river.append(Deck.draw())
        else:
            pass # Raise stepNum Exception
    def showRiver(self): # displays the river
        print("RIVER")
        for i in range(len(self._river)):
            print (str(i+1) + ". "),
            print self._river[i]
    def getRiver(self): # returns the river
        return self._river

class Hand:
    Rankings = {"SINGLE":0, "PAIR":1, "TWOPAIR":2, "THREE":3, "STRAIGHT":4, "FLUSH":5,
                    "FULLHOUSE":6, "FOUR":7, "STRAIGHTFLUSH":8, "ROYALFLUSH":9}
    def __init__(self):
        self._hand = []
        self._High = []
    def dealtHand(self, nCards, Deck): # Deals ncards from Deck to the hand
        for i in range(nCards):
            self._hand.append(Deck.draw())
    def showHand(self): # displays the hand
        print ("Have your opponent face away from the screen and press enter when ready to see your hand.")
        if raw_input() == "":
            for i in range(len(self._hand)):
                print(self._hand[i])
    def getHand(self): # returns the hand
        return self._hand
    def getHigh(self): # returns the highest card in the player's hand
        return self._High
    def evaluate(self, riverCards): # evaluates what combinations the player has achieved with his hand and the river
        fullHand = self._hand + riverCards
        fullHand.sort(reverse=True)
        self._High.append(fullHand[0])
        StraightCombo = Hand.checkStraight(self,fullHand)
        FlushCombo = Hand.checkFlush(self,fullHand)
        if StraightCombo is not None and FlushCombo is not None:
            if Hand.checkRoyal(self,StraightCombo, FlushCombo):
                return (StraightCombo, Hand.Rankings["ROYALFLUSH"])
            elif StraightCombo == FlushCombo:
                return (StraightCombo, Hand.Rankings["STRAIGHTFLUSH"])
            else:
                return (FlushCombo,Hand.Rankings["FLUSH"])
        elif StraightCombo is not None and FlushCombo is None:
            return (StraightCombo, Hand.Rankings["STRAIGHT"])
        elif StraightCombo is None and FlushCombo is not None:
            return (FlushCombo,Hand.Rankings["FLUSH"])
        else:
            cards, freqList = Hand.checkFreq(self, fullHand)
            FourOfKind = Hand.checkFour(self, fullHand, cards, freqList)
            if FourOfKind is not None:
                return (FourOfKind,Hand.Rankings["FOUR"])
            ThreeOfKind = Hand.checkThree(self, fullHand, cards, freqList)
            Pair = Hand.checkPair(self, fullHand, cards, freqList)
            if ThreeOfKind is not None and Pair is not None:
                FullHouse = ThreeOfKind + Pair
                return (FullHouse,Hand.Rankings["FULLHOUSE"])
            elif ThreeOfKind is not None and Pair is None:
                return (ThreeOfKind,Hand.Rankings["THREE"])
            elif ThreeOfKind is None and Pair is not None:
                Pairs = Hand.getAllPairs(self, fullHand, cards, freqList)
                if len(Pairs) > 2:
                    return (Pairs, Hand.Rankings["TWOPAIR"])
                else:
                    return (Pairs, Hand.Rankings["PAIR"])
            else:
                return (self._High, Hand.Rankings["SINGLE"])

    def checkStraight(self,CardList): # checks if hand has a straight in it
        start, end = 0,5
        while end <= len(CardList):
            fail = False
            temp = CardList[start:end]
            high = temp[start].getRanking()
            for i in range(1, 5):
                if high-1 != temp[i].getRanking():
                    fail = True
                    break
                else:
                    high = temp[i].getRanking()
            if fail:
                start+=1
                end+=1
                temp=[]
            else:
                return(temp)

    def checkFlush(self,CardList): # checks if hand has a flush in it
        nSuit = {"DIAMONDS":0, "CLUBS":0, "HEARTS":0, "SPADES":0}
        for i in range(len(CardList)):
            suit = CardList[i].getSuit()
            nSuit[suit] += 1
        for tup in nSuit.items():
            if tup[1] >= 5:
                flushSuit = tup[0]
                flushHand = []
                count = 0
                while len(flushHand) < 5:
                    if CardList[count].getSuit() == flushSuit:
                        flushHand.append(CardList[count])
                    count+=1
                return flushHand

    def checkRoyal(self,StraightCombo, FlushCombo):  # checks if hand has a royal in it
        if StraightCombo != FlushCombo or StraightCombo[0].getRanking() != 14:
            return False
        return True

    def checkFreq(self, CardList):  # checks if frequency of card number in player's hand
        cards, freq = [],[]
        for i in range(len(CardList)):
            if CardList[i].getNumber() not in cards:
                cards.append(CardList[i].getNumber())
                freq.append(1)
            else:
                freq[len(freq)-1]+=1
        return cards, freq

    def checkFour(self, CardList, cards, freq): # checks if hand has a four of a kind
        if 4 in freq:
            combo = []
            wantedCardNumber = cards[freq.index(4)]
            for c in CardList:
                if c.getNumber() == wantedCardNumber:
                    combo.append(c)
            return combo
    def checkThree(self, CardList, cards, freq): # checks if hand has a three of a kind
        if 3 in freq:
            combo = []
            wantedCardNumber = cards[freq.index(3)]
            for c in CardList:
                if c.getNumber() == wantedCardNumber:
                    combo.append(c)
            return combo
    def checkPair(self, CardList, cards, freq): # checks if hand has a pair
        if 2 in freq:
            combo = []
            wantedCardNumber = cards[freq.index(2)]
            for c in CardList:
                if c.getNumber() == wantedCardNumber:
                    combo.append(c)
            return combo

    def getAllPairs(self, CardList, cards, freq): # checks for at most 2 pairs in hand
        pairs = []
        for i in range(len(freq)):
            if freq[i] == 2:
                wantedCardNumber = cards[i]
                for j in range(len(CardList)):
                    if CardList[j].getNumber() == wantedCardNumber:
                        pairs.append(CardList[j])
                if len(pairs) == 4:
                    break
        return pairs

    def assignHand(self,CardList): # assigns cards to hand. Exclusively for testing purposes
        raise NotImplementedError
        #Uncomment below and comment above for testing purposes
        #self._hand = CardList

class ChipPile():
    BIG_BLIND = 40
    SMALL_BLIND = 20
    STARTING = 2000
    def __init__(self):
        self._chipPile = ChipPile.STARTING
        self._BigBlind = False
    def getChipPile(self): # returns the player's chip pile
        return (self._chipPile)
    def addToChipPile(self, nChips): # adds nChips to to player's chip pile
        self._chipPile += nChips
    def setBlinds(self, alternate): # setBlinds depending on alternate boolean True/False for 2 players
        if alternate:
            self._BigBlind = True
    def betBlinds(self, Pot): # bet blinds to the pot
        if self._BigBlind:
            Pot.addToPot(PokerPlayer.BIG_BLIND)
            self._chipPile -= PokerPlayer.BIG_BLIND
        else:
            Pot.addToPot(PokerPlayer.SMALL_BLIND)
            self._chipPile -= PokerPlayer.SMALL_BLIND
        if self._chipPile < 0:
            self._chipPile = 0
    def getBigBlind(self): # returns big blind status
        return self._BigBlind

class PokerPlayer(Hand, ChipPile):
    def __init__(self, name=""):
        Hand.__init__(self)
        ChipPile.__init__(self)
        self._name = name
        self._AllIn = False
        self._isWinner = False
    def __repr__(self):
        prompt = self._name + ", " + str(self._chipPile) + " chips"
        return prompt
    def getName(self): # gets name of poker player
        return self._name
    def getWinStatus(self): # returns win status of poker player
        return self._isWinner
    def isAllIn(self): # returns all in status of poker player
        return self._AllIn
    def setAsWinner(self): # sets poker player as winner of pot
        self._isWinner = True
    def resetAll(self): # resets attributes for the next round
        self._AllIn = False
        self._BigBlind = False
        self._hand = []
        self._High = []
        self._isWinner = False
    def bet(self,multiplyPotBy,pokerPot): # handles player's option for betting
        oldPot = pokerPot.getPot()
        newPot = oldPot + oldPot * multiplyPotBy
        self._chipPile -= (newPot - oldPot)
        if self._chipPile <= 0:
            self._chipPile += (newPot - oldPot)
            PokerPlayer.allIn(self,pokerPot)
        else:
            pokerPot.setCallBet(newPot - oldPot)
            pokerPot.setPot(newPot)
            print self.getName() + " bets " + str(newPot - oldPot) + "!"
    def call(self, pokerPot): # handles player's option for calling
        oldPot = pokerPot.getPot()
        callBet = pokerPot.getCallBet()
        self._chipPile -= callBet
        if self._chipPile > 0:
            newPot = oldPot + callBet
            pokerPot.setPot(newPot)
            print self.getName() + " calls " + str(callBet) + "!"
        else:
            self._chipPile += callBet
            PokerPlayer.allIn(self,pokerPot)
    def check(self, pokerPot): # handles player's option for calling a call or checking
        pokerPot.resetCallBet()
        print self.getName() + " checks!"
    def allIn(self,pokerPot, other=None): # handles player's option for going all in
        self._AllIn = True
        if other==None or self._chipPile < other.getChipPile() :
            oldPot = pokerPot.getPot()
            newPot = oldPot + self._chipPile
            pokerPot.setCallBet(self._chipPile)
            self._chipPile = 0
            pokerPot.setPot(newPot)
            print self.getName() + " is all in! Bets " + str(newPot - oldPot) + "! "
        else:
            oldPot = pokerPot.getPot()
            newPot = oldPot + other.getChipPile()
            pokerPot.setCallBet(other.getChipPile())
            self._chipPile -= other.getChipPile()
            pokerPot.setPot(newPot)
            print self.getName() + " is all in! Bets " + str(newPot - oldPot) + "! "

class Pot:
    def __init__(self):
        self._pot = 0
        self._callBet = 0
    def __repr__(self):
        prompt = "Pot at " + str(self._pot)
        return prompt
    def getPot(self): # returns the pot
        return self._pot
    def getCallBet(self): # returns amount needed to call a bet
        return self._callBet
    def setCallBet(self, nChips): # sets amount needed to call a bet
        self._callBet = nChips
    def resetCallBet(self): # resets amount needed to call a bet
        self._callBet = 0
    def setPot(self, new): # sets the Pot to a new amount
        self._pot = new
    def addToPot(self, nChips): # adds nchips to pot
        self._pot += nChips
    def awardPot(self, whoWon): # awards pot to whoWon
        whoWon.addToChipPile(self._pot)
        self._pot = 0
        self._callBet = 0
    def splitPot(self, p1, p2): # splits pot between player1 and player2
        p1.addToChipPile(self._pot//2)
        p2.addToChipPile(self._pot//2)
        self._pot = 0
        self._callBet = 0
    def whoIsBigBlind(self,p1,p2): # returns player who is the big blind
        if p1.getBigBlind():
            return p1
        else:
            return p2