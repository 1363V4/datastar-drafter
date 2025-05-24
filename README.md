# Datastar Drafter

A League of Legends champion draft simulator built with **Datastar**, showcasing reactive web development patterns including dynamic filtering, real-time champion selection, and smooth UI transitions.
This drafter demonstrates Datastar's power for building game-like interfaces with complex state management, real-time filtering, and smooth user interactions while maintaining clean, declarative code.

## Overview

This League of Legends drafter application demonstrates Datastar's capabilities for building interactive, responsive web applications. Users can select champions for both blue and red teams with live filtering by role, search functionality, and visual feedback during the draft process.

## Project Structure

```
datastar-drafter/
├── main.py               # Main Quart application
├── champs.py             # Champion data with roles and sprite positions
├── templates/
│   └── index.html        # Landing page template
├── static/
│   ├── css/
│   │   ├── main.css      # Main stylesheet with grid layouts
│   │   └── gold.css      # League of Legends themed styling
│   └── img/
│       ├── champion0.png # Champion sprite sheet
│       ├── lol-icon.png  # Application favicon
│       └── role icons/   # Top, jungle, mid, ADC, support icons
├── datastar_py/          # Local Datastar Python integration
└── data.json             # TinyDB storage for game states
```

## Technology Stack

- **Backend**: Python with Quart (async Flask)
- **Frontend**: Datastar for reactive UI
- **Database**: TinyDB for lightweight persistence
- **State Management**: In-memory session storage
- **UI Assets**: League of Legends champion sprites and role icons

## Datastar Integration & Features

### 1. Client-Side Setup

The frontend loads Datastar from CDN and establishes the reactive foundation:

```html
<script
  type="module"
  src="https://cdn.jsdelivr.net/gh/starfederation/datastar@1.0.0-beta.11/bundles/datastar.js"
></script>
```

### 2. Event Handling & Game Initialization

**Landing Page Navigation**

```html
<div class="button gp gm" data-on-click="@get('/game')">VS AI</div>
```

- `data-on-click="@get('/game')"`: Datastar directive that creates a new game session
- Smooth transition to the draft interface using view transitions

### 3. Reactive Champion Filtering System

**Role-Based Filtering**

```html
<img
  alt="top"
  src="/static/img/top.webp"
  data-on-click="$filter == 'top' ? $filter = 'all' : $filter = 'top'"
  data-attr-selected="$filter == 'top'"
/>
```

Key Datastar concepts demonstrated:

- **Conditional Signal Updates**: Toggle between specific role and 'all' filter
- **Reactive Attributes**: `data-attr-selected` changes appearance based on filter state
- **Ternary Operations**: Complex conditional logic within Datastar expressions

**Text Search Integration**

```html
<input data-bind-search type="text" placeholder="Search"></input>
```

- `data-bind-search`: Two-way data binding for search input
- Automatically updates `$search` signal for reactive filtering

### 4. Dynamic Champion Grid

**Reactive Champion Display**

```python
f'''<div id="{name}"
class="legend {'nope' if name in picks.values() else ''}"
data-show="($filter == 'all' || $filter == {'|| $filter == '.join(f"'{role}'" for role in champ['role'])})
&& ($search == '' || '{name}'.toLowerCase().includes($search.toLowerCase()))">'''
```

**Advanced Filtering Logic**:

- **Multi-Role Support**: Champions can belong to multiple roles (e.g., Yasuo: top/mid)
- **Combined Filters**: Role filter AND search term must both match
- **Case-Insensitive Search**: `toLowerCase()` for user-friendly searching
- **Visual State Management**: `nope` class for already-picked champions

### 5. Champion Selection & State Updates

**Grid-Based Selection**

```html
<div id="legends" data-on-click="@get('/pick/' + event.target.id)"></div>
```

- **Event Delegation**: Single click handler for entire champion grid
- **Dynamic URLs**: Uses `event.target.id` to identify selected champion
- **RESTful Design**: Clean URL pattern for champion selection

**Server-Side Pick Processing**

