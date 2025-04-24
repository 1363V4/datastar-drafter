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

async def view(state):
    match state:
        case "test":
            room_info = "Game room not found."
            room_record = None
            room_id = session.get('game_room_id')
            if room_id:
                room_record = games.get(doc_id=room_id)
                if room_record:
                    room_info = (
                        f"Room: {room_record.get('name')} | "
                        f"Blue: {room_record.get('blue')} | "
                        f"Red: {room_record.get('red')}"
                    )
            picks = room_record.get('picks')
            
            blue_html = ""
            for i in [0, 3, 4, 7, 8]:
                i = str(i)
                pick_value = picks.get(i, "")
                if pick_value:
                    champ = champs[pick_value]
                    blue_html += f'''<div class="pick"><div class="pick-legend" style="background-position: {champ['pos'][0]}px {champ['pos'][1]}px;"></div><div class="gc">{pick_value}</div></div>'''
                else:
                    blue_html += '<div class="pick"><div></div><div></div></div>'
            red_html = ""
            for i in [1, 2, 5, 6, 9]:
                i = str(i)
                pick_value = picks.get(i, "")
                if pick_value:
                    champ = champs[pick_value]
                    red_html += f'<div class="pick"><div class="gc">{pick_value}</div><div class="pick-legend" style="background-position: {champ['pos'][0]}px {champ['pos'][1]}px;"></div></div>'
                else:
                    red_html += '<div class="pick"><div></div><div></div></div>'
            
            html = f'''
            <main id="main">
              <div id="main-container">
                <div id="blue-side" data-view-transition="'slide-left'">
                  <p class="gc">BLUE SIDE</p>
                  {blue_html}
                </div>
                <div id="picker" data-signals-filter="'all'">
                  <div id="roles">
                    <img alt="top" src="/static/img/top.webp" data-on-click__viewtransition ="$filter == 'top' ? $filter = 'all' : $filter = 'top'" data-attr-selected="$filter.includes('top')">
                    <img alt="jungle" src="/static/img/jungle.webp" data-on-click__viewtransition="$filter == 'jun' ? $filter = 'all' : $filter = 'jun'" data-attr-selected="$filter.includes('jun')">
                    <img alt="mid" src="/static/img/mid.webp" data-on-click__viewtransition="$filter == 'mid' ? $filter = 'all' : $filter = 'mid'" data-attr-selected="$filter.includes('mid')">
                    <img alt="adc" src="/static/img/adc.webp" data-on-click__viewtransition="$filter == 'adc' ? $filter = 'all' : $filter = 'adc'" data-attr-selected="$filter.includes('adc')">
                    <img alt="supp" src="/static/img/supp.webp" data-on-click__viewtransition="$filter == 'sup' ? $filter = 'all' : $filter = 'sup'" data-attr-selected="$filter.includes('sup')">
                    <div></div>
                    <input type="text" placeholder="Search"></input>
                  </div>
                  <div id="legends" data-on-click="@get('/pick/' + event.target.id)">
                    {"".join(
                        [
                            f'''<div id="{name}" class="legend {'nope' if name in picks.values() else ''}" aria-describedby="aria-{name}" style="background-position: {champ['pos'][0]}px {champ['pos'][1]}px;" data-show="$filter == 'all' || $filter == {'|| $filter == '.join(f"'{role}'" for role in champ['role'])}">'''
                            + f'<div id=aria-{name} role="tooltip">{name}</div></div>'
                            for name, champ in champs.items()
                        ]
                    )}
                  </div>
                </div>
                <div id="red-side"  data-view-transition="'slide-right'">
                  <p class="gc">RED SIDE</p>
                  {red_html}
                </div>
              </div>
              <div id="info" class="gc">{room_info}</div>
              {'<div id="info" class="gc">COMPUTE DRAFTS</div>' if picks.get("9") else ""}
            </main>
            '''
            return html
        case _:
            return '<main id="main" class="gc">huh?</main>'

async def view_route():
    state = session['state']
    html = await view(state)
    return SSE.merge_fragments(fragments=[html], use_view_transition=True)

# APP STUFF

@app.before_request
async def before_request():
    if not session.get('user_id'): 
        session['user_id'] = fake.name()
    if not session.get('state'): 
        session['state'] = "home"

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/game')
async def new_game():
    new_room = fake.color_name()
    game_room_id = games.insert({
        'name': new_room, 
        'red': "AI", 
        'blue': session['user_id'], 
        'picks': {i: "" for i in range(10)}
    })
    session['game_room_id'] = game_room_id
    session['state'] = "test"
    return await view_route()

@app.route('/pick/<legend>')
async def pick(legend):
    game_room_id = session.get('game_room_id')
    if game_room_id is not None:
        game_record = games.get(doc_id=game_room_id)
        if game_record is not None:
            picks = game_record.get('picks', {})
            for i in range(10):
                i = str(i)
                if picks[i] == "":
                    picks[i] = legend
                    break
            games.update({'picks': picks}, doc_ids=[game_room_id])
    return await view_route()

if __name__ == '__main__':
    app.run(debug=True)
