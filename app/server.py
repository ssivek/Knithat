import aiohttp
import asyncio
import uvicorn
import requests as rq
import json
import os
from flask import Flask, render_template
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
    prediction = learn.predict(img) #[0] # returns "(MultiCategory ribbed;cables, tensor([0., 0., 0...."
    
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
    try:
        response = rq.get(api_url, auth=(user, pswd))
        json_data = response.json()

        # info on first search result
        p_info_1 = json_data['patterns'][0]['name'] + ' by ' + json_data['patterns'][0]['pattern_author']['name']
        p_link_1 = 'https://www.ravelry.com/patterns/library/' + json_data['patterns'][0]['permalink']
        p_photo_1 = json_data['patterns'][0]['first_photo']['square_url']
        if json_data['patterns'][0]['free'] == True:
            p_free_1 = 'Free pattern? Yes'
        else:   
            p_free_1 = 'Free pattern? No'

        #info on second search result
        p_info_2 = json_data['patterns'][1]['name'] + ' by ' + json_data['patterns'][1]['pattern_author']['name']
        p_link_2 = 'https://www.ravelry.com/patterns/library/' + json_data['patterns'][1]['permalink']
        p_photo_2 = json_data['patterns'][1]['first_photo']['square_url']
        if json_data['patterns'][1]['free'] == True:
            p_free_2 = 'Free pattern? Yes'
        else:   
            p_free_2 = 'Free pattern? No'

        # info on third search result
        p_info_3 = json_data['patterns'][2]['name'] + ' by ' + json_data['patterns'][2]['pattern_author']['name']
        p_link_3 = 'https://www.ravelry.com/patterns/library/' + json_data['patterns'][2]['permalink']
        p_photo_3 = json_data['patterns'][2]['first_photo']['square_url']
        if json_data['patterns'][2]['free'] == True:
            p_free_3 = 'Free pattern? Yes'
        else:   
            p_free_3 = 'Free pattern? No'
            
        return render_template('pattern-search.html', p_info_1 = p_info_1, p_link_1 = p_link_1, p_photo_1 = p_photo_1,
            p_free_1 = p_free_1, p_info_2 = p_info_2, p_link_2 = p_link_2, p_photo_2 = p_photo_2, p_free_2 = p_free_2, 
            p_info_3 = p_info_3, p_link_3 = p_link_3, p_photo_3 = p_photo_3, p_free_3 = p_free_3)
    except rq.exceptions.HTTPError:
        return "Error: " + str(err)

if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
