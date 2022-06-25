import CharacterJSONprocess
import initimport
import classes as C
import awards
import playerstats

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

    games[(g.session,g.game)]=g

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
    print(i)
    createimgs.imageondemand(i)

playerpack = playerstats.PlayerFactory(games)
awardspack = awards.getallawards(games)

import pickle
#D:\PyCharm\BOTCwebsite2
datapack = [games]
pickle.dump(datapack, open(r'D:\PyCharm\BOTCwebsite2\datapack.p',"wb"))