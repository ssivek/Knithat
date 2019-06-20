import aiohttp
import asyncio
import uvicorn
from fastai import *
from fastai.vision import *
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

export_file_url = 'https://www.dropbox.com/s/kmgcoaqbfo76kbt/export.pkl?dl=1'
export_file_name = 'export.pkl'

classes = classes = ['felted', 'tassel', 'stripes', 'bobble-or-popcorn', 'cables', 'eyelets', 'lace', 'ribbed', 
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
    prediction = learn.predict(img) #[0] # returns "(MultiCategory ribbed, tensor([0., 0., 0...."
    a = str(prediction) # makes list from prediction into a string
    b = a.split(',') # splits string on the commas
    c = b[0] # extracts first item out of string "(MultiCategory ribbed"
    d = c.split(' ') # splits item(s) on the space
    e = d[1:] # extracts the second and all following items, which are pattern attributes
    custom_search = '%2B'.join(e) # constructs string from pattern attributes in e, joining with '%2B' for Ravelry search
    search_url = 'https://www.ravelry.com/patterns/search#craft=knitting&photo=yes&pc=hat&sort=best&view=captioned_thumbs&ratings=5&pa='
    url_all =  search_url + custom_search # concatenates start of search URL with custom attributes joined as string
    return JSONResponse({'result': str(url_all)})
    
if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
