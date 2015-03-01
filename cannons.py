#1/3/2015
#This software is developed under:

#The GNU General Public License is a free, copyleft license for
#software and other kinds of works. See licence for more information

#Anycase you can use github to contact Me, the author, Pandaro or write to padarogames@gmail.com

#caution can eat your hamster!

from pyspades.server import Territory, grenade_packet
from pyspades.constants import UPDATE_FREQUENCY
from pyspades import world
from twisted.internet import reactor
from pyspades.common import Vertex3
import math
from random import randint, uniform
from math import pow, sqrt
from pyspades.constants import TC_MODE

_play=[]
class _players:#class of players to manage it
	def __init__(self,_name,_status,_ammo,_cannon,_timer,_bullets):
		self._name=False
		self._status=False
		self._ammo=0
		self._cannon=False
		self._timer=False
		self._bullets=1
	def stampa(self):
		print("player: ",self._name,self._status,self._ammo,self._cannon,self._bullets)
		
_bullets_=[]
class _bullets:#class of bullets
	def __init__(self,_name,_number,_speed,_refill,_callback,_eta,_kinetic):
		self._name=_name
		self._number=_number
		self._speed=_speed
		self._refill=_refill
		self._callback=_callback
		self._eta=_eta
		self._kinetic=_kinetic
	def stampa(self):
		print("_bullets",self._name,self._number,self._speed,_refill,_eta,_kinetic)
		
_cannons = []
_artillery_positions=_a_p=0#if>=1 control point are in random position and in give number,0=fixes(declare in _cannon_location) 
_cannons_locations=((10,10,20),(25,26,20),(30,30,20),(462,463,20),(500,500,20),(510,510,20))#list of artillery locations 

#artillery golbal settings
_ammo_mode=1#0=infinite ammo, 1=player ammo, 2=artillery ammo
_bullets_types=[0] #available types of bullets: 0 = cannonball,2 = buster,1 = cluster, 3 = missile
_persistent_players_ammo=_p_p_a=False #if True, if a plyer die, his ammunition are not 
_player_ammo=_p_a=25#number of bullets available for each player if _ammo_mode=1
_cannon_ammo=_c_a=100#number of bullets available for each artillery battery if _ammo_mode=2
_cannons_step=_c_s=0.25 #speed of cannons, set 0 to not mobile artillery
_artillery_step_height=_h_s_h=1.5#how much block can get over


#cannonball settings
CANNONBALL_NUMBER=C_N=1 #number of shooted bullets for this type i suggest only 1
CANNONBALL_SPEED=C_S=3#speed of bullets
CANNONBALL_REFILL=C_R=1#refilling time of artillery with this bullet
CANNONBALL_kINETIC=C_K=1.0#speed of secondary bullets
CANNONBALL_ETA=C_E=C_E=1.0#time before the primary bullet exploded before the collision.See clusterbomb for example.

#clusterbombs settings
CLUSTERBOMB_NUMBER=CB_N=7
CLUSTERBOMB_SPEED=CB_S=2
CLUSTERBOMB_REFILL=CB_R=4
CLUSTERBOMB_ETA=CB_E=0.75#if eta of primary explosion is 1 sec, the primary bullet exploded after 750 milliseconds
CLUSTERBOMB_KINETIC=CB_K=0.25

#bunkbusters settings
BUNKBUSTER_NUMBER=BK_N=5
BUNKBUSTER_SPEED=BK_S=2.2
BUNKBUSTER_REFILL=BK_R=4
BUNKBUSTER_ETA=BK_E=1.0
BUNKBUSTER_KINETIC=BK_K=0.3

#missiles settings
MULTIPLE_NUMBER=MB_N=4
MULTIPLE_SPEES=MB_S=2.5
MULTIPLE_REFILL=MB_R=3
MULTIPLE_ETA=MB_E=0.5
MULTIPLE_KINETIC=MB_K=0.2

