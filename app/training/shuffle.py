import random
fid = open("final_dataset.csv", "r")
li = fid.readlines()
fid.close()
print(li)

random.shuffle(li)
print(li)

fid = open("shuffled_final_dataset.csv", "w")
fid.writelines(li)
fid.close()