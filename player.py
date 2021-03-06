import numpy as np
import os
from numpy.random import randint

class Player:

    def __init__(self):
        self.dt = 0.5
        self.efficiency=0.95
        self.sun=[]
        self.bill = np.zeros(48) # prix de vente de l'électricité
        self.load= np.zeros(48) # chargement de la batterie (li)
        self.penalty=np.zeros(48)
        self.grid_relative_load=np.zeros(48)
        self.battery_stock = np.zeros(49) #a(t)
        self.capacity = 100
        self.max_load = 70
        self.prices = {"purchase" : [],"sale" : []}
        self.imbalance={"purchase_cover":[], "sale_cover": []}

    def take_decision(self, time):

            # TO DO:
            # implement your policy here to return the load charged / discharged in the battery
            # below is a simple example
                
            #actions de la journée
            if time>=12 and time<=43:
                
                #on stocke qd le prix est min
                if time >=21 and time <30 :
                    return self.max_load/3
                    
                #le reste du temps on vend presque tout (production + stock) sur les 2 pics matin et soir
                elif time<=15 :
                    return -self.max_load*3/8
                    
                elif  time>=38 and time<40 :
                    return -self.max_load/3
                    
                elif time>=40 :
                    return -self.max_load*21/36
                    
                #on stocke rien et on ne vend pas de stock
                else :
                    return 0
                
                

            #on remplit à moitié la batterie tout au long de la nuit en achetant moins sur le pic 
            elif time >= 44:
                return +self.max_load*3/31
            
            elif time >=0 and time <=2:
                return +self.max_load*3/60
            
            elif time >2 and time <12:
                return +self.max_load*3/31
                
            else:
                return 0
                
                
                

                

    def update_battery_stock(self, time,load):
            if abs(load) > self.max_load:
                load = self.max_load*np.sign(load) #saturation au maximum de la batterie
            
            new_stock = self.battery_stock[time] + (self.efficiency*max(0,load) - 1/self.efficiency * max(0,-load))*self.dt
            
            #On rétablit les conditions si le joueur ne les respecte pas :
            
            if new_stock < 0: #impossible, le min est 0, on calcule le load correspondant
                load = - self.battery_stock[time] / (self.efficiency*self.dt)
                new_stock = 0
    
            elif new_stock > self.capacity:
                load = (self.capacity - self.battery_stock[time]) / (self.efficiency*self.dt)
                new_stock = self.capacity
    
            self.battery_stock[time+1] = new_stock
            
            
            return load
        
    def compute_load(self,time,sun):
        load_player = self.take_decision(time)
        load_battery=self.update_battery_stock(time,load_player)
        self.load[time]=load_battery - sun
        
        return self.load[time]
    
    def observe(self, t, sun, price, imbalance,grid_relative_load):
        self.sun.append(sun)
        
        self.prices["purchase"].append(price["purchase"])
        self.prices["sale"].append(price["sale"])

        self.imbalance["purchase_cover"].append(imbalance["purchase_cover"])
        self.imbalance["sale_cover"].append(imbalance["sale_cover"])
        self.grid_relative_load[t]=grid_relative_load
    
    def reset(self):
        self.load= np.zeros(48)
        self.bill = np.zeros(48)
        self.penalty=np.zeros(48)
        self.grid_relative_load=np.zeros(48)
        
        last_bat = self.battery_stock[-1]
        self.battery_stock = np.zeros(49)
        self.battery_stock[0] = last_bat
        
        self.sun=[]
        self.prices = {"purchase" : [],"sale" : []}
        self.imbalance={"purchase_cover":[], "sale_cover": []}
