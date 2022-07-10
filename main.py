import CharacterJSONprocess
import initimport
import classes as C

SessionsMain, RolesMain, EventsMain, VotesMain, PlayerVotesMain = initimport.importxlsx()
RoleTypesdf = CharacterJSONprocess.getrolesdf()

RoleTypesdict = RoleTypesdf.to_dict("records")
RoleTypesdict = {x['Role']:x['Side'] for x in RoleTypesdict}

games = {}
for ind, r in SessionsMain.iterrows():

    g = C.Game(r.Date,r.Session,r["Game Number"],r.Script,r.Result,r.PlayerCount)

    es = EventsMain.copy(deep=True)
    es = es.loc[(es["Session"] == g.session) & (es["Game Number"] == g.game)]
    g.eventdf = es

    vs = VotesMain.copy(deep=True)
    vs = vs.loc[(vs["Session"] == g.session) & (vs["Game Number"] == g.game)]
    g.votedf = vs

    pvs = PlayerVotesMain.copy(deep=True)
    pvs = pvs.loc[(pvs["Session"] == g.session) & (pvs["Game Number"] == g.game)]
    g.playervotedf = pvs

    for p in RolesMain.loc[(RolesMain["Session"]==g.session) & (RolesMain["Game Number"]==g.game)].to_dict("records"):
        if p['Role'] == "ST":
            g.storytellers.append(p["Player"])
        elif p['Player'] == "Bluff":
            g.demonbluffs.append(p["Role"])
        elif p['Notes'] in ["Good","Evil"]:
            g.addplayer(p["Player"], p['Role'], p['Notes'], p['Notes'])
        else:
            g.addplayer(p["Player"], p['Role'], RoleTypesdict[p['Role']], p['Notes'])

    g.processgame()

    games[f"{g.session}-{g.game}"]=g

    #print(g.getgamestate())
    #exit()

imgrequired = []
for x in games:
    imgrequired += list(games[x].imagesrequired)

imgrequired = set(imgrequired)

import createimgs
createimgs.basicimages()

from os import listdir
from os.path import isfile, join
mypath2 = r'D:\PyCharm/BOTCwebsite2/app\static/tokenimgs'
made = [f.split(".")[0] for f in listdir(mypath2) if isfile(join(mypath2, f))]
for i in imgrequired:
    if i.split(".")[-2].split("/")[-1] not in made:
        createimgs.imageondemand(i)


import pickle
from awards import awardpackgen
awards = awardpackgen(games)
print(awards)
pickle.dump(games, open(r'games.p',"wb"))


#D:\PyCharm\BOTCwebsite2
targetings = []
exportgames = {}
gamessummary = {}
for g in games:
    gamedict = games[g].gamejson()
    gamessummary[g] = {x:gamedict[x] for x in ['playerorder', 'date', 'session', 'game', 'script', 'result',
                                               'winmethod', 'players', 'storytellers', 'allrolesused']
    }

    del gamedict['playerobjs']
    del gamedict['eventdf']
    del gamedict['playervotedf']
    del gamedict['votedf']
    del gamedict['imagesrequired']

    gamedict['events'] = [x.__dict__ for x in gamedict['events']]

    gamedict['phases'] = {}

    for e in gamedict['events']:
        if e['phase'] not in gamedict['phases']:
            gamedict['phases'][e['phase']] = []
        gamedict['phases'][e['phase']].append(e)

    exportgames[g] = gamedict



datapack = [exportgames,gamessummary,awards]
pickle.dump(datapack, open(r'D:\PyCharm\BOTCwebsite2\datapack.p',"wb"))
print("--END--")
