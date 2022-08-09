import copy
import pandas as pd
from collections import Counter as cnt
import CharacterJSONprocess
RoleTypesdf = CharacterJSONprocess.getrolesdf()
RoleTypesdfdict = RoleTypesdf.to_dict("records")
RoleSidedict = {x['Role']:x['Side'] for x in RoleTypesdfdict}
RoleTypesdict = {x['Role']:x['Type'] for x in RoleTypesdfdict}

class Player:
    def __init__(self, name, role, alignment, note, type):
        self.name = name
        self.active = True
        self.startingrole = role
        self.rolenote = note
        self.currentrole = role
        self.startingalignment = alignment
        self.startingtype = type
        self.currentalignment = alignment
        self.currenttype = type
        self.alive = True
        self.deadvoteused = False
        self.hasability = False
        self.abilityused = False
        self.poisoned = False
        self.startingroleimg = None
        self.roleimg = None
        self.win = None


        self.deaths = []
        self.kills = []

    def startcommand(self):
        self.rolechange(self.currentrole)
        self.startingroleimg = self.getroleimg()

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

        inactive = "active" if self.active else "inactive"

        self.roleimg = f"https://raw.githubusercontent.com/SDoehren/AFBOTCSite/main/app/static/tokenimgs/{roleconverted}-{alignment}-{health}-{ability}-{alive}-{inactive}.webp"
        return self.roleimg

    def rolechange(self, newrole):
        self.currentrole = newrole
        self.startingtype = RoleTypesdict[newrole]

        singleuseability = ['Slayer', 'Virgin', 'Assassin', 'Mastermind', 'Courtier', 'Fool', 'Professor',
                            'Artist', 'Philosopher', 'Seamstress', 'Mezepheles', 'Damsel', 'Golem', 'Fisherman',
                            'Huntsman', 'Pixie', 'King', 'Engineer', 'Nightwatchman', 'Bone Collector',
                            'Judge', 'Scapegoat']
        if newrole in singleuseability:
            self.hasability = True
            self.abilityused = False
        else:
            self.hasability = False
            self.abilityused = False

        self.getroleimg()


class Game:
    def __init__(self, date, session, game, script, result, players):
        self.playerobjs = {}
        self.playerorder = []
        self.date = date
        self.session = session
        self.game = game
        self.script = script
        self.result = result
        self.winmethod = None
        self.players = players
        self.demonbluffs = []
        self.additionalbluffs = []
        self.storytellers = []
        self.eventdf = None
        self.votedf = None
        self.playervotedf = None
        self.events = None
        self.setup = {"Townsfolk": 0, "Outsider": 0, "Minion": 0, "Demon": 0, "Travellers": 0}
        self.setupstr = ""

        self.startofphasestate = {}
        self.imagesrequired = []

        self.allrolesused = []

    def __repr__(self):
        return f"<classes.Game object - {self.session}-{self.game}>"

    def gamejson(self):
        return self.__dict__

    def gamesummary(self):
        return [self.result, self.winmethod]

    def getid(self):
        return f"{self.session}-{self.game}"

    def addplayer(self, name, role, alignment, note, type):
        p = Player(name, role, alignment, note, type)
        self.setup[type] +=1

        if self.setup["Travellers"]>0:
            self.setupstr = f'{self.setup["Townsfolk"]}-{self.setup["Outsider"]}-{self.setup["Minion"]}-{self.setup["Demon"]} ({self.setup["Travellers"]})'
        else:
            self.setupstr = f'{self.setup["Townsfolk"]}-{self.setup["Outsider"]}-{self.setup["Minion"]}-{self.setup["Demon"]}'
        self.playerorder.append(name)
        self.playerobjs[p.name] = p

    def getgamestate(self):
        d = self.__dict__
        d['playerdata'] = {x: d['playerobjs'][x].getplayerstate() for x in d['playerobjs']}
        d = copy.deepcopy(d)
        del d['playerobjs']
        return d

    def processgame(self):
        print(f"{self.session}-{self.game}")
        for x in self.playerobjs:
            self.playerobjs[x].startcommand()

        self.votedf["voteid"] = self.votedf['gameid'].astype(str) + "-" + self.votedf['Vote Number'].astype(str)
        self.playervotedf["voteid"] = self.playervotedf['gameid'].astype(str) + "-" + self.playervotedf[
            'Vote Number'].astype(str)

        v = self.votedf.copy(deep=True)
        pv = self.playervotedf.copy(deep=True)

        t = self.eventdf.copy(deep=True)
        t = t.reset_index()
        self.events = []
        for ind, r in t.iterrows():
            self.events.append(self.processevent(r, v, pv))
        self.imagesrequired = set(self.imagesrequired)

    def processevent(self, row, votes, playervotes):
        # print(row)
        #print(f'{row["Session"]}-{row["Game Number"]}-{row["Phase"]}')
        actiontaker = None if pd.isnull(row["Player"]) else row["Player"]
        if actiontaker == "Legion":
            actiontakerstate = "Legion"
        elif actiontaker == 'Storyteller':
            actiontakerstate = 'Storyteller'
        elif actiontaker is not None:
            actiontakerstate = self.playerobjs[actiontaker].getplayerstate()
        else:
            actiontakerstate = None

        targetlist = [x for x in row["Target"].split("|")]
        targetstatedict = {x: self.playerobjs[x].getplayerstate() for x in targetlist if x in self.playerobjs}

        if row["Phase"] not in self.startofphasestate:
            imgs = []
            for x in self.playerobjs:
                obj = self.playerobjs[x]
                imgs.append([obj.name, obj.currentrole, obj.roleimg])
                if obj.currentrole not in self.allrolesused:
                    self.allrolesused.append(obj.currentrole)

            self.startofphasestate[row["Phase"]] = imgs

        gamestate = self.getgamestate()
        playerpack = gamestate['playerdata']
        e = Event(row["Session"], row["Game Number"], row["index"], row["Phase"], row["Action"],
                  actiontaker, actiontakerstate, targetlist, targetstatedict, row["Note"], playerpack)
        e.processevent(gamestate, votes, playervotes)

        d = self.getgamestate()['playerdata']
        self.imagesrequired += [d[x]['roleimg'] for x in d]

        # print(row["Session"], row["Game Number"], row["index"], row["Phase"], row["Action"], actiontaker,
        # actiontakerstate, targetlist, targetstatedict, row["Note"])
        self.processdelta(e.delta)

        # print(getattr(e,'avsavs',None))
        # print(setattr(e,'session',99))
        for x in self.playerobjs:
            self.playerobjs[x].getroleimg()
            if self.playerobjs[x].currentrole not in self.allrolesused:
                self.allrolesused.append(self.playerobjs[x].currentrole)

        return copy.deepcopy(e)

    def processdelta(self, delta):
        for d in delta:
            player, event, action = d
            if player == 'Storyteller':
                continue
            if event in ['alive', 'active', 'poisoned', 'currentalignment', 'abilityused']:
                setattr(self.playerobjs[player], event, action)
            elif event == 'killed':
                killer, method = action
                self.playerobjs[player].deaths.append((killer, method))
                if killer is not None:
                    self.playerobjs[killer].kills.append((player, method))
            elif event == 'win condition':
                self.winmethod = action[0]
                for p in self.playerobjs:
                    self.playerobjs[p].win = self.playerobjs[p].currentalignment == action[1]
            elif event == 'additional bluff used':
                self.additionalbluffs.append(action)
            elif event == 'currentrole':
                self.playerobjs[player].rolechange(action)
            else:
                print(d)


