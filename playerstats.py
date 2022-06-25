


class PlayerDetails:
    def __init__(self,name):
        self.name = name
        self.gamepack = []

    def __repr__(self):
        return f"<playerstats.PlayerDetails object - {self.name}>"

    def addgame(self,game):
        print(game.playerobjs[self.name])
        print(game.gamesummary())
        exit()

class PlayerFactory:
    def __init__(self,games):
        self.players = {}


        self.processgames(games)
        print(self.players)

    def processgames(self,games):
        for gid in games:
            game = games[gid]
            for p in game.playerobjs:
                if p not in self.players:
                    self.players[p] = PlayerDetails(p)
                self.players[p].addgame(game)


if __name__ == '__main__':
    import pickle
    datapack = pickle.load(open(r'D:\PyCharm\BOTCwebsite2\datapack.p', "rb"))
    playerpack = PlayerFactory(datapack[0])
