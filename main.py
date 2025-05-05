from quart import Quart, session, render_template
from datastar_py.sse import ServerSentEventGenerator as SSE

from tinydb import TinyDB
from faker import Faker

from champs import champs


# CONFIG

app = Quart(__name__)
app.secret_key = 'a_secret_key'

db = TinyDB("data.json", sort_keys=True, indent=2)
games = db.table('games')

fake = Faker()

# VIEW STUFF

async def render_side(color, picks):
    if color == "blue":
        html = '<div id="blue-side" data-view-transition="\'slide-right\'"><p class="gc">BLUE SIDE</p>'
        for i in [0, 3, 4, 7, 8]:
            i = str(i)
            pick_value = picks.get(i, "")
            if pick_value:
                champ = champs[pick_value]
                html += f'''<div class="pick"><div class="pick-legend" style="background-position: {champ['pos'][0]}px {champ['pos'][1]}px;"></div><div class="gc">{pick_value}</div></div>'''
            else:
                html += '<div class="pick"><div></div><div></div></div>'
        html += '</div>'
    else:  # red side
        html = '<div id="red-side" data-view-transition="\'slide-left\'"><p class="gc">RED SIDE</p>'
        for i in [1, 2, 5, 6, 9]:
            i = str(i)
            pick_value = picks.get(i, "")
            if pick_value:
                champ = champs[pick_value]
                html += f'<div class="pick"><div class="gc">{pick_value}</div><div class="pick-legend" style="background-position: {champ['pos'][0]}px {champ['pos'][1]}px;"></div></div>'
            else:
                html += '<div class="pick"><div></div><div></div></div>'
        html += '</div>'
    return html

async def drafter():
    room_info = "Hmm problem."
    room_record = None
    room_id = session.get('room_id')
    if room_id:
        room_record = games.get(doc_id=room_id)
        if room_record:
            room_info = (
                f"Room: {room_record.get('name')} | "
                f"Blue: {room_record.get('blue')} | "
                f"Red: {room_record.get('red')}"
            )
    picks = room_record.get('picks')
    
    blue_html = await render_side("blue", picks)
    red_html = await render_side("red", picks)
            
    html = f'''
    <main id="main">
        <div id="main-container">
        {blue_html}
        <div id="picker" data-signals-filter="'all'">
            <div id="roles">
            <img alt="top" src="/static/img/top.webp" 
            data-on-click ="$filter == 'top' ? $filter = 'all' : $filter = 'top'" 
            data-attr-selected="$filter == 'top'">
            <img alt="jungle" src="/static/img/jungle.webp" data-on-click="$filter == 'jun' ? $filter = 'all' : $filter = 'jun'" data-attr-selected="$filter == 'jun'">
            <img alt="mid" src="/static/img/mid.webp" data-on-click="$filter == 'mid' ? $filter = 'all' : $filter = 'mid'" data-attr-selected="$filter == 'mid'">
            <img alt="adc" src="/static/img/adc.webp" data-on-click="$filter == 'adc' ? $filter = 'all' : $filter = 'adc'" data-attr-selected="$filter == 'adc'">
            <img alt="supp" src="/static/img/supp.webp" data-on-click="$filter == 'sup' ? $filter = 'all' : $filter = 'sup'" data-attr-selected="$filter == 'sup'">
            <div></div>
            <input data-bind-search type="text" placeholder="Search"></input>
            </div>
            <div id="legends" data-on-click="@get('/pick/' + event.target.id)">
            {"".join(
                [
                    f'''
                    <div id="{name}" 
                    class="legend {'nope' if name in picks.values() else ''}" 
                    aria-describedby="aria-{name}" 
                    style="background-position: {champ['pos'][0]}px {champ['pos'][1]}px;" 
                    data-show="($filter == 'all' || $filter == {'|| $filter == '.join(f"'{role}'" for role in champ['role'])}) 
                    && ($search == '' || '{name}'.toLowerCase().includes($search.toLowerCase()))">'''
                    + f'<div id=aria-{name} role="tooltip">{name}</div></div>'
                    for name, champ in champs.items()
                ]
            )}
            </div>
        </div>
        {red_html}
        </div>
        <div id="info" class="gc">{room_info}</div>
        {'<div id="info" class="gc">COMPUTE DRAFTS</div>' if picks.get("9") else ""}
    </main>
    '''
    return html

# APP STUFF

@app.before_request
async def before_request():
    if not session.get('user_id'): 
        session['user_id'] = fake.name()

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/game')
async def new_game():
    new_room = fake.color_name()
    room_id = games.insert({
        'name': new_room, 
        'red': "AI", 
        'blue': session['user_id'], 
        'picks': {i: "" for i in range(10)}
    })
    session['room_id'] = room_id
    html = await drafter()
    return SSE.merge_fragments(fragments=[html], use_view_transition=True)

@app.route('/pick/<legend>')
async def pick(legend):
    room_id = session.get('room_id')
    
    if room_id and (game_record := games.get(doc_id=room_id)):
        picks = game_record.get('picks', {})
        if legend not in picks.values():
            for i in range(10):
                i = str(i)
                if picks[i] == "":
                    picks[i] = legend
                    break
            games.update({'picks': picks}, doc_ids=[room_id])
        
    html = await drafter()
    return SSE.merge_fragments(fragments=[html], use_view_transition=True)

if __name__ == '__main__':
    app.run(debug=True)
