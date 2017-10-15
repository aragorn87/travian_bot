from bs4 import BeautifulSoup
import requests, time

def create_req():
    r = requests.session()
    r.post('https://ts7.travian.com/dorf1.php', data={
            'name': 'foobar',
            'password': 'foo@',
            's1': 'Einloggen',
            'login': time.time()
    })
    return r;

def get_current_levels(req_handler):
    s = req_handler.get('https://ts7.travian.com/dorf1.php')
    soup = BeautifulSoup(s.content, "lxml")
    lumber = clean_numbers(soup.find(id="stockBarResource1").find(id="l1").get_text().strip()[1:-1])
    clay = clean_numbers(soup.find(id="stockBarResource2").find(id="l2").get_text().strip()[1:-1])
    iron = clean_numbers(soup.find(id="stockBarResource3").find(id="l3").get_text().strip()[1:-1])
    crop=clean_numbers(soup.find(id="stockBarResource4").find(id="l4").get_text().strip()[1:-1])
    return lumber, clay, iron, crop;

def get_prod_rate(req_handler):
    s = req_handler.get('https://ts7.travian.com/dorf1.php')
    soup = BeautifulSoup(s.content, "lxml")
    lumber_prod=clean_numbers(soup.find(id="production").find_all("tr")[1].find('td', class_="num").get_text().strip()[1:-1])
    clay_prod=clean_numbers(soup.find(id="production").find_all("tr")[2].find('td', class_="num").get_text().strip()[1:-1])
    iron_prod=clean_numbers(soup.find(id="production").find_all("tr")[3].find('td', class_="num").get_text().strip()[1:-1])
    crop_prod=clean_numbers(soup.find(id="production").find_all("tr")[4].find('td', class_="num").get_text().strip()[1:-1])
    return lumber_prod, clay_prod, iron_prod, crop_prod;

def get_queue_len(req_handler):
    s = req_handler.get('https://ts7.travian.com/dorf1.php')
    soup = BeautifulSoup(s.content, "lxml")
    queue = len(soup.find('div', class_="boxes-contents cf").find_all('div', class_="name"))
    wait_time= int(soup.find('div', class_="boxes-contents cf").find_all('div', class_="buildDuration")[0].find("span")['value'])
    return queue, wait_time;

def get_costs(req_handler, i):
    url1='https://ts7.travian.com/build.php?id=' + str(i)
    t = req_handler.get(url1)
    soup = BeautifulSoup(t.content, "lxml")
    lumber_cost=clean_numbers(soup.find_all('div', class_="showCosts")[0].find(title="Lumber").get_text().strip())
    clay_cost=clean_numbers(soup.find_all('div', class_="showCosts")[0].find(title="Clay").get_text().strip())
    iron_cost=clean_numbers(soup.find_all('div', class_="showCosts")[0].find(title="Iron").get_text().strip())
    crop_cost=clean_numbers(soup.find_all('div', class_="showCosts")[0].find(title="Crop").get_text().strip())
    free_crop_cost=clean_numbers(soup.find_all('div', class_="showCosts")[0].find(title="Free crop").get_text().strip())
    return lumber_cost, clay_cost, iron_cost, crop_cost, free_crop_cost;

def enqueue(req_handler, i):
    url1='https://ts7.travian.com/build.php?id=' + str(i)
    t = req_handler.get(url1)
    soup = BeautifulSoup(t.content, "lxml")
    x=soup.find('div', class_="section1").find('button',class_="green build").get('onclick')
    a=x[x.find('a=')+2:x.find('&c')]
    c=x[x.find('c=')+2:x.find(';')-1]
    url = 'https://ts7.travian.com/dorf1.php?a='+ a + '&c=' + c
    r.get(url)
    print "Queued Production Unit: ", i
    return ;

def clean_numbers(p):
    p_text=p
    if p_text.find('.')!=-1:
        z=p_text[:p_text.find('.')] + p_text[p_text.find('.')+1:]
    else:
        z=p_text
    return int(z)
	
r=create_req()
s = r.get('https://ts7.travian.com/dorf1.php')
soup = BeautifulSoup(s.content, "lxml")
lumber_prod, clay_prod, iron_prod, crop_prod = get_prod_rate(r)
lumber, clay, iron, crop = get_current_levels(r)
queue, wait_time = get_queue_len(r)

setting_queue=0
while setting_queue == 0:
    max_time=999999
    for i in range(1,19):
        lumber_cost, clay_cost, iron_cost, crop_cost, free_crop_cost=get_costs(r,i)
        if ((lumber>=lumber_cost) & (clay>=clay_cost) & (iron >=iron_cost) & (crop>=crop_cost) & (queue<2)):
            enqueue(r,i)
            queue, wait_time = get_queue_len(r)
            lumber_prod, clay_prod, iron_prod, crop_prod = get_prod_rate(r)
            lumber, clay, iron, crop = get_current_levels(r)
        else:
            print 'Not Enough Resources for Production Unit: ', i
            timerequired = max(max(lumber_cost-lumber,0)*60.0*60.0/lumber_prod, max(clay_cost-clay,0)*60.0*60.0/clay_prod, max(iron_cost-iron,0)*60.0*60.0/iron_prod, max(crop_cost-crop,0)*60.0*60.0/crop_prod)
            if timerequired<max_time:
                max_time=max(timerequired, wait_time)
            #print 'Time required = ', timerequired
    print "Sleeping for", max_time, " seconds. Will wake up at ", str(time.ctime(int(time.time() + max_time)))
    time.sleep(max_time)
    print "Good Morning"
    r = create_req()
    s = r.get('https://ts7.travian.com/dorf1.php')
    soup = BeautifulSoup(s.content, "lxml")
    queue, wait_time = get_queue_len(r)
    lumber_prod, clay_prod, iron_prod, crop_prod = get_prod_rate(r)
    lumber, clay, iron, crop = get_current_levels(r)