def apply_script(protocol,connection,config):
	
	
	class cannons_connection(connection):
		def __init__(self, *arg, **kw):
			connection.__init__(self, *arg, **kw)
			if _bullets_types.count(0)>=1: #add cannonball
				cannonball=_bullets("cannonball",C_N,C_S,C_R,self.cannonball_bomb,C_E,C_K)
				_bullets_.append(cannonball)
			if _bullets_types.count(1)>=1: #add cluster bombs
				clusterbomb=_bullets("clusterbomb",CB_N,CB_S,CB_R,self.cluster_bomb,CB_E,CB_K)
				_bullets_.append(clusterbomb)	
			if _bullets_types.count(2)>=1: #add bunkbusters
				bunkbuster=_bullets("bunkbuster",BK_N,BK_S,BK_R,self.bunk_buster,BK_E,BK_K)
				_bullets_.append(bunkbuster)
			if _bullets_types.count(3)>=1: #add multiple
				multiple=_bullets("multiple",MB_N,MB_S,MB_R,self.multiple_bombs,MB_E,MB_K)
				_bullets_.append(multiple)
			return connection.__init__(self, *arg, **kw)
					
		def cannonball_bomb(self,grenade): #type of secondary bullet
			pos=grenade.position
			vel=Vertex3(0,0,0)
			for i in range(C_N-1):
				ball=self.protocol.world.create_object(world.Grenade, 0.0,pos, None,vel , self.grenade_exploded)
				ball.name=_bullets_[1]._name
				ball.fuse=0
				grenade_packet.value = ball.fuse
				grenade_packet.player_id = self.player_id
				grenade_packet.position = pos.get()
				grenade_packet.velocity = vel.get()
				self.protocol.send_contained(grenade_packet)				
			self.grenade_exploded(grenade)
			
		def multiple_bombs(self,grenade): #type of bullet
			eta=grenade.fuse*(1-CB_E)
			pos=grenade.position
			vel=grenade.velocity			
			vel=vel.get()
			for i in range(MB_N-1):
				X=vel[0]*uniform(1,1+MB_K)
				Y=vel[1]*uniform(1,1+MB_K)
				Z=vel[2]*uniform(1,1+MB_K)			
				speed=Vertex3(X,Y,Z)
				multiple = self.protocol.world.create_object(world.Grenade, 0.0,pos, None, speed, self.grenade_exploded)
				multiple.name = 'multiple'
				collision = multiple.get_next_collision(UPDATE_FREQUENCY)
				if collision:
					eta, x, y, z = collision					
				multiple.fuse = eta*1.1
				grenade_packet.value = multiple.fuse
				grenade_packet.player_id = self.player_id
				grenade_packet.position = pos.get()
				grenade_packet.velocity = speed.get()			
				self.protocol.send_contained(grenade_packet)
			self.grenade_exploded(grenade)				
			
		def bunk_buster(self,grenade):#type of bullet
			pos=grenade.position
			for i in range(BK_N-1):
				vel=Vertex3(uniform(BK_K*-1,BK_K),uniform(BK_K*-1,BK_K),uniform(BK_K*-1,BK_K))
				buster = self.protocol.world.create_object(world.Grenade, 0.0,pos, None,vel , self.grenade_exploded)
				eta=uniform(0,BK_E)
				collision = buster.get_next_collision(UPDATE_FREQUENCY)
				if collision:
					eta, x, y, z = collision
				buster.fuse=eta
				buster.name="buster"
				grenade_packet.value = buster.fuse
				grenade_packet.player_id = self.player_id
				grenade_packet.position = pos.get()
				grenade_packet.velocity = vel.get()
				self.protocol.send_contained(grenade_packet)
			self.grenade_exploded(grenade)	
			
		def cluster_bomb(self, grenade):#type of bullet 
			eta=grenade.fuse*(1-CB_E)
			pos=grenade.position
			for i in range(CB_N-1):
				X=uniform(-1*CB_K,CB_K)
				Y=uniform(-1*CB_K,CB_K)
				Z=uniform(-1*CB_K,CB_K)			
				speed=Vertex3(X,Y,Z)
				cluster = self.protocol.world.create_object(world.Grenade, 0.0,pos, None, speed, self.grenade_exploded)
				cluster.name = 'cluster'
				collision = cluster.get_next_collision(UPDATE_FREQUENCY)
				if collision:
					eta, x, y, z = collision					
				cluster.fuse = eta				
				grenade_packet.value = cluster.fuse
				grenade_packet.player_id = self.player_id
				grenade_packet.position = pos.get()
				grenade_packet.velocity = speed.get()			
				self.protocol.send_contained(grenade_packet)
			self.grenade_exploded(grenade)				

		def on_join(self): #into a list, player is a instance of a class
			#print("on join")			
			_play.append(self.player_id)
			_play[self.player_id]=_players(None,False,_player_ammo,False,False,_bullets_)
			return connection.on_join(self)

		def on_login(self,name):#set name & ammo 
			#print("on login")
			player=_play[self.player_id]
			player._name=self.name
			player._status=False
			player._ammo=_player_ammo	
			player._cannon=False
			player._timer=False
			player._bullets=_bullets_
			#_players.stampa(player)

		def on_spawn(self,pos): #every time a player spawn liberate himself and his artillery 
			#print("on spawn")
			player=_play[self.player_id]
			player._status=False
			for i in _cannons:
				if i.status==self.player_id:
					i.status=False
					self.protocol.update_entities()			
			return connection.on_spawn(self,pos)
		
		def on_kill(self, killer, type, grenade):#all times a player die unlock reset himself and artillery status
			#print("on kill")
			player=_play[self.player_id]
			if _persistent_players_ammo==False:
				player._ammo=_player_ammo
			player._status=False
			player._cannon=False					
			player._timer=False
			for i in _cannons:
				if i.status==self.player_id:
					i.status=False
					self.protocol.update_entities()
			return connection.on_kill(self, killer, type, grenade)

		def on_reset(self): #total  status reset
			#print("on reset")
			player=_play[self.player_id]
			player._name=False
			player._ammo=_player_ammo
			player._status=False
			player._cannon=False					
			player._timer=False
			for i in _cannons:
				if i.status==self.player_id:
					i.status=False
					self.protocol.update_entities()
			return connection.on_reset(self)

		def on_animation_update(self, jump, crouch, sneak, sprint): #on jump enter in a artillery battery if captured
			#print("on animation update")
			player=_play[self.player_id]
			if jump==True:
				if player._status!=False:
					player._status=False
					player._cannon=False					
					player._timer=False
					for i in _cannons:
						if i.status==self.player_id:
							i.status=False
							self.protocol.update_entities()					
				else:
					p=self.get_location()	
					for i in _cannons:
						if i.status!=0:
							return connection.on_animation_update(self, jump, crouch, sneak, sprint)
						dist=sqrt((pow((i.x)-p[0],2))+(pow((i.y)-p[1],2))+(pow((i.z)-p[2],2)))
						if dist<10 and i.team==self.team:	
							player._status=(i.id)
							player._cannon=(i)
							#_players.stampa(player)
							i.status=self.player_id
							self.protocol.update_entities()
							self.set_location((player._cannon.x,player._cannon.y,player._cannon.z))
							self.send_chat("Artillery enabled! up/down->MOVE, left/right->SELECT BULLETS TYPE. spade->SHOOT!")
							break
			return connection.on_animation_update(self, jump, crouch, sneak, sprint)
			
		def on_position_update(self): #if hold down up or right can move
			#print("on position update")
			player=_play[self.player_id]
			if player._cannon!=False and _cannons_step>0:
				Cannon=player._cannon
				_dir=self.world_object.orientation
				z=self.protocol.map.get_z
				start=_cannons[player._status]
				if self.world_object.up:
					z=(z(start.x+(_dir.x)*_c_s,start.y+(_dir.y),start.z))
					z=(abs(start.z-z))					
					if z>_h_s_h:
						_cannons[player._status].x+=(_dir.x*-1)*_c_s
						_cannons[player._status].y+=(_dir.y*-1)*_c_s
						return connection.on_position_update(self)
					else:
						_cannons[player._status].x+=(_dir.x)*_c_s				
						_cannons[player._status].y+=(_dir.y)*_c_s
						self.protocol.update_entities()
						Territory.update(_cannons[player._status])
						self.set_location((Cannon.x,Cannon.y,Cannon.z))
						return connection.on_position_update(self)
					
					
				elif self.world_object.down:
					z=(z(start.x+(_dir.x*-1)*_c_s,start.y+(_dir.y*-1),start.z))
					z=(abs(start.z-z))
					if z>_h_s_h:
						_cannons[player._status].x+=(_dir.x)*_c_s				
						_cannons[player._status].y+=(_dir.y)*_c_s
						return connection.on_position_update(self)
					else:
						_cannons[player._status].x+=(_dir.x*-1)*_c_s				
						_cannons[player._status].y+=(_dir.y*-1)*_c_s
						self.set_location((Cannon.x,Cannon.y,Cannon.z))
						self.protocol.update_entities()
						Territory.update(_cannons[player._status])
						return connection.on_position_update(self)
			self.protocol.update_entities()
			Territory.update(_cannons[player._status])
			return connection.on_position_update(self)

		def on_walk_update(self, up, down, left, right):#movements and change bullets type	
			#print("on walk update")		
			player=_play[self.player_id]	
			if player._cannon!=False:				
				Cannon=player._cannon
				self.set_location((Cannon.x,Cannon.y,Cannon.z))
				_dir=self.world_object.orientation
				z=self.protocol.map.get_z
				start=_cannons[player._status]
				if up and _cannons_step>0:
					z=(z(start.x+(_dir.x)*_c_s,start.y+(_dir.y),start.z))
					z=(abs(start.z-z))					
					if z>_h_s_h:
						_cannons[player._status].x+=(_dir.x*-1)*_c_s
						_cannons[player._status].y+=(_dir.y*-1)*_c_s
						return connection.on_position_update(self)
					else:
						_cannons[player._status].x+=(_dir.x)*_c_s				
						_cannons[player._status].y+=(_dir.y)*_c_s
						self.set_location((Cannon.x,Cannon.y,Cannon.z))
						self.protocol.update_entities()
						Territory.update(_cannons[player._status])
						return connection.on_walk_update(self, up, down, left, right)
				if down and _cannons_step>0: 
					z=(z(start.x+(_dir.x*-1)*_c_s,start.y+(_dir.y*-1),start.z))
					z=(abs(start.z-z))
					if z>_h_s_h:
						_cannons[player._status].x+=(_dir.x)*_c_s				
						_cannons[player._status].y+=(_dir.y)*_c_s
						return connection.on_position_update(self)
					else:
						_cannons[player._status].x+=(_dir.x*-1)*_c_s				
						_cannons[player._status].y+=(_dir.y*-1)*_c_s
						self.set_location((Cannon.x,Cannon.y,Cannon.z))
						self.protocol.update_entities()
						Territory.update(_cannons[player._status])
						return connection.on_walk_update(self, up, down, left, right)
				if right:
					first=player._bullets.pop(0)
					player._bullets.append(first)
					self.send_chat("bullets type: "+player._bullets[0]._name) 
					self.set_location((Cannon.x,Cannon.y,Cannon.z))
					return connection.on_walk_update(self, up, down, left, right)
					
				if left:
					last=player._bullets.pop(-1)
					player._bullets.insert(0,last)
					self.send_chat("bullets type: "+player._bullets[0]._name) 
					self.set_location((Cannon.x,Cannon.y,Cannon.z))
					return connection.on_walk_update(self, up, down, left, right)
				self.protocol.update_entities()
				Territory.update(_cannons[player._status])
			return connection.on_walk_update(self, up, down, left, right)
		
		def on_shoot_set(self, fire):#shoot with spade
			#print("on shoot")	
			player=_play[self.player_id]
			if player._status==0:
				return connection.on_shoot_set(self,fire)
			elif fire==False:
				return connection.on_shoot_set(self,fire)
			elif self.tool!=0:
				self.send_chat("Use spade to shoot!")
				return connection.on_shoot_set(self,fire)
			shoot=reactor.seconds()		
			bullet=player._bullets[0]
			if player._timer!=False and shoot-player._timer< bullet._refill:
				self.send_chat("Wait! refilling is underway: "+(str(bullet._refill-(shoot-player._timer)))[0:3]+"seconds")
				return connection.on_shoot_set(self,fire)
			if player._ammo >=bullet._number and _ammo_mode==1:
				player._ammo-=bullet._number
				self.send_chat("Munitions: "+str(player._ammo))
			elif _ammo_mode==2 and _cannons[player].ammo>=bullet._number:
				_cannons[player]._cannon-=bullet.number
				self.send_chat("Munition: "+str(_cannons[player]._cannon))
				Territory.update(_cannons[player._status])
				self.protocol.update_entities()				
			else:
				self.send_chat("Munition finished!")
				return connection.on_shoot_set(self,fire)
			player._timer=shoot
			pos=self.get_location()			
			position = Vertex3(pos[0],pos[1],pos[2]-0.5)
			vel=self.world_object.orientation
			orient=Vertex3(vel.x,vel.y,vel.z)
			velocity = Vertex3(vel.x* bullet._speed, vel.y* bullet._speed, vel.z* bullet._speed)			
			grenade = self.protocol.world.create_object(world.Grenade, 0.0,position, None, velocity,bullet._callback)	
			grenade.name = bullet._name			
			collision = grenade.get_next_collision(UPDATE_FREQUENCY)				
			if collision:
				eta, x, y, z = collision
			eta=eta*(1+((eta)/25))
			eta=eta*bullet._eta
			grenade.fuse = eta		
			grenade_packet.value = grenade.fuse
			grenade_packet.player_id = self.player_id
			grenade_packet.position = position.get()
			grenade_packet.velocity = velocity.get()			
			self.protocol.send_contained(grenade_packet)		
			return connection.on_shoot_set(self,fire)
		
	class cannons_protocol(protocol):#place the artillery/control point
		game_mode = TC_MODE	
		def get_cp_entities(self):
			#print("get cp entities")
			if _a_p==0:#user defined
				for i, (x, y,z) in enumerate(_cannons_locations):
					entity = Territory(i, self, *(x, y, z))
					self.cp = entity
					self.spawn_cp = entity
					self.cp.disabled = False
					self.cp.name="cannon"
					self.cp.ammo=_cannon_ammo
					self.cp.status=False
					_cannons.append(entity)
			elif _a_p == 1:#random
				for i in range(_a_p):
					x=randint(0,512)
					y=randint(0,512)
					z=self.map.get_height(x,y)
					entity = Territory(i, self, *(x, y, z))
					self.cp = entity
					self.spawn_cp = entity
					self.cp.disabled = False
					self.cp.name="cannon"
					self.cp.ammo=_cannon_ammo
					self.cp.status=False
					_cannons.append(entity)
			elif _a_p==-1:#disabled
				return protocol.get_cp_entities(self)
				
			self.update_entities()
			return _cannons
			return protocol.get_cp_entities(self)
		
		def on_cp_capture(self,cp):
			#print("on capture")
			self.send_chat("Jump to enable artillery mode!")
			return protocol.on_cp_capture(self,cp)

		def on_game_end(self):
			#print("on game end")
			for i in _play:
				i._status=False
				i._ammo=_p_a
				i._cannon=False
				i._timer=False
			for i in _cannons:
				i.ammo=_cannon_ammo
				i.status=False					
			return protocol.on_game_end(self)

		
	return cannons_protocol, cannons_connection
