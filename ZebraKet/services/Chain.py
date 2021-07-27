from utils.data import read_inventory_optimization_data


class Chain(list):
    def __init__(self) -> None:
        super().__init__()
    
    def process_single_qubo(self, index, sampler, **kwargs):
        qubo = self[index]
        qubo.solve(sampler, **kwargs)
    
    def process_best(self, samplers: list, sampler_params: list):
        """Processes the chain but only passes the best solutions forward

        Args: 
        samplers - list of samplers to use, must be same length as self
        sampler_params - list of paramaters to use for the samplers must be same length as self
        """

        previous_qubo = None
        for qubo, sampler, sampler_params in zip(self, samplers, sampler_params):
            if previous_qubo is None: 
                # first qubo to process
                qubo.solve(sampler, **sampler_params)
                previous_qubo = qubo
                continue
            next_iteration_data = previous_qubo.post_process[0]
            print('Starting next iteration with data', next_iteration_data)
            qubo.build(**next_iteration_data)
            qubo.solve(sampler, **sampler_params)
            previous_qubo = qubo
            print('found solution: \n', qubo.response)
        

if __name__ == "__main__":

    from models.ProfitQubo import ProfitQubo
    from models.SupplierQubo import SupplierQubo
    from utils.data import read_profit_optimization_data
    from config import standard_mock_data
    from neal import SimulatedAnnealingSampler
    from dwave.system import LeapHybridDQMSampler

    budget = 1000
    max_number_of_products = 30

    data_file = standard_mock_data['small']

    inventory_requirement, supplier_inventory = read_inventory_optimization_data(data_file)

    # def return_

    qubo0 = SupplierQubo(inventory_requirement, supplier_inventory)
    def get_post_process_inventory_function(data_file:str): 

        def post_process_inventory_qubo(solution, energy):
            from utils.data import read_profit_optimization_data

            profit, cost = read_profit_optimization_data(data_file, solution)

            return dict(
                profits=profit,
                costs=cost
            )
        
        return post_process_inventory_qubo

    qubo0.define_post_process_function(get_post_process_inventory_function(data_file))
    sampler0 = SimulatedAnnealingSampler().sample
    sampler0_params = dict()

    qubo1 = ProfitQubo()
    sampler1 = LeapHybridDQMSampler().sample_dqm
    sampler1_params = dict()

    # profit, cost = read_profit_optimization_data(standard_mock_data['small'])
    # sampler1 = LeapHybridDQMSampler().sample_dqm
    # sampler2 = LeapHybridDQMSampler().sample_dqm
    

    # # supplier_qubo = SupplierQubo()

    # # price_qubo = ProfitQubo(sampler1, profit, cost)
    # # qubo0.define_post_process_function(lambda solution, energy: dict(profits=profit, costs=cost))
    # # # qubo0.solve()
    # # # print(qubo0.post_process)
    # # qub
    
    # # qubo1 = ProfitQubo(sampler2)

    # qubo0 = ProfitQubo(profit, cost)
    # qubo0.define_post_process_function(lambda solution, energy: dict(profits=profit, costs=cost))

    # qubo1 = ProfitQubo()

    chain = Chain()
    chain.append(qubo0)
    chain.append(qubo1)

    samplers = [sampler0, sampler1]
    sampler_params = [sampler0_params, sampler1_params]

    chain.process_best(samplers, sampler_params)
    