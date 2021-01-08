import numpy as np

# To suppress scientific notation for our probabilities
np.set_printoptions(suppress=True)

# enums
ROCK = 0
PAPER = 1
SCISSORS = 2

NUM_ACTIONS = 3

class RPSTrainer:

    '''
    Use regret matching to learn how to play rock, paper, scissors
    against a fixed opponent.
    '''
    
    def __init__(self):
        self.regret_sum = np.zeros(NUM_ACTIONS)
        self.strategy = np.zeros(NUM_ACTIONS)
        self.strategy_sum = np.zeros(NUM_ACTIONS) 

        self.opp_strategy = np.asarray([0.6, 0.3, 0.1])

    def get_strategy(self):
        nonnegative = np.where(self.regret_sum > 0.0)
        print("Nonnegative: ", nonnegative)
        self.strategy[nonnegative] = self.regret_sum[nonnegative] 
        print("Strategy at place nonnegative: ", self.strategy[nonnegative])
        normalizing_sum = np.sum(self.strategy)
        print("Normalizing_sum: ", normalizing_sum)
        if normalizing_sum > 0.0:
            self.strategy /= normalizing_sum
        else:
            self.strategy = np.full(NUM_ACTIONS, 1.0 / NUM_ACTIONS)
        print("Self_strategy 2: ", self.strategy)
        self.strategy_sum += self.strategy
        print("Strategy_sum: ", self.strategy_sum)
        
        return self.strategy

    def get_action(self, strategy):
        return np.random.choice(np.arange(NUM_ACTIONS), 1, p = strategy) #1st param: list [0,1,2]; 2nd param: how many; 3rd param: probabilities

    def train(self, iterations):
        '''
        When our action wins, the strategy remains unchanged.
        When we lose or play even, we get a positive regret sum values that are used to  modify our strategy weights.
        With every round, the strategy is summed to the strategy_sum so that in the end we get an average strategy for all the plays.
        '''
        action_utility = np.zeros(NUM_ACTIONS)
        for i in range(iterations):
            strategy = self.get_strategy()
            my_action = self.get_action(strategy)
            other_action = self.get_action(self.opp_strategy)
            print("My action: ", my_action)
            print("Other action: ", other_action)
            action_utility[other_action] = 0.0 # Lets put zero to the value opponents value
            print("Action utility1: ", action_utility)
            action_utility[0 if other_action == NUM_ACTIONS - 1 else other_action + 1] = 1 #Lets put 1 to the value that would win opponent's action
            print("Action utility2: ", action_utility)
            action_utility[NUM_ACTIONS - 1 if other_action == 0 else other_action - 1] = -1 #Lets put -1 to the value that would lose to opponent's action
            print("Action utility3: ", action_utility)
            print(action_utility[my_action])
            self.regret_sum = action_utility - action_utility[my_action]
            print("Regret_sum: ", self.regret_sum)
            print("-----------")
            #if(i%50==0):
                #print(i,": ",strategy)
            
    def get_average_strategy(self):
        '''
        Calculate average strategy
        '''
        avg_strategy = np.zeros(NUM_ACTIONS)
        normalizing_sum = np.sum(self.strategy_sum)
        print("normalizing_sum: ", normalizing_sum)
        print("self.strategy_sum: ", self.strategy_sum)
        
        if normalizing_sum > 0.0:
            avg_strategy = self.strategy_sum / normalizing_sum
        else:
            avg_strategy = np.full(NUM_ACTIONS, 1.0 / NUM_ACTIONS)
            
        return avg_strategy


if __name__ == '__main__':
    trainer = RPSTrainer()
    trainer.train(1000)
    print("Average strategy: ",trainer.get_average_strategy())