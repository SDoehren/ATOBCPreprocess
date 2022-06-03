import CharacterJSONprocess
import initimport
import classes as C


SessionsMain, RolesMain, EventsMain, VotesMain, PlayerVotesMain = initimport.importxlsx()
RoleTypesdf = CharacterJSONprocess.getrolesdf()

RoleTypesdict = RoleTypesdf.to_dict("records")
RoleTypesdict = {x['Role']:x['Side'] for x in RoleTypesdict}

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

    #print(g.getgamestate())
    #exit()