
class BacktestConfig:

    def __init__(self):
        self.strat_id = ""
        self.strat_name = ""
        self.strat_version = ""
        self.pair = ""
        self.exchange = ""
        self.leverage = ""
        self.period = ""
        self.start = ""
        self.end = ""
        self.recommended = ""

    def setStratId(self, strat_id):
        self.strat_id = strat_id

    def setStratName(self, strat_name):
        self.strat_name = strat_name

    def setStratVersion(self, strat_version):
        self.strat_version = strat_version
    
    def setPair(self, pair):
        self.pair = pair

    def setExchange(self, exchange):
        self.exchange = exchange

    def setLeverage(self, leverage):
        self.leverage = leverage

    def setPeriod(self, period):
        self.period = period

    def setStart(self, start):
        self.start = start

    def setEnd(self, end):
        self.end = end

    def setRecommended(self, recommended):
        if recommended:
            self.recommended = 1
        else:
            self.recommended = 0
    
    def getStratId(self):
        return self.strat_id

    def getStratName(self):
        return self.strat_name

    def getStratVersion(self):
        return self.strat_version

    def getPair(self):
        return self.pair

    def getExchange(self):
        return self.exchange

    def getLeverage(self):
        return self.leverage

    def getPeriod(self):
        return self.period

    def getStart(self):
        return self.start

    def getEnd(self):
        return self.end
    
    def getRecommended(self):
        return self.recommended

    def getId(self):
        return str(self.getStratId())+str(self.getStratVersion())+str(self.getExchange())+str(self.getPair()).replace(" / ", "-")+str(self.getPeriod())

    def toString(self):
        return "strat_id = " + str(self.getStratId()) + "," +  "strat_name = " + str(self.getStratName()) + "," +  "strat_version = " + str(self.getStratVersion()) + "," +  "pair = " + str(self.getPair()) + "," +  "exchange = " + str(self.getExchange()) + "," +  "period = " + str(self.getPeriod()) + "," +  "start = " + str(self.getStart()) + "," +  "end = " + str(self.getEnd()) + "," +  "recommended = " + str(self.getRecommended())