```python
@app.route('/pick/<legend>')
async def pick(legend):
    # Validate champion isn't already picked
    if legend not in picks.values():
        # Find next available pick slot (0-9 for 10 champion draft)
        for i in range(10):
            if picks[str(i)] == "":
                picks[str(i)] = legend
                break

    # Return updated UI fragment
    html = await drafter()
    return SSE.merge_fragments(fragments=[html], use_view_transition=True)
```

### 6. Reactive Team Composition Display

**Blue Side Rendering**

```python
async def render_side(color, picks):
    if color == "blue":
        for i in [0, 3, 4, 7, 8]:  # Blue team pick order
            if pick_value:
                champ = champs[pick_value]
                html += f'''<div class="pick">
                    <div class="pick-legend" style="background-position: {champ['pos'][0]}px {champ['pos'][1]}px;">
                    </div>
                    <div class="gc">{pick_value}</div>
                </div>'''
```

**Red Side with Reversed Layout**

```python
else:  # red side
    for i in [1, 2, 5, 6, 9]:  # Red team pick order
        html += f'<div class="pick">
            <div class="gc">{pick_value}</div>
            <div class="pick-legend" style="background-position: {champ['pos'][0]}px {champ['pos'][1]}px;">
            </div>
        </div>'
```

**Key Features**:

- **Alternating Draft Order**: Realistic League of Legends pick/ban sequence
- **Sprite Sheet Positioning**: Efficient champion image loading using CSS background-position
- **Mirrored Layouts**: Blue side (left-aligned) vs Red side (right-aligned) visual distinction

### 7. Smooth View Transitions

**Fragment Updates with Animations**

```html
<div id="blue-side" data-view-transition="'slide-right'">
  <div id="red-side" data-view-transition="'slide-left'"></div>
</div>
```

```python
return SSE.merge_fragments(fragments=[html], use_view_transition=True)
```

- **Named Transitions**: Different animations for blue vs red side updates
- **CSS Integration**: Works with CSS `@keyframes` and `::view-transition` pseudo-elements
- **Smooth UX**: No jarring page reloads during champion selection

### 8. Signal-Based State Management

The application uses several reactive signals:

- **`$filter`**: Current role filter ('all', 'top', 'jun', 'mid', 'adc', 'sup')
- **`$search`**: Text search term for champion names
- **Pick State**: Server-managed champion selection state

### 9. Responsive Grid Layouts

**Champion Grid**

```css
#legends {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 0.3rem;
}

.legend {
  width: 48px;
  height: 48px;
  background-image: url("/static/img/champion0.png");
  background-size: 480px 288px;
}
```

**Team Composition**

```css
#main-container {
  display: grid;
  grid-template-columns: 10rem 1fr 10rem;
  gap: 2rem;
}
```

## Key Datastar Patterns Demonstrated

### Complex Conditional Logic

```html
data-show="($filter == 'all' || $filter == 'top' || $filter == 'mid') &&
($search == '' || 'Yasuo'.toLowerCase().includes($search.toLowerCase()))"
```

### Signal Initialization and Management

```html
<div id="picker" data-signals-filter="'all'"></div>
```

### Event Delegation with Dynamic Parameters

```html
data-on-click="@get('/pick/' + event.target.id)"
```

### Reactive Attribute Binding

```html
data-attr-selected="$filter == 'top'"
```

## Running the Application

### Prerequisites

- uv package manager

### Setup with uv

1. **Run the application**:

   ```bash
   uv run main.py
   ```

2. **Access**: Open `http://localhost:5000` in your browser

### Game Flow

1. **Start**: Click "VS AI" to begin a new draft
2. **Filter**: Click role icons to filter champions by position
3. **Search**: Type champion names for quick finding
4. **Draft**: Click champions to add them to the draft in order
5. **Visual Feedback**: Picked champions are grayed out and marked "nope"

## Notable Implementation Details

- **Efficient Asset Loading**: Single sprite sheet for all champion images
- **Session Management**: Game state persistence using TinyDB

## Champion Data Structure

Each champion in `champs.py` includes:

```python
'Yasuo': {
    'pos': [-384, -144],        # Sprite sheet coordinates
    'role': ['top', 'mid']      # Playable positions
}
```
