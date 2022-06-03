import copy

import pandas as pd



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
        self.hasability = False
        self.abilityused = False
        self.poisoned = False
        self.roleimg = self.getroleimg()

    def getplayerstate(self):
        return self.__dict__

    def getroleimg(self):
        if self.currentrole == "ST":
            return "https://raw.githubusercontent.com/bra1n/townsquare/develop/src/assets/demon-head.png"
        roleconverted = self.currentrole.replace("'", '').replace(' ', '').replace('-', '').lower()
        alignment = self.currentalignment.lower()
        health = "ill" if self.poisoned else "healthy"
        if not self.hasability:
            ability = "noability"
        elif self.abilityused:
            ability = "used"
        else:
            ability = "unused"
        alive = "alive" if self.alive else "dead"
        return f"{roleconverted}-{alignment}-{health}-{ability}-{alive}.png"

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
        self.eventdf = None
        self.votedf = None
        self.playervotedf = None
        self.events = None

    def getid(self):
        return f"{self.session}-{self.game}"

    def addplayer(self, name, role, alignment, note):
        p = Player(name, role, alignment,note)
        self.playerobjs[p.name] = p

    def getgamestate(self):
        d = self.__dict__
        d['playerdata'] = {x:d['playerobjs'][x].getplayerstate() for x in d['playerobjs']}
        d = copy.deepcopy(d)
        del d['playerobjs']
        return d

    def processgame(self):
        self.votedf["voteid"] = self.votedf['gameid'].astype(str)+"-"+self.votedf['Vote Number'].astype(str)
        self.playervotedf["voteid"] = self.playervotedf['gameid'].astype(str)+"-"+self.playervotedf['Vote Number'].astype(str)

        v = self.votedf.copy(deep=True)
        pv = self.playervotedf.copy(deep=True)

        t = self.eventdf.copy(deep=True)
        t = t.reset_index()
        self.events = []
        for ind, r in t.iterrows():
            self.events.append(self.processevent(r, v, pv))

    def processevent(self, row, votes, playervotes):
        #print(row)
        actiontaker = None if pd.isnull(row["Player"]) else row["Player"]
        if actiontaker == "Legion":
            actiontakerstate = "Legion"
        elif actiontaker is not None:
            actiontakerstate = self.playerobjs[actiontaker].getplayerstate()
        else:
            actiontakerstate = None

        targetlist = [x for x in row["Target"].split("|")]
        targetstatedict = {x:self.playerobjs[x].getplayerstate() for x in targetlist if x in self.playerobjs}

        e = Event(row["Game Number"], row["Session"], row["index"], row["Phase"], row["Action"],
                  actiontaker, actiontakerstate, targetlist, targetstatedict, row["Note"])
        e.processevent(self.getgamestate(), votes, playervotes)

        #print(getattr(e,'avsavs',None))
        #print(setattr(e,'session',99))
        return copy.deepcopy(e)

