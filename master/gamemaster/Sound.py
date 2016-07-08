import os
import time
import pygame



sound_folder = "sounds/"

class SoundManager(object):
	MUSIC_CHANNEL = 0
	instance = None

	def __init__(self, soundfiles):
		if SoundManager.instance is not None:
			raise Exception("Sound manager is a singleton instance. an instance is already defined!")
		SoundManager.instance = self
		pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=64)
		pygame.mixer.set_num_channels(2)
		pygame.mixer.set_reserved(1) # number of dedicated channels (e.g. music)
		self.musicChannel = pygame.mixer.Channel(SoundManager.MUSIC_CHANNEL)
		
		self.files = {k: pygame.mixer.Sound(sound_folder+filename) for k, filename in soundfiles.iteritems()}
	
	def __getitem__(self, key):
		return self.files[key]

	@staticmethod
	def StopAll():
		pygame.mixer.stop()

