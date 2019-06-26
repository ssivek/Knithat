import aiohttp
import asyncio
import uvicorn

import requests as rq

from fastai import *
from fastai.vision import *
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

export_file_url = 'https://www.dropbox.com/s/kmgcoaqbfo76kbt/export.pkl?dl=1'
export_file_name = 'export.pkl'

user = os.getenv('user')
pswd = os.getenv('pswd')

classes = ['felted', 'tassel', 'stripes', 'bobble-or-popcorn', 'cables', 'eyelets', 'lace', 'ribbed', 
    'slipped-stitches', 'textured', 'twisted-stitches', 'fairisle', 'stranded', 'appliqued', 
    'norwegian']

path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))


async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f:
                f.write(data)


async def setup_learner():
    await download_file(export_file_url, path / export_file_name)
    try:
        learn = load_learner(path, export_file_name)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise


loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()


@app.route('/')
async def homepage(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())


@app.route('/analyze', methods=['POST'])
async def analyze(request):
    img_data = await request.form()
    img_bytes = await (img_data['file'].read())
    img = open_image(BytesIO(img_bytes))
    prediction = learn.predict(img)
    json_data = get_api_call(prediction)
    p1 = extract_pattern_1_info(json_data)
    p1_info = p1[0]
    p1_link = p1[1]
    p1_photo = p1[2]
    p1_free = p1[3]
    p2 = extract_pattern_2_info(json_data)
    p2_info = p2[0]
    p2_link = p2[1]
    p2_photo = p2[2]
    p2_free = p2[3]
    p3 = extract_pattern_3_info(json_data)
    p3_info = p3[0]
    p3_link = p3[1]
    p3_photo = p3[2]
    p3_free = p3[3]
    return JSONResponse({
        'hat_1_info' : p1_info,
        'hat_1_link' : p1_link,
        'hat_1_photo' : p1_photo,
        'hat_1_free' : p1_free,
        'hat_2_info' : p2_info,
        'hat_2_link' : p2_link,
        'hat_2_photo' : p2_photo,
        'hat_2_free' : p2_free,
        'hat_3_info' : p3_info,
        'hat_3_link' : p3_link,
        'hat_3_photo' : p3_photo,
        'hat_3_free' : p3_free
        })


def get_api_call(prediction):
    # transform prediction into API call to Ravelry using detected pattern attributes
    a = str(prediction) # makes list from prediction into a string
    b = a.split(',') # splits string on the commas
    c = b[0] # extracts first item out of string "(MultiCategory ribbed;cables, ..."
    d = c.split(' ') # splits item(s) on the space (Multicategory, ribbed;cables)
    e = d[1:] # extracts the second and all following items, which are pattern attributes, as a list with one item ['ribbed;cables']
    f = e[0].split(';') # splits item(s) on the semicolon into a new list ['ribbed', 'cables']
    pattern_attributes = '&pa=' + '%2B'.join(e) # joins pattern attributes to add to API call string
    params = '&' + pattern_attributes # + user_input if/when user input options eventually exist!
    api_url = str('https://api.ravelry.com/patterns/search.json?craft=knitting&photo=yes&pc=hat&sort=best&ratings=5&page=1' + str(params))
   
    # make request and parse out results
    response = rq.get(api_url, auth=(user, pswd))
    json_data = response.json()
    return json_data


def extract_pattern_1_info(json_data): # info on first search result
    pattern_1 = []
    p_info_1 = json_data['patterns'][0]['name'] + ' by ' + json_data['patterns'][0]['pattern_author']['name']
    p_link_1 = 'https://www.ravelry.com/patterns/library/' + json_data['patterns'][0]['permalink']
    p_photo_1 = json_data['patterns'][0]['first_photo']['square_url']
    if json_data['patterns'][0]['free'] == True:
        p_free_1 = 'Free pattern? Yes'
    else:   
        p_free_1 = 'Free pattern? No'
    pattern_1.append(p_info_1)
    pattern_1.append(p_link_1)
    pattern_1.append(p_photo_1)
    pattern_1.append(p_free_1)
    return pattern_1


def extract_pattern_2_info(json_data): #info on second search result
    pattern_2 = []
    p_info_2 = json_data['patterns'][1]['name'] + ' by ' + json_data['patterns'][1]['pattern_author']['name']
    p_link_2 = 'https://www.ravelry.com/patterns/library/' + json_data['patterns'][1]['permalink']
    p_photo_2 = json_data['patterns'][1]['first_photo']['square_url']
    if json_data['patterns'][1]['free'] == True:
        p_free_2 = 'Free pattern? Yes'
    else:   
        p_free_2 = 'Free pattern? No'
    pattern_2.append(p_info_2)
    pattern_2.append(p_link_2)
    pattern_2.append(p_photo_2)
    pattern_2.append(p_free_2)    
    return pattern_2


def extract_pattern_3_info(json_data): # info on third search result
    pattern_3 = []
    p_info_3 = json_data['patterns'][2]['name'] + ' by ' + json_data['patterns'][2]['pattern_author']['name']
    p_link_3 = 'https://www.ravelry.com/patterns/library/' + json_data['patterns'][2]['permalink']
    p_photo_3 = json_data['patterns'][2]['first_photo']['square_url']
    if json_data['patterns'][2]['free'] == True:
        p_free_3 = 'Free pattern? Yes'
    else:   
        p_free_3 = 'Free pattern? No'
    pattern_3.append(p_info_3)
    pattern_3.append(p_link_3)
    pattern_3.append(p_photo_3)
    pattern_3.append(p_free_3)    
    return pattern_3


if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")