class Event:
    def __init__(self, session, game, eventnumber, phase, eventname, player, playerstate, targetlist, targetstatedict,note):
        self.session = session
        self.game = game
        self.eventnumber = eventnumber
        self.eventname = eventname
        self.note = note
        self.phase = phase
        self.player = player
        self.playerstate = playerstate
        self.targetlist = targetlist
        self.targetstatedict = targetstatedict
        self.delta = []
        self.HTML = f"UNPROCESSED - {session}-{game}-{eventnumber} {phase} {player} {eventname} {'|'.join(targetlist)} {note}"

        self.death = False
        self.killer = None
        self.killed = []
        self.methodofdeath = None

        self.vote = False
        self.voteHTML = ""

    def playerimagehtml(self,playerstate,size=50):
        roleimg = playerstate['roleimg']
        name = playerstate['name']
        role = playerstate['currentrole']
        return f'<img src = "{roleimg}" height = "{size}" data-bs-toggle="tooltip" data-bs-placement="bottom" title="" data-bs-original-title="{name}-{role}">'

    def getroleimg(self,role,size=50):
        if role == "ST":
            address = "https://raw.githubusercontent.com/bra1n/townsquare/develop/src/assets/demon-head.png"
        else:
            roleconverted = role.replace("'", '').replace(' ', '').replace('-', '').lower()
            address = f"https://raw.githubusercontent.com/bra1n/townsquare/develop/src/assets/icons/{roleconverted}.png"

        return f'<img src = "{address}" height = "{size}" data-bs-toggle="tooltip" data-bs-placement="bottom" title="" data-bs-original-title="{role}">'

    def getplayerimg(self,size=50):
        return f"<strong>{self.player}</strong> {self.playerimagehtml(self.playerstate,size=size)}"

    def processdeath(self,killer,killed,method):
        for p in killed:
            self.delta.append([p,"alive", False])
            self.delta.append([p,"killed by", killer])
            self.delta.append([p,"killed method", method])
            self.delta.append([killer, "kills", p])
            self.killed.append(p)
        self.death = True
        self.killer = killer
        self.methodofdeath = method

    def processevent(self, gamestate, votes, playervotes):
        if self.eventname == 'Slayer Shot':
            slayershot = '/static/imgs/slayershot.webp'
            targetplayer = self.targetlist[0]
            targetplayerpack = f"{targetplayer}{self.playerimagehtml(self.targetstatedict[targetplayer], size=50)}"
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} <img src = '{slayershot}' height = '50'> {targetplayerpack}"
            else:
                self.HTML = f"{self.getplayerimg()} <img src = '{slayershot}' height = '50'> {targetplayerpack} ({self.note})"
            self.delta.append([self.player, "abilityused", True])

        elif self.eventname == 'Snitch Bluffs':
            if self.note == '':
                bluffs = " ".join([self.getroleimg(x, size=40) for x in self.targetlist])
                self.HTML = f"{self.getplayerimg()} receives bluffs.<br> {bluffs}"
                for x in self.targetlist:
                    self.delta.append(["additional bluff used", x])
            else:
                print(self.__dict__)

        elif self.eventname == 'Washerwoman Information':
            if self.note == '':
                pack = [self.targetstatedict[x] for x in self.targetlist[:2]]
                self.HTML = f"{self.getplayerimg()} learns {self.playerimagehtml(pack[0])} or {self.playerimagehtml(pack[1])} is {self.getroleimg(self.targetlist[2])}"
            else:
                print(self.__dict__)

        elif self.eventname in ['Oracle Number','Chef Number','Mathematician Number','Empath Number','Clockmaker Number']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} learns a {self.targetlist[0]}"
            else:
                print(self.__dict__)

        elif self.eventname == 'Killed':
            if self.note == 'Slayer Kill':
                self.HTML = f"{self.getplayerimg()} is killed by the Slayer"
                attacker = [x for x in gamestate['events'] if x.eventname == "Slayer Shot"][-1].player
                self.processdeath(attacker, [self.player], 'Slayer Kill')
            else:
                print(self.__dict__)

        elif self.eventname == 'Nomination':
            print("FINSIH THIS")
            print(print(self.__dict__))
            if self.note != 'No Vote':
                voteid = f"{self.session}-{self.game}-{str(self.note)[1:]}"
                print(voteid)
                print([x for x in votes.to_dict("records") if x['voteid'] == voteid][0])
                print({x['Player']:x['Voted'] for x in playervotes.to_dict("records") if x['voteid'] == voteid})
                #votes, playervotes
                exit()

                pack = [self.targetstatedict[x] for x in self.targetlist[:2]]
                self.HTML = f"{self.getplayerimg()} learns {self.playerimagehtml(pack[0])} or {self.playerimagehtml(pack[1])} is {self.getroleimg(self.targetlist[2])}"
            else:
                print(self.__dict__)
            exit()

        elif self.eventname == 'Executed':
            execute = '/static/imgs/execute.webp'
            executeblock = '/static/imgs/executeblock.webp'
            executejudge = '/static/imgs/executejudge.webp'
            if self.note == '':
                self.HTML = f"<img src = '{execute}' height = '60'> {self.getplayerimg()} was executed"
                self.processdeath(None, [self.player], 'Executed')
            elif self.note == "Protected":
                self.HTML = f"<img src = '{executeblock}' height = '60'> {self.getplayerimg()} dodged execution"
            elif self.note == "Double Tap":
                self.HTML = f"<img src = '{execute}' height = '60'> {self.getplayerimg()} was double tapped"
            elif self.note == "Judge":
                self.HTML = f"<img src = '{executejudge}' height = '60'> {self.getplayerimg()} was executed by the Judge"
                print("GET THE JUDGES NAME")
                exit()
                attacker = [x for x in gamestate['events'] if x.eventname == "Slayer Shot"][-1].player
                self.processdeath(attacker, [self.player], 'Executed')
            elif self.note == "Scarlet Pass":
                self.HTML = f"<img src = '{executejudge}' height = '60'> {self.getplayerimg()} was executed ({self.getroleimg('scarletwoman')}triggered)"
            else:
                print(self.__dict__)


        elif self.eventname == 'Demon Kill':
            demonattack = '/static/imgs/DemonKill.webp'
            demonattackblock = '/static/imgs/DemonKillBlocked.webp'
            targetplayer = self.targetlist[0]
            targetplayerpack = f"{targetplayer}{self.playerimagehtml(self.targetstatedict[targetplayer],size=50)}"
            if self.note == "Star Pass":
                self.HTML = f"{self.getplayerimg()} <img style='-webkit-transform: scaleX(-1); transform: " \
                            f"scaleX(-1);' src = '{demonattack}' height = '50'> <strong>STAR PASS</strong>"
            elif self.note == "Legion":
                self.HTML = f"{self.getroleimg('Legion', size=50)} <img src = '{demonattack}' height = '50'> " \
                       f"{targetplayerpack}"
            elif self.note == "Scarlet Pass":
                self.HTML = f"{self.getplayerimg()} <img style='-webkit-transform: scaleX(-1); transform: " \
                            f"scaleX(-1);' src = '{demonattack}' height = '50'> " \
                            f"{self.getroleimg('scarletwoman', size=40)} triggered"
            elif self.note != "":
                self.HTML = f"{self.getplayerimg()} <img src = '{demonattackblock}' height = '50'> " \
                       f"{targetplayerpack} {self.note}"
            else:
                self.HTML = f"{self.getplayerimg()} <img src = '{demonattack}' height = '50'> {targetplayerpack}"
            self.processdeath(self.player,[self.targetlist[0]],'Demon Kill')




        elif self.eventname == 'Game End':
            winner = None
            method = None
            img = None
            if self.note == 'Demon Executed':
                winner, method = "Good", "The Demon was Executed"
            elif self.note == 'Mayor Win':
                winner, method = "Good", "The Mayor Lives"
            elif self.note == 'Slayer Kill':
                winner, method = "Good", "The Slayer got the Demon"


            elif self.note == 'Saint Executed':
                winner, method = "Evil", "The Saint was Executed"
            elif self.note == 'Two Living Players':
                winner, method = "Evil", "Demon in final 2"
            elif self.note == 'No Execution - Vortox':
                winner, method = "Evil", f"No Execution with the {self.getroleimg('Vortox', size=40)}"

            elif self.note == 'Mastermind Execution':
                winner, method = self.targetlist[0], "Mastermind Triggered"


            if winner is None or method is None:
                print(self.__dict__)
            else:
                colour = "#09a5e3" if winner == "Good" else "#bd0000"
                if img is None:
                    self.HTML = f'<h1>Game End - <span style="color: {colour}">{winner} Win</span>' \
                                f'</h1><h4>{method}</h4>'
                else:
                    self.HTML = f'<h1>Game End - <span style="color: {colour}">{winner} Win</span>' \
                                f'</h1><h4>{method}</h4><img src = "{img}" width = "100%">'
                self.delta.append(["gamestate","Complete"])


        else:
            print(self.__dict__)
            exit()