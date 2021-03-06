from pyevolve import G1DList
from pyevolve import GAllele
from pyevolve import GSimpleGA
from pyevolve import Selectors
from pyevolve import Statistics
from pyevolve import Scaling
from pyevolve import Mutators
from pyevolve import Initializators
from pyevolve import DBAdapters

from trading.backtest import BacktestMarket
from trading.strategy import Strategy
import datetime

class Evolver:
    def __init__(self,filename, gen=10, pop=10):
        self.filename = filename
        self.gen = gen
        self.pop = pop

    def fitness(self, genome):
        market = BacktestMarket()
        ticker = market["SBER"]
        ticker.candle( datetime.timedelta( minutes=1) ).strategy(Strategy, genome[0], genome[1])
        market.load( self.filename )
        print("Type: %s Priod: %s -> %s (%s from %s)" % ( genome[0], genome[1], market.balance, market.trades, market.profit_trades ) )
        return market.balance

    def run(self):
        # Allele define valid chromosome value
        alleles = GAllele.GAlleles()

        # Define gene with 2 chromosomes
        # MA type
        alleles.add(GAllele.GAlleleList([0,1,2,3,4]))
        # MA range
        alleles.add(GAllele.GAlleleRange(1, 99))
      
        # Genome instance, 1D List
        genome = G1DList.G1DList(len(alleles))
        # Sets the range max and min of the 1D List
        genome.setParams(allele=alleles)
        # The evaluator function (evaluation function)
        genome.evaluator.set(self.fitness)
        # This mutator and initializator will take care of
        # initializing valid individuals based on the allele set
        # that we have defined before
        genome.mutator.set(Mutators.G1DListMutatorAllele)
        genome.initializator.set(Initializators.G1DListInitializatorAllele)

        # Genetic Algorithm Instance
        ga = GSimpleGA.GSimpleGA(genome)
        # Set the Roulette Wheel selector method, the number of generations and
        # the termination criteria
        ga.selector.set(Selectors.GRouletteWheel)
        ga.setGenerations(self.gen)
        ga.setPopulationSize(self.pop)
        ga.terminationCriteria.set(GSimpleGA.ConvergenceCriteria)

        pop = ga.getPopulation()
        pop.scaleMethod.set(Scaling.SigmaTruncScaling)

        ga.evolve(freq_stats=10)
        # Best individual
        self.best = ga.bestIndividual()

