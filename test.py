from gpiozero import LEDBarGraph
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
from bitfinex import WssClient


factory = PiGPIOFactory(host='192.168.1.16')


class CoinObserver:
	"""
	Simple LED ticker based on bitfinex websockets. Uses 6 LEDS.
	"""
	def __init__(self, pair, graph):
		"""
		pair - pair name ex. 'BTCUSD'
		graph - gpiozero.LEDBarGraph used as ticker change indicator
		"""
		assert isinstance(graph, LEDBarGraph), 'Grap must be instance of gpiozero.LEDBarGraph'
		self.pair = pair
		self.graph = graph
		self.last_price = 0
		self.last_points = []
		self.verbose = True


		# Check if graph works and set number of LEDs
		self.graph.on()
		self.graph_size = graph.lit_count
		sleep(1)
		self.graph.value = 0


	def _update_last_points(self, value):
		if len(self.last_points) > 2:
			self.last_points = self.last_points[1:] + [value]
		else:
			self.last_points.append(value)

	def _beep(self):
		v = graph.value
		graph.value = 0 
		sleep(0.1)
		graph.value = v

	def _update_graph(self, value):
		if value >= self.last_price:
			l = 3 - len([x for x in self.last_points if x >= value])
			graph.value = l / self.graph_size
		else:
			l = 3 - len([x for x in self.last_points if x < value])
			graph.value = -l / self.graph_size

		self.last_price = value
		self._update_last_points(value)

	def _handler(self, message):
	  # Signal new message
	  self._beep()

	  if isinstance(message, dict) and self.verbose:
	  	print(message.get('event', 'error'))

	  if isinstance(message, list):
	  	code, info = message
	  	if isinstance(info, list):
	  		last_price = info[6]
	  		self._update_graph(last_price)
	  		if self.verbose:
	  			print(f'Last price: {last_price}, last points: {self.last_points}')

	def start(self, verbose = True):
		"""
		verbose - if set to True then channel information is printed out
		"""
		self.verbose = verbose
		client = WssClient()
		client.subscribe_to_ticker(
		    symbol=self.pair,
		    callback=self._handler
		)
		client.start()


graph = LEDBarGraph(25, 24, 23, 21, 16, 12, pin_factory=factory)
obsrv = CoinObserver('BTCUSD', graph)

obsrv.start()

