import pygame as p
import random as r

p.init()

screen_width = 256
screen_height = 240
window = p.display.set_mode((screen_width, screen_height))
fullscreen = False
p.display.set_caption('The Game is On')
font = p.font.Font('fonts/pixelemulator.ttf', 10)
clock = p.time.Clock()
running = True
score = 0
paused = False
pause_counter_init = 50
pause_counter = pause_counter_init
reset_counter_init = 30
reset_counter = reset_counter_init
level = 1
final_level = 8
bgm_change = False
background = []
for i in range(0, 3, 1):
	background.append(p.image.load('bg/bg{}.png'.format(i)))
win_countdown_init = 425
win_countdown = win_countdown_init
win = False
enemy_spawn_timer_init = 100
enemy_spawn_timer = enemy_spawn_timer_init
spawn_sfx = p.mixer.Sound('sfx/spawn.wav')
pause_sfx = p.mixer.Sound('sfx/pause.wav')

class Object:
	def __init__(self, x, y, width, height):
		self.x_init = x
		self.y_init = y
		self.x = self.x_init
		self.y = self.y_init
		self.width = width
		self.height = height
		self.speed = 0
		self.hitbox = (self.x, self.y, self.width, self.height)

class Player(Object):
	standing_sprite = [p.image.load('player/sr.png').convert(), p.image.load('player/sl.png').convert()]
	for sprite in standing_sprite:
		sprite.set_colorkey((255, 255, 255))

	walking_right = []
	walking_left = []

	for i in range(0, 4, 1):
		walking_right.append(p.image.load('player/wr{}.png'.format(i)).convert())
		walking_right[i].set_colorkey((255, 255, 255))
		walking_left.append(p.image.load('player/wl{}.png'.format(i)).convert())
		walking_left[i].set_colorkey((255, 255, 255))

	jumping_sprite = [p.image.load('player/jr.png').convert(), p.image.load('player/jl.png').convert()]
	for sprite in jumping_sprite:
		sprite.set_colorkey((255, 255, 255))

	shooting_sprite = [p.image.load('player/shr.png').convert(), p.image.load('player/shl.png').convert()]
	for sprite in shooting_sprite:
		sprite.set_colorkey((255, 255, 255))

	death = p.image.load('player/d.png').convert()
	death.set_colorkey((255, 255, 255))

	jump_sfx = p.mixer.Sound('sfx/jump.wav')
	fireball_sfx = p.mixer.Sound('sfx/fireball.wav')
	hit_sfx = p.mixer.Sound('sfx/player_hit.wav')

	def __init__(self, x, y, width, height):
		super().__init__(x, y, width, height)
		self.speed = 2
		self.standing = True
		self.walking = False
		self.steps = 0 # step ticks
		self.step_delay = 5
		self.jump_init = 18
		self.jump_count = self.jump_init
		self.jumping = False
		self.facing_right = True
		self.shooting = False
		self.fireball_max = 2
		self.fireball_cooldown_init = 12
		self.fireball_cooldown = self.fireball_cooldown_init
		self.alive = True
		self.death_bounce_init = 15
		self.death_bounce = self.death_bounce_init
		self.death_pause_init = 50
		self.death_pause = self.death_pause_init
		self.respawn_delay_init = 150
		self.respawn_delay = self.respawn_delay_init

	def draw(self, window):
		if self.alive:
			if not self.shooting:
				if self.standing:
					self.steps = 0

					if self.facing_right:
						window.blit(self.standing_sprite[0], (self.x, self.y))
					else:
						window.blit(self.standing_sprite[1], (self.x, self.y))
				if self.walking:
					self.steps %= len(self.walking_right) * self.step_delay # or self.walking_left

					if self.facing_right:
						window.blit(self.walking_right[self.steps // self.step_delay], (self.x, self.y))
					else:
						window.blit(self.walking_left[self.steps // self.step_delay], (self.x, self.y))

					self.steps += 1
				if self.jumping:
					if self.facing_right:
						window.blit(self.jumping_sprite[0], (self.x, self.y))
					else:
						window.blit(self.jumping_sprite[1], (self.x, self.y))
			else:
				if self.facing_right:
					window.blit(self.shooting_sprite[0], (self.x, self.y))
				else:
					window.blit(self.shooting_sprite[1], (self.x, self.y))
		else:
			window.blit(self.death, (self.x, self.y))

			if self.death_pause > 0:
				self.death_pause -= 1

	def move(self):
		global keys
		self.hitbox = (self.x, self.y, self.width, self.height)

		if self.alive:
			if keys[p.K_LEFT] and self.x > 0:
				self.x -= self.speed
				self.facing_right = False
				self.walking = True
				self.standing = False
			elif keys[p.K_RIGHT] and self.x < (screen_width - self.width):
				self.x += self.speed
				self.facing_right = True
				self.walking = True
				self.standing = False
			else:
				self.standing = True
				self.walking = False

			if not self.jumping:
				if keys[p.K_UP]:
					self.jump_sfx.play()
					self.jumping = True
					self.standing = False
					self.walking = False
			else:
				if self.jump_count > -(self.jump_init + 1):
					# alternative way to jump: self.y -= int(self.jump_count * 0.33)
					if self.jump_count > 0:
						self.y -= (self.jump_count ** 2) // (self.jump_init * 2)
					else:
						self.y += (self.jump_count ** 2) // (self.jump_init * 2)
					self.jump_count -= 1
					self.standing = False
					self.walking = False
				else:
					self.jump_count = self.jump_init
					self.jumping = False

			if keys[p.K_SPACE]:
				if(self.fireball_cooldown == self.fireball_cooldown_init):
					self.fireball_cooldown -= 1

					if len(fireballs) != self.fireball_max:
						self.fireball_sfx.play()
						self.shooting = True
						fireballs.append(Projectile(self.x, self.y, 8, 8, self.facing_right))

			if (self.fireball_cooldown != self.fireball_cooldown_init) and (self.fireball_cooldown > 0):
				self.fireball_cooldown -= 1
			else:
				self.fireball_cooldown = self.fireball_cooldown_init
				self.shooting = False
		else:
			if self.death_pause == 0:
				if (self.death_bounce > -((self.death_bounce_init + 1) * 3)) or (self.respawn_delay > 0):
					self.y -= int(self.death_bounce * 0.33)
					self.death_bounce -= 1
					self.respawn_delay -= 1
				else:
					reset_game()

class Projectile(Object):
	fireball_sprites = []

	for i in range(0, 4, 1):
		fireball_sprites.append(p.image.load('fireball/f{}.png'.format(i)).convert())
		fireball_sprites[i].set_colorkey((255, 255, 255))

	def __init__(self, x, y, width, height, facing_right):
		super().__init__(x, y, width, height)
		self.speed = 3
		self.facing_right = facing_right
		self.rotation_count = 0
		self.rotation_delay = 4
		self.has_bounced = False
		self.max_bounce_height = self.height * 5

	def draw(self, window):
		self.rotation_count %= len(self.fireball_sprites) * self.rotation_delay
		window.blit(self.fireball_sprites[self.rotation_count // self.rotation_delay], (self.x, self.y))
		self.rotation_count += 1

	def move(self):
		self.hitbox = (self.x, self.y, self.width, self.height)

		if self.facing_right:
			self.x += self.speed
		else:
			self.x -= self.speed

		if self.has_bounced:
			self.y -= self.speed
		else:
			self.y += self.speed

		if ((self.y + self.height) > screen_height - 24):
			self.has_bounced = True
		if (((screen_height - 24) - self.y) > self.max_bounce_height):
			self.has_bounced = False

		if ((self.x > screen_width) or (self.x < 0)) or not player1.alive:
			try:
				fireballs.pop(fireballs.index(self))
			except:
				pass

class Enemy(Object):
	walking_right = [p.image.load('spiny/wr0.png').convert(), p.image.load('spiny/wr1.png').convert()]
	walking_left = [p.image.load('spiny/wl0.png').convert(), p.image.load('spiny/wl1.png').convert()]

	for sprite in walking_right:
		sprite.set_colorkey((255, 255, 255))

	for sprite in walking_left:
		sprite.set_colorkey((255, 255, 255))

	hit_sfx = p.mixer.Sound('sfx/hit.wav')
	next_sfx = p.mixer.Sound('sfx/next.wav')
	clear_sfx = p.mixer.Sound('sfx/game_clear.wav')

	def __init__(self, x, y, width, height):
		super().__init__(x, y, width, height)
		self.speed = 1
		self.path = (0, screen_width)
		self.facing_left = r.choice([True, False])
		self.steps = 0
		self.steps_delay = 6
		self.maximum_health = 10
		self.current_health = self.maximum_health
		self.alive = True
		self.death_bounce_init = 10
		self.death_bounce = self.death_bounce_init

	def draw(self, window):
		if self.alive:
			self.steps %= len(self.walking_right) * self.steps_delay

			if self.facing_left:
				window.blit(self.walking_left[self.steps // self.steps_delay], (self.x, self.y))
			else:
				window.blit(self.walking_right[self.steps // self.steps_delay], (self.x, self.y))

			if player1.alive:
				self.steps += 1
				p.draw.rect(window, (255, 255, 255), (self.x - 1, (self.y - int(self.height // 2)) - 1, self.width + 2, 5))
				p.draw.rect(window, (156, 37, 32), (self.x, self.y - int(self.height // 2), self.width, 3))
				p.draw.rect(window, (0, 173, 0), (self.x, self.y - int(self.height // 2), int(self.width * (self.current_health / self.maximum_health)), 3))
		else:
			if self.facing_left:
				dead = p.transform.flip(self.walking_left[0], False, True)
			else:
				dead = p.transform.flip(self.walking_right[0], False, True)

			window.blit(dead, (self.x, self.y))

	def move(self):
		self.hitbox = (self.x, self.y, self.width, self.height)

		if self.alive:
			if player1.alive:
				if self.facing_left:
					if self.x < self.path[0]:
						self.facing_left = False
					else:
						self.x -= self.speed
				else:
					if (self.x + self.width) > self.path[1]:
						self.facing_left = True
					else:
						self.x += self.speed
		else:
			if self.death_bounce > -((self.death_bounce_init + 1) * 3):
				self.y -= int(self.death_bounce * 0.33)
				self.death_bounce -= 1
			else:
				if len(enemies) == 1:
					if level != final_level:
						self.next_sfx.play()
					else:
						self.clear_sfx.play()

				enemies.pop(enemies.index(self))

	def hit(self):
		if self.current_health > 0:
			self.current_health -= 1
		if self.current_health == 0:
			self.alive = False

def draw_game():
	if not win:
		if level == final_level:
			window.blit(background[2], (0, 0))
		else:
			if level % 2 == 0:
				window.blit(background[1], (0, 0))
			else:
				window.blit(background[0], (0, 0))

		player1.draw(window)

		for fireball in fireballs:
			fireball.draw(window)

		for enemy in enemies:
			enemy.draw(window)

		score_text = font.render('score {}'.format(score), 0, (255, 255, 255))
		window.blit(score_text, (int(screen_width * 0.9) - score_text.get_width(), 10))

		level_text = font.render('level {}'.format(level), 0, (255, 255, 255))
		window.blit(level_text, (int(screen_width * 0.1), 10))
	else:
		win_messages = ['congratulations!', 'you exterminated all the spinies!', 'press r to play again', 'press esc to quit']
		window.fill((0, 0, 0))

		for i in range(0, len(win_messages), 1):
			win_text = font.render(win_messages[i], 0, (255, 255, 255))
			window.blit(win_text, ((screen_width // 2) - (win_text.get_width() // 2), int(screen_height * 0.33) + (i * (2 * win_text.get_height()))))

	p.display.update()

def movement():
	player1.move()

	for fireball in fireballs:
		fireball.move()

	for enemy in enemies:
		enemy.move()

def check_collision():
	global score

	for fireball in fireballs:
		for enemy in enemies:
			if enemy.alive:
				if (((fireball.hitbox[0]) <= (enemy.hitbox[0] + enemy.hitbox[2])) and ((fireball.hitbox[0] + fireball.hitbox[2]) >= (enemy.hitbox[0]))):
					if ((fireball.hitbox[1] <= (enemy.hitbox[1] + enemy.hitbox[3])) and ((fireball.hitbox[1] + fireball.hitbox[3]) >= (enemy.hitbox[1]))):
						enemy.hit_sfx.play()
						enemy.hit()
						score += 1

						try:
							fireballs.pop(fireballs.index(fireball))
						except:
							pass

	for enemy in enemies:
		if player1.alive and enemy.alive:
			if (((player1.hitbox[0]) <= (enemy.hitbox[0] + enemy.hitbox[2])) and ((player1.hitbox[0] + player1.hitbox[2]) >= (enemy.hitbox[0]))):
				if ((player1.hitbox[1] <= (enemy.hitbox[1] + enemy.hitbox[3])) and ((player1.hitbox[1] + player1.hitbox[3]) >= (enemy.hitbox[1]))):
					player1.hit_sfx.play()
					p.mixer.music.pause()
					player1.alive = False

def reset_game():
	global score
	global level
	global win_countdown
	global bgm_change
	global win
	global enemy_spawn_timer
	score = 0
	level = 1
	bgm_change = False
	win_countdown = win_countdown_init
	win = False
	enemy_spawn_timer = enemy_spawn_timer_init

	player1.__init__(player1.x_init, player1.y_init, player1.width, player1.height)

	fireballs.clear()
	enemies.clear()
	enemies.append(Enemy(r.randint(int(screen_width * 0.75), screen_width - 16), screen_height - 40, 16, 16))

player1 = Player(screen_width // 4, screen_height - 56, 16, 32)
fireballs = []
enemies = [Enemy(r.randint(int(screen_width * 0.75), screen_width - 16), screen_height - 40, 16, 16)]

while running:
	clock.tick(60)
	keys = p.key.get_pressed()

	if keys[p.K_ESCAPE]:
		running = False

	if keys[p.K_f]:
		if not fullscreen:
			fullscreen = True
			window = p.display.set_mode((screen_width, screen_height), p.FULLSCREEN)
		else:
			fullscreen = False
			window = p.display.set_mode((screen_width, screen_height))

	if keys[p.K_p] and (win_countdown == win_countdown_init):
		if pause_counter == pause_counter_init:
			pause_counter -= 1
			pause_sfx.play()

			if not paused:
				paused = True
				paused_text = font.render('paused', 0, (255, 255, 255))
				window.blit(paused_text, ((screen_width // 2) - (paused_text.get_width() // 2), (screen_height // 2) - (paused_text.get_height() // 2)))
				p.display.update()
			else:
				paused = False

	if (pause_counter != pause_counter_init) and (pause_counter > 0):
		pause_counter -= 1
	else:
		pause_counter = pause_counter_init

	if keys[p.K_r] and ((win_countdown == win_countdown_init) or win_countdown == 0):
		if (reset_counter == reset_counter_init) and not paused:
			reset_game()
			reset_counter -= 1

	if (reset_counter != reset_counter_init) and (reset_counter > 0):
		reset_counter -= 1
	else:
		reset_counter = reset_counter_init

	for event in p.event.get():
		if (event.type == p.QUIT) or (event.type == p.K_ESCAPE):
			running = False

	if not bgm_change:
		if not win:
			if level == final_level:
				p.mixer.music.load('bgm/castle.mp3')
			else:
				if level % 2 == 0:
					p.mixer.music.load('bgm/underworld.mp3')
				else:
					p.mixer.music.load('bgm/overworld.mp3')
		else:
			p.mixer.music.load('bgm/you_win.mp3')
		p.mixer.music.play(-1)
		bgm_change = True

	if not paused:
		if len(enemies) == 0 and win_countdown == win_countdown_init:
			if level != final_level:
				enemy_spawn_timer -= 1

				if enemy_spawn_timer == 0:
					level += 1
					spawn_sfx.play()
					enemy_spawn_timer = enemy_spawn_timer_init
					bgm_change = False

					if player1.x >= 0 and player1.x < (screen_width // 2):
						enemy_respawn_x = r.randint(int(screen_width * 0.75), screen_width - 16)
					else:
						enemy_respawn_x = r.randint(0, int(screen_width * 0.25))

					if level < 5:
						spiny = Enemy(enemy_respawn_x, screen_height - 40, 16, 16)

						if level > 2:
							spiny.speed = 2

						enemies.append(spiny)
					else:
						for i in range(0, 2, 1):
							spiny = Enemy(enemy_respawn_x, screen_height - 40, 16, 16)

							if level < 7:
								spiny.speed += i
							else:
								spiny.speed += (i + 1)

							if level == final_level:
								spiny.maximum_health *= 2
								spiny.current_health = spiny.maximum_health

							enemies.append(spiny)
			else:
				win_countdown -= 1
				p.mixer.music.pause()

		if (win_countdown != win_countdown_init) and (win_countdown > 0):
			win_countdown -= 1

		if win_countdown == 0 and not win:
			win = True
			bgm_change = False

		if not win:
			movement()
			check_collision()

		draw_game()

p.quit()