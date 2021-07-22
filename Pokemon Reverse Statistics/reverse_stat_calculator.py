def get_base_hp_from_stats(Level, Stat, IV, EV, Nature):
    Base = ((Stat - 10)*(100/Level) - 100 - IV - EV/4)/2
    return round(Base)

def get_base_stat_from_stats(Level, Stat, IV, EV, Nature):
    Base = (((Stat/Nature) - 5)*(100/Level) - IV - (EV/4))/2
    return round(Base)

hp = get_base_hp_from_stats(25,85,10,12,1)
attack = get_base_stat_from_stats(25,64,14,22,1.1)
special_attack = get_base_stat_from_stats(25,45,2,12,1)
defense = get_base_stat_from_stats(25,37,27,12,0.9)
special_defense = get_base_stat_from_stats(25,72,17,23,1)
speed = get_base_stat_from_stats(25,50,15,22,1)
base_stat_total = hp + attack + special_attack + defense + special_defense + speed

print("HP: "+str(hp))
print("Attack: "+str(attack))
print("Defense: "+str(defense))
print("Special Attack: "+str(special_attack))
print("Special Defense: "+str(special_defense))
print("Speed: "+str(speed))
print("Base Stat Total: "+str(base_stat_total))
