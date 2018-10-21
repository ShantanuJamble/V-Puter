import collections
import requests
from bs4 import BeautifulSoup
#link = 'https://vox.veritas.com/t5/NetBackup/Netbackup-Client-quot-Error-Installation-Failed-quot/td-p/484903'
link = 'https://vox.veritas.com/t5/NetBackup/PBX-Issue/m-p/694822#M184722'
headers = {"user-agent": "Mozilla/5.0",}
resp = requests.get(link, headers=headers)
if resp.status_code == 200:
    soup = BeautifulSoup(resp.content, "html.parser")
    ans = soup.find_all('div', {"class":"lia-component-solution-list"})
    ans = ans[0].find_all('div',{"class":"lia-message-body-content"})
    ans = ans[0].find_all('p')
solution=''
for sol in ans:
    solution = solution + sol.text+"\n"
if solution != '':
    solution = solution+ "\nFor more details visit:\n " + link
else:
    solution = "Please visit:\n " + link
print solution
