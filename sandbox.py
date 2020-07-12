from Pythagoras import *

a_dataframe = pd.DataFrame(
    data = {
        'COL_1': [-1, -2, -3]
        ,'COL_2': [4.4, 5.5, None]
        ,'COL_3': [7.7, 8.8, 9.9]
        ,'COL_4': [0, 0, 0]
    })

nf = NumericImputer()

r=nf.fit_transform(a_dataframe)

print()