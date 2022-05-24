from pibic import Flow

flow = Flow(['37220000', '37230000', '37260000'])
df1 = flow.track_back()
df2 = flow.data()

class Hydro_Sig():

    def __init__(self, station):
        self.station = station
    
    def skew(self):
        mean = df2[self.station].mean()
        median = df2[self.station].median()
        return mean / median

    def qsp(self):
        media = df2[self.station].mean()
        drainage_area = df1[df1['Code'] == self.station]['DrainageArea']
        return media / drainage_area

    def cvq(self):
        cv = df2[self.station].std() / df2[self.station].mean()
        return cv

    def bfi(self):
        return df2[self.station].rolling(7).mean().min() / df2[self.station].mean()

    def q5(self):
        drainage_area = df1[df1['Code'] == self.station]['DrainageArea']
        ef = df2[self.station] / drainage_area.values[0]
        return ef.quantile(q=0.95)

    def hfd(self):
        return df2[self.station].quantile(q=0.9) / df2[self.station].mean()

    def q95(self):
        drainage_area = df1[df1['Code'] == self.station]['DrainageArea']
        ef = df2[self.station] / drainage_area.values[0]
        return ef.quantile(q=0.05)

    def lowfr(self):
        lim = df2[self.station].mean() * 0.05
        res = len(df2[self.station][df2[self.station] < lim]) / len(df2[self.station].dropna())
        return res

    def highfrvar(self):
        q75 = df2[self.station].quantile(q=.25)
        res = df2[self.station][df2[self.station] > q75].std() / df2[self.station][df2[self.station] > q75].mean()
