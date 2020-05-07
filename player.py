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
        self.battery_stock = np.zeros(49) #a(t)
        self.capacity = 100
        self.max_load = 70
        self.prices = {"purchase" : [],"sale" : []}
        self.imbalance={"purchase_cover":[], "sale_cover": []}

    def take_decision(self, time):

            # TO DO:
            # implement your policy here to return the load charged / discharged in the battery
            # below is a simple example
            
                
            
            if time>=12 and time<=43:
                #on stocke qd le prix est min
                if self.prices["sale"][time-1]<=0.077:
                    return min(self.max_load,max(0,2*self.sun[time-1]-self.sun[time-2]))
                #on stocke rien qd le prix est moyen
                elif self.prices["sale"][time-1]<=0.083:
                    return 0
                #le reste du temps on vend tout (production + stock)
                else:
                    return -self.max_load
                

            #on remplit entièrement la batterie achetant à 3 temps t pendant la nuit pour pouvoir le revendre plus cher le matin
            elif time in [0,2,4]:
                return +self.max_load
                
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
    
    def observe(self, t, sun, price, imbalance):
        self.sun.append(sun)
        
        self.prices["purchase"].append(price["purchase"])
        self.prices["sale"].append(price["sale"])

        self.imbalance["purchase_cover"].append(imbalance["purchase_cover"])
        self.imbalance["sale_cover"].append(imbalance["sale_cover"])
    
    def reset(self):
        self.load= np.zeros(48)
        self.bill = np.zeros(48)
        
        last_bat = self.battery_stock[-1]
        self.battery_stock = np.zeros(49)
        self.battery_stock[0] = last_bat
        
        self.sun=[]
        self.prices = {"purchase" : [],"sale" : []}
        self.imbalance={"purchase_cover":[], "sale_cover": []}

