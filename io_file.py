f = open("sample.txt","r+")
data=f.read()

new_data=data.replace("java","python")
f = open("sample.txt","r+")
data=f.write(new_data)
