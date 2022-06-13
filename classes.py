import copy

import pandas as pd



class Player:
    def __init__(self, name, role, alignment, note):
        self.name = name
        self.active = True
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

        e = Event(row["Session"], row["Game Number"], row["index"], row["Phase"], row["Action"],
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

    def getplayerimg(self, size=50):
        return f"<strong>{self.player}</strong> {self.playerimagehtml(self.playerstate, size=size)}"

    def gettargetpack(self,name,size=50):
        targetstate = self.targetstatedict[name]
        return f"<strong>{name}</strong> {self.playerimagehtml(targetstate,size=size)}"

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

    def processmissing(self):
        for k in self.__dict__:
            print(k, ":", [self.__dict__[k]])
        exit()

    def processevent(self, gamestate, votes, playervotes):
        if self.eventname in ['Lunatic Information','Minion Information','Demon Information']:

            if self.player in ['Legion']:
                self.HTML = f"Legion learns their team as expected"
            elif self.targetlist[0] in ['Standard']:
                self.HTML = f"{self.getplayerimg()} learns their team as expected"
            elif self.targetlist[0] in ['Poppy Grower']:
                pg = [x for x in gamestate['playerdata']
                          if gamestate['playerdata'][x]['currentrole'] == 'Poppy Grower'][0]
                pgpack = [gamestate['playerdata'][x] for x in gamestate['playerdata']
                              if gamestate['playerdata'][x]['currentrole'] == 'Poppy Grower'][0]
                self.HTML = f"<strong>{pg}</strong>{self.playerimagehtml(pgpack)} stops {self.getplayerimg()} learning their team"
            elif self.note in ['', 'Magician', 'Marionette']:
                team = " ".join([self.gettargetpack(x) for x in self.targetlist])
                self.HTML = f"{self.getplayerimg()} learns their team is {team}"
            else:
                self.processmissing()

        elif self.eventname in ['Mezepheles Word']:
            if self.note in ['']:
                self.HTML = f"{self.getplayerimg()} learns their Mezepheles word is <strong>{self.targetlist[0]}</strong>"
            else:
                self.processmissing()

        elif self.eventname in ['Lleech Host']:
            if self.note in ['']:
                self.HTML = f"{self.getplayerimg()} hosts {self.gettargetpack(self.targetlist[0])}"
            else:
                self.processmissing()

        elif self.eventname in ['Noble Information']:
            team = " ".join([self.gettargetpack(x) for x in self.targetlist])
            if self.note in ['']:
                self.HTML = f"{self.getplayerimg()} learns their in an evil among {team}"
            else:
                self.processmissing()

        elif self.eventname in ['Amnesiac Ability']:
            if self.note in ['', 'Poisoned']:
                self.HTML = f"{self.getplayerimg()} Amnesiac ability set as<br>" \
                            f"&nbsp;&nbsp;&nbsp;&nbsp;<strong>{self.targetlist[0]}</strong>"
            else:
                self.processmissing()

        elif self.eventname in ['Alchemist Ability']:
            if self.note in ['']:
                self.HTML = f"{self.getplayerimg()} gets the ability of {self.getroleimg(self.targetlist[0])}"
            else:
                self.processmissing()

        elif self.eventname in ['Pixie Information']:
            if self.note in ['']:
                self.HTML = f"{self.getplayerimg()} learns {self.getroleimg(self.targetlist[0])} is in play"
            else:
                self.processmissing()

        elif self.eventname in ['Bounty Hunter Information']:
            if self.note in ['']:
                self.HTML = f"{self.getplayerimg()} learns {self.getroleimg(self.targetlist[0])}"
            else:
                self.processmissing()

        elif self.eventname == 'Slayer Shot':
            slayershot = '/static/imgs/slayershot.webp'
            targetplayer = self.targetlist[0]
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} <img src = '{slayershot}' height = '50'> {self.gettargetpack(targetplayer)}"
            else:
                self.HTML = f"{self.getplayerimg()} <img src = '{slayershot}' height = '50'> {self.gettargetpack(targetplayer)} ({self.note})"
            self.delta.append([self.player, "abilityused", True])

        elif self.eventname == 'Snitch Bluffs':
            if self.note == '':
                bluffs = " ".join([self.getroleimg(x, size=40) for x in self.targetlist])
                self.HTML = f"{self.getplayerimg()} receives bluffs.<br> {bluffs}"
                for x in self.targetlist:
                    self.delta.append(["additional bluff used", x])
            else:
                self.processmissing()

        elif self.eventname == 'Godfather Information':
            if self.note == '':
                bluffs = " ".join([self.getroleimg(x, size=40) for x in self.targetlist])
                self.HTML = f"{self.getplayerimg()} learns the following are in play:<br>{bluffs}"
            else:
                self.processmissing()

        elif self.eventname in ['Washerwoman Information', 'Investigator Information', 'Librarian Information',
                                'Sage Information']:
            if self.targetlist[0] == "No Minion In Play":
                self.HTML = f"{self.getplayerimg()} discovered that there is no minion in play"
            elif self.note == '':
                if self.eventname == 'Sage Information':
                    pack = [self.gettargetpack(x) for x in self.targetlist]
                    role = "The Demon"
                else:
                    try:
                        pack = [self.gettargetpack(x) for x in self.targetlist[1:]]
                        role = self.getroleimg(self.targetlist[0])
                    except:
                        self.processmissing()

                self.HTML = f"{self.getplayerimg()} learns {pack[0]} or {pack[1]} is {role}"
            else:
                self.processmissing()

        elif self.eventname in ['Innkeeper Protect']:
            if self.note == '':
                pack = [self.gettargetpack(x) for x in self.targetlist]
                self.HTML = f"{self.getplayerimg()} selects {pack[0]} and {pack[1]}"
            else:
                self.processmissing()

        elif self.eventname in ['Grandmother Information']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} learns {self.gettargetpack(self.targetlist[0])} is {self.getroleimg(self.targetlist[1])}"
            else:
                self.processmissing()

        elif self.eventname in ['Seamstress Pick', 'Fortune Teller Information','Chambermaid Choice']:
            if self.note == '':
                pack = [self.gettargetpack(x) for x in self.targetlist[:2]]
                self.HTML = f"{self.getplayerimg()} selects {pack[0]} and {pack[1]} and learns a {self.targetlist[2]}"
            else:
                self.processmissing()

        elif 'Amnesiac Action' in self.eventname:
            if 'Amnesiac Action - Select 1 player with response' in self.eventname:
                self.HTML = f"{self.getplayerimg()} selects {self.gettargetpack(self.targetlist[0])} " \
                            f"and learns {self.targetlist[1]}"
            elif 'Amnesiac Action - Select 2 players with response' in self.eventname:
                self.HTML = f"{self.getplayerimg()} selects {self.gettargetpack(self.targetlist[0])} " \
                            f"and {self.gettargetpack(self.targetlist[1])} " \
                            f"and learns {self.targetlist[1]}"
            else:
                self.processmissing()

        elif self.eventname in ['Amnesiac Question']:
            self.HTML = f"{self.getplayerimg()} visits the story teller and asks:<br>" \
                        f"&nbsp;&nbsp;&nbsp;&nbsp;<strong>{self.targetlist[0]}</strong><br>" \
                        f"They learn:<br>" \
                        f"&nbsp;&nbsp;&nbsp;&nbsp;<strong>{self.note}</strong>"

        elif self.eventname in ['Artist Question']:
            if self.note in ['','Poisoned']:
                self.HTML = f"{self.getplayerimg()} visits the story teller and asks:<br>" \
                            f"&nbsp;&nbsp;&nbsp;&nbsp;<strong>{self.targetlist[0]}</strong><br>" \
                            f"They learn:<br>" \
                            f"&nbsp;&nbsp;&nbsp;&nbsp;<strong>{self.targetlist[1]}</strong>"
            else:
                self.processmissing()

        elif self.eventname in ['Savant Info']:
            if self.note in ['','Poisoned']:
                self.HTML = f"{self.getplayerimg()} visits the story teller and learns one of the following is true:<br>" \
                            f"&nbsp;&nbsp;<strong> {self.targetlist[0]}</strong><br>" \
                            f"&nbsp;&nbsp;<strong> {self.targetlist[1]}</strong>"
            else:
                self.processmissing()

        elif self.eventname in ['General Information']:
            if self.note in ['','Poisoned']:
                self.HTML = f"{self.getplayerimg()} learns <strong> {self.targetlist[0]}</strong>"
            else:
                self.processmissing()

        elif self.eventname in ['Roshambo']:
            selections = self.note.split("|")
            self.HTML = f"{self.getplayerimg()} plays Roshambo with {self.gettargetpack(self.targetlist[0])}<br>" \
                        f"&nbsp;&nbsp;{self.player} picks <strong>{selections[0]}</strong><br>" \
                        f"&nbsp;&nbsp;{self.targetlist[0]} picks <strong>{selections[1]}</strong>"

        elif self.eventname in ['Juggle','Gambler Choice']:
            if self.note in ['']:
                if self.eventname == 'Juggle':
                    verb = "juggles"
                elif self.eventname == 'Gambler Choice':
                    verb = "gambles"

                self.HTML = f"{self.getplayerimg()} {verb} " \
                            f"{self.gettargetpack(self.targetlist[0])} " \
                            f"as the {self.getroleimg(self.targetlist[1])}"
            else:
                self.processmissing()

        elif self.eventname in ['Gossip']:
            if self.note in ['']:
                self.HTML = f"{self.getplayerimg()} gossips " \
                            f"{self.targetlist[0]}"
            else:
                self.processmissing()

        elif self.eventname in ['Barista Ability']:
            if self.note in ['1']:
                self.HTML = f"{self.getplayerimg()} caused {self.gettargetpack(self.targetlist[0])} to become sober, " \
                            f"healthy & get true info"
                self.delta.append([self.targetlist[0], "ill", False])
            elif self.note in ['2']:
                self.HTML = f"{self.getplayerimg()} causes {self.gettargetpack(self.targetlist[0])} to fire " \
                            f"their ability twice"
            else:
                self.processmissing()

        elif self.eventname in ['Oracle Number','Chef Number','Mathematician Number','Empath Number',
                                'Clockmaker Number','Juggler Information','Flowergirl Information',
                                'Town Crier Information']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} learns a <strong>{self.targetlist[0]}</strong>"
            else:
                self.processmissing()

        elif self.eventname in ['Monk Protect']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} protects " \
                            f"{self.gettargetpack(self.targetlist[0])}"
            else:
                self.processmissing()

        elif self.eventname in ['Philosopher Switch', 'Cannibal Ability']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} gains the ability of " \
                            f"{self.getroleimg(self.targetlist[0])}"
            else:
                self.processmissing()

        elif self.eventname in ['Dreamer Check']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} selects {self.gettargetpack(self.targetlist[0])} and " \
                            f"learns they are {self.getroleimg(self.targetlist[1])} " \
                            f"or {self.getroleimg(self.targetlist[2])}"
            else:
                self.processmissing()

        elif self.eventname in ['Undertaker Information']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} learns {self.getroleimg(self.targetlist[0])} was executed"
            else:
                self.processmissing()

        elif self.eventname in ['Select Barber Swap']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} switches the roles of  " \
                            f"{self.gettargetpack(self.targetlist[0])} into " \
                            f"{self.gettargetpack(self.targetlist[1])}"
            else:
                self.processmissing()

        elif self.eventname in ['Witch Pick', 'Picks Master', 'Poisoner Pick', 'Snake Charmer Pick','Drinking Buddy',
                                'DA Protection', 'Klutz Pick', 'Lunatic Pick', 'Exorcist Pick', 'Lycanthrope Pick',
                                'Nightwatchman Pick']:
            if self.note == '':
                pack = " ".join([self.gettargetpack(x) for x in self.targetlist])
                verb = {'Witch Pick':'curses',
                        'Picks Master':'picks there master as',
                        'Poisoner Pick':'attempts to poison',
                        'Snake Charmer Pick':'attempts to snake charm',
                        'Drinking Buddy':'chooses their drinking buddy as',
                        'DA Protection':'DA protects',
                        'Klutz Pick':'chooses their drinking buddy as',
                        'Lunatic Pick':'makes their "demon" pick and selects',
                        'Exorcist Pick':'tries to excise',
                        'Lycanthrope Pick':'tries to turn',
                        'Nightwatchman Pick':'reveals themselves to'}
                self.HTML = f"{self.getplayerimg()} {verb[self.eventname]} " \
                            f"{pack}"
            else:
                self.processmissing()

        elif self.eventname in ['Damsel Guess']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} guesses {self.gettargetpack(self.targetlist[0])} as the Damsel"
            else:
                self.processmissing()

        elif self.eventname in ['Courtier Pick']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} picks " \
                            f"{self.getroleimg(self.targetlist[0])}"
            else:
                self.processmissing()

        elif self.eventname in ['Cerenovus Madness']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} makes " \
                            f"{self.gettargetpack(self.targetlist[0])} mad that they are " \
                            f"{self.getroleimg(self.targetlist[1])}"
            else:
                self.processmissing()

        elif self.eventname in ['Pit-Hag Pick']:
            if self.note != '':
                self.HTML = f"{self.getplayerimg()} changes " \
                            f"{self.gettargetpack(self.targetlist[0])} into " \
                            f"{self.getroleimg(self.note)}"
            else:
                self.processmissing()

        elif self.eventname in ['No Dashii Poison']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} poisons their neighbours " \
                            f"{self.gettargetpack(self.targetlist[0])} and " \
                            f"{self.gettargetpack(self.targetlist[1])}"
            else:
                self.processmissing()

        elif self.eventname in ['Evil Twin Information', 'Good Twin Information']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} see their twin as {self.gettargetpack(self.targetlist[0])}"
            else:
                self.processmissing()

        elif self.eventname in ['Vigormortis Poison']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} poisons {self.gettargetpack(self.targetlist[0])}"
            else:
                self.processmissing()

        elif self.eventname in ['Knows Widow']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} heard the Widow's call"
            else:
                self.processmissing()

        elif self.eventname in ['Pukka Poison','Widow Poison']:
            verbs = {'Pukka Poison':'Pukka Poisoned','Widow Poison':'Widow Poisoned'}

            if self.note == '':
                self.HTML = f"{self.getplayerimg()} {verbs[self.eventname]} {self.gettargetpack(self.targetlist[0])}"
                self.delta.append([self.targetlist[0], "ill", True])
            elif self.note == 'Drunk':
                self.HTML = f"{self.getplayerimg()} tried to {self.eventname} {self.gettargetpack(self.targetlist[0])}"
            else:
                self.processmissing()

        elif self.eventname in ['Poisoned','Drunked','Philosopher Drunk','Snake Charm Poison','Goon Drunk',
                                'Innkeeper Drunk']:
            if self.eventname == 'Snake Charm Poison':
                self.eventname = 'Snake Charm Poisoned'
            elif self.eventname == 'Pukka Poison':
                self.eventname = 'Pukka Poisoned'

            if self.note == '':
                self.HTML = f"{self.getplayerimg()} became {self.eventname}"
                self.delta.append([self.targetlist[0], "ill", True])
            elif self.note == 'Drunk':
                self.HTML = f"{self.getplayerimg()} did not became {self.eventname}"
            else:
                self.processmissing()

        elif self.eventname == 'Healthy':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} became Healthy"
                self.delta.append([self.targetlist[0], "ill", False])
            else:
                self.processmissing()

        elif self.eventname == 'Role Change':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} had their role changed to {self.getroleimg(self.targetlist[0])}"
                self.delta.append([self.player, "currentrole", self.targetlist[0]])
            else:
                self.processmissing()

        elif self.eventname == 'Alignment Change':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} had their alignment changed to {self.getroleimg(self.targetlist[0])}"
                self.delta.append([self.player, "currentalignment", self.targetlist[0]])
            else:
                self.HTML = f"{self.getplayerimg()} had their alignment changed to {self.getroleimg(self.targetlist[0])} ({self.note})"
                self.delta.append([self.player, "currentalignment", self.targetlist[0]])

        elif self.eventname == 'Doomsay':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} Doomsays"
            else:
                self.processmissing()

        elif self.eventname == 'Po Charge':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} charges up"
            else:
                self.processmissing()

        elif self.eventname == 'Killed':
            if self.note == 'Slayer Kill':
                self.HTML = f"{self.getplayerimg()} is killed by the Slayer"
                attacker = [x for x in gamestate['events'] if x.eventname == "Slayer Shot"][-1].player
                self.processdeath(attacker, [self.player], 'Slayer Kill')
            elif self.note == 'Doomsay':
                self.HTML = f"{self.getplayerimg()} is killed by the Doomsayer"
                attacker = [x for x in gamestate['events'] if x.eventname == "Doomsay"][-1].player
                self.processdeath(attacker, [self.player], 'Doomsay')
            elif self.note == 'Lleech Host':
                self.HTML = f"{self.getplayerimg()} dies along side there host"
                self.processdeath(None, [self.player], 'Lleech Host')
            elif self.note == 'Failed Gamble':
                self.HTML = f"{self.getplayerimg()} bet doesn't come in and dies"
                self.processdeath(self.player, [self.player], 'Failed Gamble')
            elif self.note == 'Gunslinger':
                gunslinger = [x for x in gamestate['playerdata']
                          if gamestate['playerdata'][x]['currentrole'] == 'Gunslinger'][0]
                gunslingerpack = [gamestate['playerdata'][x] for x in gamestate['playerdata']
                              if gamestate['playerdata'][x]['currentrole'] == 'Gunslinger'][0]
                self.HTML = f"{self.getplayerimg()} is targeted by {self.playerimagehtml(gunslingerpack)}"
                self.processdeath(gunslinger, [self.player], 'Gunslinger Kill')
            else:
                self.processmissing()

        elif self.eventname == 'Riot Kill':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} get their riot on with {self.gettargetpack(self.targetlist[0])}"
                self.processdeath(self.player, [self.targetlist[0]], 'Riot Kill')
            else:
                self.processmissing()

        elif self.eventname == 'Mayor Kill':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} bounces the kill onto {self.gettargetpack(self.targetlist[0])}"
                self.processdeath(self.player, [self.targetlist[0]], 'Mayor Kill')
            else:
                self.processmissing()

        elif self.eventname == 'Virgin Kill':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} Virgin kills {self.gettargetpack(self.targetlist[0])}"
                self.processdeath(self.player, [self.targetlist[0]], 'Virgin Kill')
            else:
                self.processmissing()

        elif self.eventname == 'Assassin Kill':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} assassinates {self.gettargetpack(self.targetlist[0])}"
                self.processdeath(self.player, [self.targetlist[0]], 'Assassin Kill')
            else:
                self.processmissing()

        elif self.eventname == 'Psychopath Kill':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} ends {self.gettargetpack(self.targetlist[0])}"
                self.processdeath(self.player, [self.targetlist[0]], 'Psychopath Kill')
            else:
                self.processmissing()

        elif self.eventname == 'Tinker Kill':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} spontaneously dies"
                self.processdeath(None, [self.targetlist[0]], 'Tinker Kill')
            else:
                self.processmissing()

        elif self.eventname == 'Cerenovus Execution':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} is executed for breaking madness"
                cere = [x for x in gamestate['playerdata']
                        if gamestate['playerdata'][x]['currentrole'] == 'Cerenovus'][0]
                self.processdeath(cere, [self.player], 'Cere Kill')
            else:
                self.processmissing()

        elif self.eventname == 'Gossip Kill':
            if self.note == '':
                gossip = [x for x in gamestate['playerdata']
                          if gamestate['playerdata'][x]['currentrole'] == 'Gossip'][0]
                gossippack = [gamestate['playerdata'][x] for x in gamestate['playerdata']
                          if gamestate['playerdata'][x]['currentrole'] == 'Gossip'][0]
                self.HTML = f"{self.getplayerimg()} dies to the {self.playerimagehtml(gossippack)}"
                self.processdeath(gossip, [self.player], 'Gossip Kill')
            else:
                self.processmissing()

        elif self.eventname in ['Boomdandy Slaughter','Boomdandy Vote Kill']:
            boomdandykill = '/static/imgs/boomdandykill.webp'
            if self.note == '':
                self.HTML = f"<img src = '{boomdandykill}' height = '75'>{self.gettargetpack(self.targetlist[0])} gets caught in the explosion"
                self.processdeath(self.player, [self.targetlist[0]], 'Boomdandy Slaughter')
            else:
                self.processmissing()

        elif self.eventname == 'Exiled':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} was Exiled"
                self.processdeath(None, [self.player], 'Exiled')
            else:
                self.processmissing()

        elif self.eventname == 'Witch Kill':
            if self.note == '':
                witch = [x for x in gamestate['playerdata']
                          if gamestate['playerdata'][x]['currentrole'] == 'Witch'][0]
                witchpack = [gamestate['playerdata'][x] for x in gamestate['playerdata']
                          if gamestate['playerdata'][x]['currentrole'] == 'Witch'][0]
                self.HTML = f"{self.getplayerimg()} dies to the {self.playerimagehtml(witchpack)}"
                self.processdeath(witch, [self.player], 'Witch Kill')
            else:
                self.processmissing()

        elif self.eventname == 'Nomination':
            clockhand = '/static/imgs/clock.webp'
            targetplayerpack = self.getroleimg(self.targetlist[0])

            if self.note != 'No Vote':
                print("FINISH SORTING REPORTING OF THE VOTE!")
                voteid = f"{self.session}-{self.game}-{str(self.note)[1:]}"
                #print(voteid)
                #print([x for x in votes.to_dict("records") if x['voteid'] == voteid][0])
                #print({x['Player']:x['Voted'] for x in playervotes.to_dict("records") if x['voteid'] == voteid})
                #votes, playervotes
                self.HTML = f"{self.getplayerimg()} <img src = '{clockhand}' height = '30'> {targetplayerpack}"
            elif self.note == 'No Vote':
                self.HTML = f"{self.getplayerimg()} <img src = '{clockhand}' height = '30'> {targetplayerpack}"
            else:
                self.processmissing()

        elif self.eventname == 'Boomdandy Vote':
            if self.note != 'No Vote':
                print("FINSIH SORTING REPORTING OF THE VOTE!")
                voteid = f"{self.session}-{self.game}-{str(self.note)[1:]}"
                #print(voteid)
                #print([x for x in votes.to_dict("records") if x['voteid'] == voteid][0])
                #print({x['Player']:x['Voted'] for x in playervotes.to_dict("records") if x['voteid'] == voteid})
                #votes, playervotes
                self.HTML = f"FINISH SORTING REPORTING OF THE Boomdandy Vote"
            else:
                self.processmissing()

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
                judge = [x for x in gamestate['playerdata']
                          if gamestate['playerdata'][x]['currentrole'] == 'Judge'][0]
                judgepack = [gamestate['playerdata'][x] for x in gamestate['playerdata']
                              if gamestate['playerdata'][x]['currentrole'] == 'Judge'][0]
                self.HTML = f"<img src = '{executejudge}' height = '60'> {self.getplayerimg()} was executed by" \
                            f"{self.playerimagehtml(judgepack)}"
                self.processdeath(judge, [self.player], 'Judge Executed')
            elif self.note == "Scarlet Pass":
                self.HTML = f"<img src = '{execute}' height = '60'> {self.getplayerimg()} was executed ({self.getroleimg('scarletwoman')}triggered)"
            else:
                self.processmissing()


        elif self.eventname == 'Demon Kill':
            demonattack = '/static/imgs/DemonKill.webp'
            demonattackblock = '/static/imgs/DemonKillBlocked.webp'
            targetplayerpack = self.gettargetpack(self.targetlist[0])
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

        elif self.eventname == 'Shabaloth Resurrect':
            p = self.targetlist[0]
            targetplayerpack = self.gettargetpack(p)
            self.HTML = f"{self.getplayerimg()} resurrects {targetplayerpack}"
            self.delta.append([p, "alive", True])

        elif self.eventname == 'Player Left Game':
            self.HTML = f"{self.getplayerimg()} left the game"
            self.delta.append([self.targetlist[0], "active", False])


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
                self.processmissing()
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
            self.processmissing()