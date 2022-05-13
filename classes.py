
class Player:
    def __init__(self, name, role, alignment, note):
        self.name = name
        self.startingrole = role
        self.rolenote = note
        self.currentrole = role
        self.startingalignment = alignment
        self.currentalignment = alignment
        self.alive = True
        self.deadvoteused = False
        self.abilityused = False

    def getplayerstate(self):
        return self.__dict__

class Game:
    def __init__(self,date,session,game,script,result,players):
        self.playerobjs = {}
        self.date = date
        self.session = session
        self.game = game
        self.script = script
        self.result = result
        self.players = players
        self.demonbluffs = []
        self.storytellers = []

    def getid(self):
        return f"{self.session}-{self.game}"

    def addplayer(self, name, role, alignment, note):
        p = Player(name, role, alignment,note)
        self.playerobjs[p.name] = p

    def getgamestate(self):
        d = self.__dict__
        d['playerdata'] = {x:d['playerobjs'][x].getplayerstate() for x in d['playerobjs']}
        del d['playerobjs']
        return d
