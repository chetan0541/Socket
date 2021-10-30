

class MonthlyGrossMarginProduct():
    '''
    Calculates the Monthly Gross Margin per Product. 
    '''
    def __init__(self, dataset, provider_name_rate = {}, products = []) -> None:
        self.main_dataset = dataset
        self.provider_name_rate = provider_name_rate
        self.fixed_rate_providers = {}
        self.changing_rate_providers = {}
        self.products = products
        self.provider = "provider"
        self.order_count = "order_count"
        self.order_date = "order_date"
        self.cumsum = "cumsum"
        self.fixed = "Fixed"
        self.per_order = "Per_order"
        self.fixed_to_limit = "Fixed_to_limit"
        self.cost_of_product = "cost_of_product"
        self.product = "product"
        self.revenue = "revenue"
        self.monthly_margin_per_product = {}



    def _slice_data(self, data, provider_name = ""):
        '''
        Slices data based on provider name and returns 
        the sliced dataset
        '''
        return data[(data.provider == provider_name)]


    def _get_difference_cumsumval(self, dataset, limit = [], provider_name = []):
        '''
        First calculates the cumilative sum for the provider which has a changing rate. 
        Then divides the set into two halves; Lesser than limit and greater than limit. 
        Then calculates the difference of the last value of the lesser and the first value
        of the greater. Appends the difference as well as the first cumilative sum value of 
        the greater to the respective dictionaries and returns the dataset with the cumilative sum
        calculation.
        Supports multiple providers
        '''
        for idx, name in enumerate(provider_name):
            dataset[self.cumsum] = dataset.where(dataset[self.provider] == name)[self.order_count].cumsum()
            lesser = dataset.where((dataset[self.cumsum] <= limit[idx]) & (dataset[self.provider] == name)).dropna()
            greater = dataset.where((dataset[self.cumsum] > limit[idx]) & (dataset[self.provider] == name)).dropna()
            last_cumsumval_lesser = lesser[-1:][self.cumsum].iloc[-1]
            cumsumval = greater[0:1][self.cumsum].iloc[-1]
            difference = int(limit - last_cumsumval_lesser)
            self.changing_rate_providers[name].append(difference)
            self.changing_rate_providers[name].append(cumsumval)
            return dataset

    def _get_rate_per_prod(self, provider_name_rate):
        '''
        Calculates the rate of providers. 
        Fixed rate is when the rate is fixed for a month.
        Per order rate is when the rate is set per order.
        Fixed to limit is when the rate is fixed to a limit but changes after the limit.
        Adds the results to a dictionary
        '''
        for name, rate in provider_name_rate.items():
            if rate[0] == self.fixed:
                data_provider = self._slice_data(self.main_dataset, provider_name = name)
                order_count_sum = data_provider.order_count.sum()
                rate_per_product = rate[1] / order_count_sum
                self.fixed_rate_providers.update({name:rate_per_product})
            elif rate[0] == self.per_order:
                self.fixed_rate_providers.update({name:rate[1]})
            elif rate[0] == self.fixed_to_limit:
                limit = rate[1]
                fixed_rate = rate[2] / limit
                additional_rate = rate[3]
                self.changing_rate_providers.update({name: [limit, fixed_rate, additional_rate]})
            
    def _calculate_cost_of_prod(self):
        '''
        Calculates the cost of product based on the rates.
        Returns dataset with the column "cost of product" and the respective values
        '''
        self._get_rate_per_prod(provider_name_rate = self.provider_name_rate)
        names_of_provider = [name for name in self.changing_rate_providers]
        limits = [self.changing_rate_providers.get(name)[0] for name in names_of_provider]
        cumsum_dataset = self._get_difference_cumsumval(dataset = self.main_dataset, limit = limits, provider_name = names_of_provider)
        cumsum_dataset[self.cost_of_product] = cumsum_dataset.apply(lambda x: x[self.order_count] * self.fixed_rate_providers.get(x[self.provider]) if x[self.provider] in self.fixed_rate_providers \
            else x[self.order_count] * 20 if (x[self.cumsum] <= self.changing_rate_providers.get(x[self.provider])[0]) else (self.changing_rate_providers.get(x[self.provider])[3] * 20 + \
                (x[self.order_count] - self.changing_rate_providers.get(x[self.provider])[3]) * 10) if (x[self.cumsum] == self.changing_rate_providers.get(x[self.provider])[4]) else \
                    x[self.order_count] * 10, axis = 1)
        dataset_with_cop = cumsum_dataset.drop([self.cumsum], axis = 1)
        return dataset_with_cop

    def _get_sum(self, dataset, column):
        '''
        Gets sum of column
        '''
        return dataset[column].sum()

    def _calculate_margin(self, revenue, expense):
        '''
        Returns cost margin
        '''
        return ((revenue - expense) / revenue) * 100

    def calculate(self):
        '''
        Calculates the cost margin for each product and returns the result 
        as a dictionary {product}
        '''
        dataset_with_cop = self._calculate_cost_of_prod()
        for product in self.products:
            single_prod = dataset_with_cop.where(dataset_with_cop[self.product] == product).dropna()
            revenue = self._get_sum(single_prod, self.revenue)
            expense = self._get_sum(single_prod, self.cost_of_product)
            margin = self._calculate_margin(revenue, expense)
            self.monthly_margin_per_product.update({product : margin})
        return self.monthly_margin_per_product

    