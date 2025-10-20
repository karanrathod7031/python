from datetime import date

print("\n\n*********AGE CALCULATOR************")

bdate = int(input("enter buith date: "))
month = int(input("Enter buirth mounth: "))   
year = int(input("enter birth year: "))

currentDay =  date.today().day
current_mouth = date.today().month
current_year = date.today().year

age_day = abs(currentDay - bdate)
age_mounth = current_mouth - month
age_year = current_year - year

print(f"your age : {age_year} years /  {age_mounth} mounth /  {age_day} days old\n")
print(f"congratdulayion sir your cross {age_year} .")
print("\n")






