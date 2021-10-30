import pandas as pd
from MonthlyGrossMarginProduct import MonthlyGrossMarginProduct

data = pd.read_excel("./dataset.xlsx")
may = data.loc[data.order_date.dt.month == 5]
june = data.loc[data.order_date.dt.month == 6]
products = ["A", "B", "C", "D"]
rate = {
    "tom_jerry": ["Fixed", 8000],       #0th index is the type of rate, 1st index is the total rate
    "roadrunner": ["Per_order", 50],    #0th index is the type, first index is the per order rate
    "micky_mouse": ["Fixed_to_limit", 500, 10000, 10],      #1st index is the limit, 2nd is the rate till the limit, 3rd is the additional rate
    "donald_duck": ["Per_order", 50] 
}

m = MonthlyGrossMarginProduct(may, provider_name_rate = rate, products = products)
j = MonthlyGrossMarginProduct(june, provider_name_rate = rate, products = products)

g = m.calculate()
k = j.calculate()
print(g)
print(k)
