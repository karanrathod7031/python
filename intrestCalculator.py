from datetime import date
import sys

print("\n-------------------INTREST CALCULATOR-------------------")

bdate = int(input("enter date: "))
if bdate > 31 :
    print("Invalid date,\n Pease enter valid date..")
    sys.exit()
else:
    pass
# # ----------------------------------------------------------------------------------------------------------
month = int(input("Enter mounth: ")) 
if month > 12 :
    print("Invalid date, \n Pease enter valid date..")
    sys.exit()
else:
    pass
# # ---------------------------------------------------------------------------------------------------------
year = int(input("Pnter year: "))
# # ---------------------------------------------------------------------------------------------------------

currentDay =  date.today().day
current_mouth = date.today().month
current_year = date.today().year

days = abs(currentDay - bdate)
mounths = abs(current_mouth - month)
years = abs(current_year - year)

print(f" {years} years /  {mounths} mounth /  {days} days ")
# -----------------------------------------------------------------------------------------------------------------------

total_mounths= years*12+mounths

amount = int(input("enter principle amount: "))
intrest_rate= int(input("intrest rate: "))
print("---------------------------------------------------------")
print("priciple amount is: ",amount)

intrest_amount= (amount * intrest_rate *total_mounths) /100
print("intrest amount is: ",intrest_amount)
print("---------------------------------------------------------")
total_amount = amount + intrest_amount
print("total amount is: ",total_amount,"\n")