class Event:
    def __init__(self, session, game, eventnumber, phase, eventname, player, playerstate, targetlist, targetstatedict,
                 note,playerpack):
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
        self.playerpack = playerpack
        self.HTML = f"UNPROCESSED - {session}-{game}-{eventnumber} {phase} {player} {eventname} {'|'.join(targetlist)} {note}"

        self.death = False
        self.killer = None
        self.killed = []
        self.methodofdeath = None

        self.vote = False
        self.voteHTML = ""

        self.nomination = []
        self.voterpack = []

    def playerimagehtml(self, playerstate, size=50):
        roleimg = playerstate['roleimg']
        name = playerstate['name']
        role = playerstate['currentrole']
        return f'<img src = "{roleimg}" height = "{size}" ' \
               f'data-bs-toggle="tooltip" data-toggle="tooltip" data-bs-placement="bottom" title="" data-bs-original-title="{name}-{role}">'

    def getroleimg(self, role, size=50):
        if role == "ST":
            address = "https://raw.githubusercontent.com/bra1n/townsquare/develop/src/assets/demon-head.png"
        else:
            roleconverted = role.replace("'", '').replace(' ', '').replace('-', '').lower()
            address = f"https://raw.githubusercontent.com/SDoehren/AFBOTCSite/main/app/static/tokenimgs/{roleconverted}.webp"

        return f'<img src = "{address}" height = "{size}" data-bs-toggle="tooltip" ' \
               f'data-bs-placement="bottom" title="" data-bs-original-title="{role}">'

    def getplayerimg(self, size=50):
        if self.player == "Storyteller":
            address = "https://raw.githubusercontent.com/bra1n/townsquare/develop/src/assets/demon-head.png"
            img = f'<img src = "{address}" height = "{size}" data-bs-toggle="tooltip" ' \
                  f'data-bs-placement="bottom" title="" data-bs-original-title="Storyteller">'
            return f"<strong>Storyteller</strong> {img}"

        return f"<strong>{self.player}</strong> {self.playerimagehtml(self.playerstate, size=size)}"

    def gettargetpack(self, name, size=50):
        if name == "Storyteller":
            address = "https://raw.githubusercontent.com/bra1n/townsquare/develop/src/assets/demon-head.png"
            img = f'<img src = "{address}" height = "{size}" data-bs-toggle="tooltip" ' \
               f'data-bs-placement="bottom" title="" data-bs-original-title="Storyteller">'
            return f"<strong>Storyteller</strong> {img}"

        targetstate = self.targetstatedict[name]
        targimg = self.playerimagehtml(targetstate, size=size)
        return f"<strong>{name}</strong> {targimg}"

    def processdeath(self, killer, killed, method):
        for p in killed:
            self.delta.append([p, "alive", False])
            self.delta.append([p, "killed", (killer, method)])
            self.killed.append(p)
        self.death = True
        self.killer = killer
        self.methodofdeath = method

    def playerabilityused(self):
        self.delta.append([self.player, "abilityused", True])

    def roleabilityused(self, role, gamestate):
        roleplayer = [x for x in gamestate['playerdata'] if gamestate['playerdata'][x]['currentrole'] == role]
        if len(roleplayer) > 0:
            roleplayer = roleplayer[0]
            self.delta.append([roleplayer, "abilityused", True])

    def processmissing(self):
        for k in self.__dict__:
            print(k, ":", [self.__dict__[k]])
        exit()

    def processevent(self, gamestate, votes, playervotes):
        if self.eventname in ['Lunatic Information', 'Minion Information', 'Demon Information']:

            if self.player in ['Legion']:
                self.HTML = f"Legion learns their team as expected"
            elif self.targetlist[0] in ['None']:
                self.HTML = f"{self.getplayerimg()} learns nothing about their team"
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

        elif self.eventname in ['Revolutionary Pair Information']:
            if self.note in ['']:
                self.HTML = f"{self.getplayerimg()} {self.getroleimg('Revolutionary')} {self.gettargetpack(self.targetlist[0])}"
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

        elif self.eventname in ['Pixie Ability']:
            if self.note in ['']:
                self.HTML = f"{self.getplayerimg()} gains the ability of {self.getroleimg(self.targetlist[0])}"
                self.playerabilityused()
            else:
                self.processmissing()

        elif self.eventname in ['Bounty Hunter Information']:
            if self.note in ['']:
                self.HTML = f"{self.getplayerimg()} learns {self.gettargetpack(self.targetlist[0])}"
            elif self.note == 'Revolutionary':
                pack = [self.gettargetpack(x) for x in self.targetlist[:2]]
                self.HTML = f"{self.getplayerimg()} learns {self.gettargetpack(self.targetlist[0])} {self.getroleimg('Revolutionary')}"
            else:
                self.processmissing()

        elif self.eventname == 'Slayer Shot':
            slayershot = '/static/imgs/slayershot.webp'
            targetplayer = self.targetlist[0]
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} <img src = '{slayershot}' height = '50'> " \
                            f"{self.gettargetpack(targetplayer)}"
            else:
                self.HTML = f"{self.getplayerimg()} <img src = '{slayershot}' height = '50'> " \
                            f"{self.gettargetpack(targetplayer)} ({self.note})"
            self.playerabilityused()

        elif self.eventname == 'Snitch Bluffs':
            if self.note == '':
                bluffs = " ".join([self.getroleimg(x, size=40) for x in self.targetlist])
                self.HTML = f"{self.getplayerimg()} receives bluffs.<br> {bluffs}"
                for x in self.targetlist:
                    self.delta.append([None, "additional bluff used", x])
            else:
                self.processmissing()

        elif self.eventname == 'Godfather Information':
            if self.note == '':
                bluffs = " ".join([self.getroleimg(x, size=40) for x in self.targetlist])
                self.HTML = f"{self.getplayerimg()} learns the following are in play:<br>{bluffs}"
            elif self.note == 'No outsiders':
                self.HTML = f"{self.getplayerimg()} learns that no outsiders are in player"
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
                    pack = [self.gettargetpack(x) for x in self.targetlist[1:]]
                    role = self.getroleimg(self.targetlist[0])
                self.HTML = f"{self.getplayerimg()} learns {pack[0]} or {pack[1]} is {role}"
            else:
                self.processmissing()

        elif self.eventname in ['Innkeeper Protect']:
            if self.note == '':
                pack = [self.gettargetpack(x) for x in self.targetlist]
                self.HTML = f"{self.getplayerimg()} selects {pack[0]} and {pack[1]}"
            else:
                self.processmissing()

        elif self.eventname in ['Grandmother Information', 'Ravenkeeper Information']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} learns {self.gettargetpack(self.targetlist[0])} is " \
                            f"{self.getroleimg(self.targetlist[1])}"
            else:
                self.processmissing()

        elif self.eventname in ['Harlot Information']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} learns {self.getroleimg(self.targetlist[0])}"
            else:
                self.processmissing()

        elif self.eventname in ['Seamstress Pick', 'Fortune Teller Information', 'Chambermaid Choice']:
            if self.note == '':
                pack = [self.gettargetpack(x) for x in self.targetlist[:2]]
                self.HTML = f"{self.getplayerimg()} selects {pack[0]} and {pack[1]} and learns a {self.targetlist[2]}"
            elif self.note == 'Fibbin':
                pack = [self.gettargetpack(x) for x in self.targetlist[:2]]
                self.HTML = f"{self.getplayerimg()} selects {pack[0]} and {pack[1]} and learns a {self.targetlist[2]} {self.getroleimg('Fibbin')}"
            else:
                self.processmissing()

            if self.eventname in ['Seamstress Pick']:
                self.playerabilityused()

        elif 'Amnesiac Action' in self.eventname:
            if 'Amnesiac Action - Select 1 player with response' in self.eventname:
                self.HTML = f"{self.getplayerimg()} selects {self.gettargetpack(self.targetlist[0])} " \
                            f"and learns {self.targetlist[1]}"
            elif 'Amnesiac Action - Select 2 players with response' in self.eventname:
                self.HTML = f"{self.getplayerimg()} selects {self.gettargetpack(self.targetlist[0])} " \
                            f"and {self.gettargetpack(self.targetlist[1])} " \
                            f"and learns {self.targetlist[1]}"
            elif 'Amnesiac Action - Select 1 character with response' in self.eventname:
                self.HTML = f"{self.getplayerimg()} selects {self.getroleimg(self.targetlist[0])} " \
                            f"and learns {self.targetlist[1]}"
            elif 'Amnesiac Action - Select 1 player' in self.eventname:
                self.HTML = f"{self.getplayerimg()} selects {self.getroleimg(self.targetlist[0])}"
            else:
                self.processmissing()

        elif self.eventname in ['Amnesiac Question']:
            self.HTML = f"{self.getplayerimg()} visits the story teller and asks:<br>" \
                        f"&nbsp;&nbsp;&nbsp;&nbsp;<strong>{self.targetlist[0]}</strong><br>" \
                        f"They learn:<br>" \
                        f"&nbsp;&nbsp;&nbsp;&nbsp;<strong>{self.note}</strong>"

        elif self.eventname in ['Artist Question']:
            if self.note in ['', 'Poisoned']:
                self.HTML = f"{self.getplayerimg()} visits the story teller and asks:<br>" \
                            f"&nbsp;&nbsp;&nbsp;&nbsp;<strong>{self.targetlist[0]}</strong><br>" \
                            f"They learn:<br>" \
                            f"&nbsp;&nbsp;&nbsp;&nbsp;<strong>{self.targetlist[1]}</strong>"
            else:
                self.processmissing()
            self.playerabilityused()

        elif self.eventname in ['Savant Info']:
            if self.note in ['', 'Poisoned']:
                self.HTML = f"{self.getplayerimg()} visits the story teller and learns one of the following is true:<br>" \
                            f"&nbsp;&nbsp;<strong> {self.targetlist[0]}</strong><br>" \
                            f"&nbsp;&nbsp;<strong> {self.targetlist[1]}</strong>"
            else:
                self.processmissing()

        elif self.eventname in ['General Information', 'Fisherman Information', 'Balloonist Information']:
            if self.note in ['', 'Poisoned']:
                self.HTML = f"{self.getplayerimg()} learns <strong> {self.targetlist[0]}</strong>"
            else:
                self.processmissing()

            if self.eventname == 'Fisherman Information':
                self.playerabilityused()

        elif self.eventname in ['Roshambo']:
            selections = self.note.split("|")
            self.HTML = f"{self.getplayerimg()} plays Roshambo with {self.gettargetpack(self.targetlist[0])}<br>" \
                        f"&nbsp;&nbsp;{self.player} picks <strong>{selections[0]}</strong><br>" \
                        f"&nbsp;&nbsp;{self.targetlist[0]} picks <strong>{selections[1]}</strong>"

        elif self.eventname in ['Juggle', 'Gambler Choice']:
            if self.note in ['']:
                if self.eventname == 'Juggle':
                    verb = "juggles"
                elif self.eventname == 'Gambler Choice':
                    verb = "gambles"
                else:
                    verb = "Something done fucked, see line 350ish"

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
                self.delta.append([self.targetlist[0], "poisoned", False])
            elif self.note in ['2']:
                self.HTML = f"{self.getplayerimg()} causes {self.gettargetpack(self.targetlist[0])} to fire " \
                            f"their ability twice"
            else:
                self.processmissing()

        elif self.eventname in ['Oracle Number', 'Chef Number', 'Mathematician Number', 'Empath Number',
                                'Clockmaker Number', 'Juggler Information', 'Flowergirl Information',
                                'Town Crier Information']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} learns a <strong>{self.targetlist[0]}</strong>"
            elif self.note == 'Fibbin':
                self.HTML = f"{self.getplayerimg()} learns a <strong>{self.targetlist[0]}</strong> {self.getroleimg('Fibbin')}"
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

            if self.eventname == 'Philosopher Switch':
                self.playerabilityused()

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

        elif self.eventname in ['Witch Pick', 'Picks Master', 'Poisoner Pick', 'Snake Charmer Pick', 'Drinking Buddy',
                                'DA Protection', 'Klutz Pick', 'Lunatic Pick', 'Exorcist Pick', 'Lycanthrope Pick',
                                'Nightwatchman Pick', 'Huntsman Pick', 'Harlot Pick', 'Fiddler Choice',
                                'Fearmonger Pick','Professor Choice']:
            if self.note == '':
                pack = " ".join([self.gettargetpack(x) for x in self.targetlist])
                verb = {'Witch Pick': 'curses',
                        'Picks Master': 'picks their master as',
                        'Poisoner Pick': 'attempts to poison',
                        'Snake Charmer Pick': 'attempts to snake charm',
                        'Drinking Buddy': 'chooses their drinking buddy as',
                        'DA Protection': 'DA protects',
                        'Klutz Pick': 'sees the good in',
                        'Lunatic Pick': 'makes their "demon" pick and selects',
                        'Exorcist Pick': 'tries to excise',
                        'Lycanthrope Pick': 'tries to turn',
                        'Nightwatchman Pick': 'reveals themselves to',
                        'Huntsman Pick': 'hopes their Damsel is',
                        'Fiddler Choice': 'fiddles the game and chooses to go against',
                        'Harlot Pick': 'asks to see the role of',
                        'Fearmonger Pick':'strikes fear into',
                        'Professor Choice':'tries to revive'}
                self.HTML = f"{self.getplayerimg()} {verb[self.eventname]} " \
                            f"{pack}"
            else:
                self.processmissing()

            if self.eventname in ['Nightwatchman Pick', 'Huntsman Pick']:
                self.playerabilityused()

        elif self.eventname in ['Harlot Choice']:
            if self.targetlist[0] == 'Yes':
                self.HTML = f"{self.getplayerimg()} agrees to share their role"
            else:
                self.HTML = f"{self.getplayerimg()} refuses to share their role"

        elif self.eventname in ['Damsel Guess']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} guesses {self.gettargetpack(self.targetlist[0])} as the Damsel"
            else:
                self.processmissing()
            self.roleabilityused("Damsel", gamestate)

        elif self.eventname in ['Courtier Pick']:
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} picks " \
                            f"{self.getroleimg(self.targetlist[0])}"
            else:
                self.processmissing()
            self.playerabilityused()

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
                self.delta.append([self.targetlist[0], "poisoned", True])
                self.delta.append([self.targetlist[1], "poisoned", True])
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

        elif self.eventname in ['Pukka Poison', 'Widow Poison']:
            verbs = {'Pukka Poison': 'Pukka Poisoned', 'Widow Poison': 'Widow Poisoned'}

            if self.note == '':
                self.HTML = f"{self.getplayerimg()} {verbs[self.eventname]} {self.gettargetpack(self.targetlist[0])}"
                self.delta.append([self.targetlist[0], "poisoned", True])
            elif self.note == 'Drunk':
                self.HTML = f"{self.getplayerimg()} tried to {self.eventname} {self.gettargetpack(self.targetlist[0])}"
            else:
                self.processmissing()

        elif self.eventname in ['Poisoned', 'Drunked', 'Philosopher Drunk', 'Snake Charm Poison', 'Goon Drunk',
                                'Innkeeper Drunk']:
            if self.eventname == 'Snake Charm Poison':
                self.eventname = 'Snake Charm Poisoned'
            elif self.eventname == 'Pukka Poison':
                self.eventname = 'Pukka Poisoned'

            if self.note == '':
                self.HTML = f"{self.getplayerimg()} became {self.eventname}"
                self.delta.append([self.player, "poisoned", True])
            elif self.note == 'Drunk':
                self.HTML = f"{self.getplayerimg()} did not became {self.eventname}"
            else:
                self.processmissing()

        elif self.eventname == 'Healthy':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} became Healthy"
                self.delta.append([self.player, "poisoned", False])
            else:
                self.processmissing()

        elif self.eventname == 'Role Change':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} had their role changed to {self.getroleimg(self.targetlist[0])}"
                self.delta.append([self.player, "currentrole", self.targetlist[0]])
            else:
                self.processmissing()

        elif self.eventname == 'Alignment Change':
            if self.targetlist[0] == "":
                CA = self.playerstate['currentalignment']
                self.targetlist[0] = "Evil" if CA == 'Good' else "Good"

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

        elif self.eventname == 'Bureaucrat Ability':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} gives 3 votes to {self.gettargetpack(self.targetlist[0])}"
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
            elif self.note == 'Arbitrary Death':
                self.HTML = f"{self.getplayerimg()} died at random"
                self.processdeath(None, [self.player], 'Arbitrary Death')
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
                self.nomination = [self.player, self.targetlist[0], None]
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
                self.delta.append([self.targetlist[0], "abilityused", True])
            else:
                self.processmissing()

        elif self.eventname == 'Assassin Kill':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} assassinates {self.gettargetpack(self.targetlist[0])}"
                self.processdeath(self.player, [self.targetlist[0]], 'Assassin Kill')
            else:
                self.processmissing()
            self.playerabilityused()

        elif self.eventname == 'Psychopath Kill':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} ends {self.gettargetpack(self.targetlist[0])}"
                self.processdeath(self.player, [self.targetlist[0]], 'Psychopath Kill')
            else:
                self.processmissing()

        elif self.eventname == 'Tinker Kill':
            if self.note == '':
                self.HTML = f"{self.getplayerimg()} spontaneously dies"
                self.processdeath(None, [self.player], 'Tinker Kill')
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

        elif self.eventname in ['Boomdandy Slaughter', 'Boomdandy Vote Kill']:
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
            elif self.note == 'Protected':
                self.HTML = f"{self.getplayerimg()} was Exiled (Protected)"
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
            clockblock = '/static/imgs/clockblock.webp'
            targetplayerpack = self.gettargetpack(self.targetlist[0])

            if self.note != 'No Vote':
                vnum = str(self.note)[1:]
                voteid = f"{self.session}-{self.game}-{vnum}"
                votedetails = [x for x in votes.to_dict("records") if x['voteid'] == voteid][0]
                voterpack = [x for x in playervotes.to_dict("records") if x['voteid'] == voteid]
                livingvotes = len([x for x in voterpack if not x['Dead']])
                deadvotes = len([x for x in voterpack if x['Dead'] and not x['Dead Vote Used']])
                usedeadvotes = len([x for x in voterpack if x['Dead'] and x['Dead Vote Used']])

                votesreceived = votedetails['Total Votes']
                skull = '<svg height="30" aria-hidden="true" focusable="false" data-prefix="fas" data-icon="skull" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" class="svg-inline--fa fa-skull fa-w-16"><path fill="currentColor" d="M256 0C114.6 0 0 100.3 0 224c0 70.1 36.9 132.6 94.5 173.7 9.6 6.9 15.2 18.1 13.5 29.9l-9.4 66.2c-1.4 9.6 6 18.2 15.7 18.2H192v-56c0-4.4 3.6-8 8-8h16c4.4 0 8 3.6 8 8v56h64v-56c0-4.4 3.6-8 8-8h16c4.4 0 8 3.6 8 8v56h77.7c9.7 0 17.1-8.6 15.7-18.2l-9.4-66.2c-1.7-11.7 3.8-23 13.5-29.9C475.1 356.6 512 294.1 512 224 512 100.3 397.4 0 256 0zm-96 320c-35.3 0-64-28.7-64-64s28.7-64 64-64 64 28.7 64 64-28.7 64-64 64zm192 0c-35.3 0-64-28.7-64-64s28.7-64 64-64 64 28.7 64 64-28.7 64-64 64z" class=""></path></svg>'
                deathmarker = skull if votedetails['On the Block'] == 1 else ""

                self.HTML = f"{self.getplayerimg()} <img src = '{clockhand}' height = '30'> {targetplayerpack}<br>" \
                            f"Living Votes Available:<strong>{livingvotes}</strong> " \
                            f"Dead Votes Available:<strong>{deadvotes}</strong> " \
                            f"Dead Votes Used:<strong>{usedeadvotes}</strong> " \
                            f"VotesReceived:<strong>{votesreceived}{deathmarker}</strong><br>"

                button = f'<button type="button" class="btn btn-outline-info btn-sm" onclick="toggletable({vnum})" id="butv{vnum}"><strong>Vote {vnum}</strong></button>'
                self.HTML += button

                pdata = gamestate['playerdata']
                tablepack = [{'name': x['Player'], 'voted': x['Voted'], 'deadvoteused': x['Dead Vote Used'],
                              'dead': not pdata[x['Player']]['alive'],'active': pdata[x['Player']]['active'],
                              "roleimg": pdata[x['Player']]['roleimg'], "role": pdata[x['Player']]['currentrole']} for x
                             in voterpack]

                self.voterpack = tablepack

                ghostvote = '/static/imgs/ghostvote.svg'
                ghostvoteused = '/static/imgs/ghostvoteused.svg'
                handraise = '/static/imgs/handraised.svg'
                handlowered = '/static/imgs/handlowered.svg'

                table = f'<table class="table" id="VoteTable{vnum}" style="display:none; table-layout: fixed ; width: 100%;"><thead><tr>'

                for t in tablepack:
                    atag = f'{t["roleimg"]}'
                    namerole = f"{t['name']}-{t['role']}"
                    table += f'<th scope="col"><img src = "{atag}" height = "40"' \
                             f'data-bs-toggle="tooltip" data-toggle="tooltip" ' \
                             f'data-bs-placement="bottom" title="" data-bs-original-title="{namerole}"></th>'

                table += '</tr></thead><tbody><tr>'

                for r in tablepack:
                    if not r["dead"]:
                        table += f'<td></td>'
                    elif r["dead"] and not r["deadvoteused"]:
                        table += f'<td scope="col"><img src = "{ghostvote}" height = "30"></td>'
                    elif r["dead"] and r["deadvoteused"]:
                        table += f'<td scope="col"><img src = "{ghostvoteused}" height = "30"></td>'
                    else:
                        table += f'<td scope="col">done fucked</td>'

                table += '</tr><tr>'

                for r in tablepack:
                    if r["voted"]:
                        table += f'<td scope="col"><img src = "{handraise}" height = "30"></td>'
                    else:
                        table += f'<td scope="col"><img src = "{handlowered}" height = "30"></td>'

                table += '</tr></tbody></table>'

                self.HTML += "<br>"
                self.HTML += table

                self.nomination = [self.player, self.targetlist[0],
                                   [livingvotes, deadvotes, votesreceived, votedetails['On the Block'] == 1, voterpack]]
            elif self.note == 'No Vote':
                self.HTML = f"{self.getplayerimg()} <img src = '{clockblock}' height = '30'> {targetplayerpack}"
                if self.targetstatedict[self.targetlist[0]]['currentrole'] == "Virgin":
                    self.roleabilityused('Virgin', gamestate)

                self.nomination = [self.player, self.targetlist[0], None]
            else:
                self.processmissing()

        elif self.eventname == 'Boomdandy Vote' or self.eventname == 'Fiddler Vote':
            if self.note != 'No Vote':
                if self.eventname == 'Boomdandy Vote':
                    self.HTML = f"{self.getplayerimg()} triggered a vote.<br>"
                    vnum = "BOOM!"
                else:
                    self.HTML = f"{self.getroleimg('Fiddler')} triggered a vote.<br>"
                    vnum = "Fiddled Vote"

                voteorder = gamestate['playerorder']
                playerdata = gamestate['playerdata']
                votecount = cnt(self.targetlist)
                votesummary = [f"{p}:{votecount[p]}" for p in votecount]
                votesummary = " | ".join(votesummary)
                self.HTML += f"{votesummary}<br>"

                button = f'<button type="button" class="btn btn-outline-info btn-sm" onclick="toggletable(999)" id="butv999"><strong>{vnum}</strong></button>'
                self.HTML += button

                table = f'<div class="row" id="VoteTable999" style="display:none; table-layout: fixed ; width: 100%;">'

                for i in range(len(voteorder)):
                    t = voteorder[i]
                    atag = f'{playerdata[t]["roleimg"]}'
                    namerole = f"{playerdata[t]['name']}-{playerdata[t]['currentrole']}"
                    table += f'<div class="col-2"><img src = "{atag}" height = "40"' \
                             f'data-bs-toggle="tooltip" data-toggle="tooltip" ' \
                             f'data-bs-placement="bottom" title="" data-bs-original-title="{namerole}">' \
                             f'<h5>{self.targetlist[i]}</h5></div>'
                table += '</div>'
                self.HTML += table
            else:
                self.processmissing()

        elif self.eventname == 'Forms a Cult (Miscount)':
            self.HTML = f"{self.getplayerimg()} tries to form a cult, the vote {self.targetlist[0]}."

        elif self.eventname == 'Forms a Cult':
            if self.note != 'No Vote':
                voteorder = gamestate['playerorder']
                playerindex = voteorder.index(self.player) + 1
                voteorder = voteorder[playerindex:] + voteorder[:playerindex]
                playerdata = gamestate['playerdata']
                voteorder = [x for x in voteorder if playerdata[x]["active"]]
                alignmentdata = [playerdata[x]["currentalignment"] for x in playerdata]
                goodcount = len([x for x in alignmentdata if x == "Good"])
                goodvotecount = len(
                    [x for x in range(len(alignmentdata)) if alignmentdata[x] == "Good" and self.targetlist[x] == "T"])
                vnum = "Cult"

                self.HTML = f"{self.getplayerimg()} tries to form a cult (Votes:{goodvotecount}/{goodcount}).<br>"
                button = f'<button type="button" class="btn btn-outline-info btn-sm" onclick="toggletable(999)" id="butv999"><strong>{vnum}</strong></button>'
                self.HTML += button

                table = f'<div class="row" id="VoteTable999" style="display:none; table-layout: fixed ; width: 100%;">'
                handraise = f'<td scope="col"><img src = "/static/imgs/handraised.svg" height = "40">'
                handlowered = f'<td scope="col"><img src = "/static/imgs/handlowered.svg" height = "40">'
                for i in range(len(voteorder)):
                    t = voteorder[i]
                    atag = f'{playerdata[t]["roleimg"]}'
                    namerole = f"{playerdata[t]['name']}-{playerdata[t]['currentrole']}"
                    hand = handraise if self.targetlist[i] == "T" else handlowered

                    table += f'<div class="col-2"><img src = "{atag}" height = "40"' \
                             f'data-bs-toggle="tooltip" data-toggle="tooltip" ' \
                             f'data-bs-placement="bottom" title="" data-bs-original-title="{namerole}">' \
                             f'<h5>{hand}</h5></div>'
                table += '</div>'
                self.HTML += table
            else:
                self.processmissing()

        elif self.eventname == "Holds Lil' Monsta":
            if self.note == '':
                LM = "Lil' Monsta"
                self.HTML = f"{self.getplayerimg()} grabs {self.getroleimg(LM)}"
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
                self.roleabilityused('Judge', gamestate)
            elif self.note == "Scarlet Pass":
                self.HTML = f"<img src = '{execute}' height = '60'> {self.getplayerimg()} was executed ({self.getroleimg('scarletwoman')}triggered)"
            elif self.note == "Mastermind":
                self.HTML = f"<img src = '{execute}' height = '60'> {self.getplayerimg()} was executed ({self.getroleimg('Mastermind')}triggered)"
                self.roleabilityused("Mastermind", gamestate)
            elif self.note == "Mutant":
                self.HTML = f"<img src = '{execute}' height = '60'> {self.getplayerimg()} was executed as the {self.getroleimg('Mutant')}"
            else:
                self.processmissing()

        elif self.eventname == 'Al-Hadikhia Selection':
            targetplayerpack = self.gettargetpack(self.targetlist[0])
            self.HTML = f"{self.getplayerimg()} selects {targetplayerpack} to choose...life or death?"

        elif self.eventname == 'Demon Kill':
            demonattack = '/static/imgs/DemonKill.webp'
            demonattackblock = '/static/imgs/DemonKillBlocked.webp'
            targetplayerpack = self.gettargetpack(self.targetlist[0])
            BLOCKED = False
            if self.note == "Fang Gu Jump":
                self.HTML = f"{self.getplayerimg()} <img src = '{demonattack}' height = '50'> " \
                            f"{targetplayerpack} {self.note}"
                self.processdeath(self.player, [self.player], 'Demon Kill')
                BLOCKED = True
            elif self.note == "Star Pass":
                self.HTML = f"{self.getplayerimg()} <img style='-webkit-transform: scaleX(-1); transform: " \
                            f"scaleX(-1);' src = '{demonattack}' height = '50'> <strong>STAR PASS</strong>"
            elif self.note == "Legion":
                self.HTML = f"{self.getroleimg('Legion', size=50)} <img src = '{demonattack}' height = '50'> " \
                            f"{targetplayerpack}"
            elif self.note == "Scarlet Pass":
                self.HTML = f"{self.getplayerimg()} <img style='-webkit-transform: scaleX(-1); transform: " \
                            f"scaleX(-1);' src = '{demonattack}' height = '50'> " \
                            f"{self.getroleimg('scarletwoman', size=40)} triggered"
            elif self.note == "Lil' Monsta":
                LM = "Lil' Monsta"
                self.HTML = f"{self.getroleimg(LM)} <img src = '{demonattack}' height = '50'> {targetplayerpack}"
            elif self.note != "":
                self.HTML = f"{self.getplayerimg()} <img src = '{demonattackblock}' height = '50'> " \
                            f"{targetplayerpack} {self.note}"
                BLOCKED = True
            else:
                self.HTML = f"{self.getplayerimg()} <img src = '{demonattack}' height = '50'> {targetplayerpack}"

            if not BLOCKED:
                self.processdeath(self.player, [self.targetlist[0]], 'Demon Kill')

        elif self.eventname == 'Al-Hadikhia Decision':
            self.HTML = f"{self.getplayerimg()} chooses to {self.targetlist[0]}"

        elif self.eventname == 'Shabaloth Resurrect':
            p = self.targetlist[0]
            targetplayerpack = self.gettargetpack(p)
            self.HTML = f"{self.getplayerimg()} resurrects {targetplayerpack}"
            self.delta.append([p, "alive", True])

        elif self.eventname == 'Inactive':
            self.HTML = f"{self.getplayerimg()} is inactive"
            self.delta.append([self.player, "active", False])

        elif self.eventname == 'Player Left Game':
            self.HTML = f"{self.getplayerimg()} left the game"
            self.delta.append([self.player, "active", False])

        elif self.eventname == 'Player Joined Game':
            self.HTML = f"{self.getplayerimg()} finally turned up"
            self.delta.append([self.player, "active", True])

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
            elif self.note == 'Storyteller Executed - Atheist':
                winner, method = "Good", "Storyteller Executed - Atheist"
            elif self.note == 'Evil Twin Executed':
                winner, method = "Good", "Evil Twin Executed"

            elif self.note == 'Saint Executed':
                winner, method = "Evil", "The Saint was Executed"
            elif self.note == 'Two Living Players':
                winner, method = "Evil", "Demon in final 2"
            elif self.note == 'No Execution - Vortox':
                winner, method = "Evil", f"No Execution with the {self.getroleimg('Vortox', size=40)}"

            elif self.note == 'Mastermind Execution':
                winner, method = self.targetlist[0], "Mastermind Triggered"
            elif self.note == 'Cult Formed':
                winner, method = self.targetlist[0], f"A {self.targetlist[0]} Cult Was Formed"
            elif self.note == 'Fiddler':
                winner, method = self.targetlist[0], f"The Game was Fiddled"

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
                self.delta.append([None, "win condition", (self.note, winner)])


        else:
            self.processmissing()
