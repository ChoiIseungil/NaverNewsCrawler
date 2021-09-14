import re
import csv
import glob

files = ['가뭄','강풍','냉해','대설','무더위','쓰나미','지진','태풍','폭설','폭염','힌피','해일','호우','혹서','홍수','황사']

pattern = r'([^ \r\n]+)\s(사망|부상|인명 피해|재산 피해)([\r\n]| |$)'


with open ("./results/matches.csv",'w',encoding='UTF-8',newline='') as big_f:
    writer = csv.writer(big_f)
    for file in glob.glob("./results/*.csv"):
        print(file)
        with open(file,'r',encoding='utf-8') as f:
            print(f)
            reader = csv.reader(f)
            # next(reader)
            for row in reader:
                title = re.findall(pattern,row[1])
                date = row[2]
                content = re.findall(pattern,row[3])
                if title:
                    for elem in title: writer.writerow([file,date,elem[0],elem[1]])
                if content:
                    for elem in content: writer.writerow([file,date,elem[0],elem[1]])
            f.close()
big_f.close()
print("Finished!")
