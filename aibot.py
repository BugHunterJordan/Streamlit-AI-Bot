import streamlit as st
import random

st.set_page_config(page_title="Longshot Dynasty", page_icon="🏈")

st.title("🏈 Longshot Dynasty")

# -----------------------------
# SESSION STATE
# -----------------------------

if "game_started" not in st.session_state:
    st.session_state.game_started = False

if "yard_line" not in st.session_state:
    st.session_state.yard_line = 25

if "yards_to_go" not in st.session_state:
    st.session_state.yards_to_go = 10

if "down" not in st.session_state:
    st.session_state.down = 1

if "log" not in st.session_state:
    st.session_state.log = []

# -----------------------------
# FOOTBALL FIELD
# -----------------------------

def draw_field(yard):

    yard = max(0, min(100, yard))

    st.markdown(
        f"""
        <div style="
        position:relative;
        width:100%;
        height:120px;
        background:#2f8f46;
        border-radius:12px;
        border:4px solid white;
        overflow:hidden;
        ">

        <div style="
        position:absolute;
        left:{yard}%;
        top:50%;
        transform:translate(-50%,-50%);
        font-size:36px;
        transition:left 0.8s ease;
        ">
        🏈
        </div>

        <div style="
        position:absolute;
        bottom:5px;
        width:100%;
        text-align:center;
        color:white;
        font-size:12px;
        ">
        0&nbsp;&nbsp;10&nbsp;&nbsp;20&nbsp;&nbsp;30&nbsp;&nbsp;40&nbsp;&nbsp;50&nbsp;&nbsp;40&nbsp;&nbsp;30&nbsp;&nbsp;20&nbsp;&nbsp;10&nbsp;&nbsp;100
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# COMMENTATOR
# -----------------------------

def commentator(text):

    lines = [
        f"The offense snaps the ball... {text}",
        f"The quarterback reads the defense... {text}",
        f"The crowd holds their breath... {text}",
        f"The offense attacks... {text}",
    ]

    return random.choice(lines)

# -----------------------------
# DICE
# -----------------------------

def roll_dice():

    player = random.randint(1,6) + random.randint(1,6)
    defense = random.randint(1,6) + random.randint(1,6)

    return player, defense

# -----------------------------
# YARD TABLE
# -----------------------------

def yards_from_roll(roll):

    table = {
        7:[1,2,3,4,5],
        6:[4,5,6,7,8],
        8:[4,5,6,7,8],
        5:[6,7,8,9,10],
        9:[6,7,8,9,10],
        4:[8,9,10,11,12],
        10:[8,9,10,11,12],
        3:[15,20,25,30,40],
        11:[15,20,25,30,40]
    }

    if roll in table:
        return random.choice(table[roll])

    return 0

# -----------------------------
# GAME RESET
# -----------------------------

def reset_game():

    st.session_state.game_started = False
    st.session_state.yard_line = 25
    st.session_state.yards_to_go = 10
    st.session_state.down = 1

# -----------------------------
# RUN PLAY
# -----------------------------

def run_play():

    player, defense = roll_dice()

    yards = 0
    result = "No gain"

    if player > defense and defense not in [10,11,12]:

        yards = yards_from_roll(player)

        st.session_state.yard_line += yards
        st.session_state.yards_to_go -= yards

        result = f"Gain of {yards} yards"

    elif defense == 11:

        st.session_state.yard_line -= 10
        result = "Sack! Lost 10 yards"

    elif defense == 10:

        result = "Pass swatted"

    elif defense == 12:

        result = "Pick Six!"

    elif player == 2:

        result = "Interception!"

    if st.session_state.yards_to_go <= 0:

        st.session_state.down = 1
        st.session_state.yards_to_go = 10

        result += " | First Down!"

    else:

        st.session_state.down += 1

    play_call = commentator(result)

    st.session_state.log.append(
        f"""
**🎙 {play_call}**

You rolled **{player}**

Defense rolled **{defense}**

📍 Ball on {st.session_state.yard_line}

Down {st.session_state.down} & {st.session_state.yards_to_go}
"""
    )

    if st.session_state.yard_line >= 100:

        st.session_state.log.append("🏆 TOUCHDOWN! YOU WIN!")
        reset_game()

    elif st.session_state.down > 4:

        st.session_state.log.append("💀 Turnover on downs!")
        reset_game()

# -----------------------------
# START GAME
# -----------------------------

def start_game():

    st.session_state.game_started = True

    st.session_state.log.append(
"""
### Welcome to Longshot Dynasty

Roll the dice to move down the field.

Outroll the defense to gain yards.

Score a touchdown to win!
"""
)

# -----------------------------
# DISPLAY GAME
# -----------------------------

draw_field(st.session_state.yard_line)

for entry in st.session_state.log:

    st.markdown(entry)

# -----------------------------
# AUTO SCROLL
# -----------------------------

st.markdown(
"""
<script>
window.scrollTo(0, document.body.scrollHeight);
</script>
""",
unsafe_allow_html=True
)

# -----------------------------
# INPUT
# -----------------------------

st.divider()

col1, col2 = st.columns([5,1])

with col1:
    user_input = st.text_input(
        "Chat or Play",
        placeholder="Type 'roll' or press the roll button...",
        key="chatbox"
    )

with col2:
    roll_clicked = st.button("🎲 Roll", use_container_width=True)

# -----------------------------
# HANDLE INPUT
# -----------------------------

prompt = None

if roll_clicked:
    prompt = "roll"

elif user_input:
    prompt = user_input.lower()

if prompt:

    if prompt == "roll":

        if not st.session_state.game_started:
            start_game()
        else:
            run_play()

    else:
        st.session_state.log.append("Type **roll** to play the game.")
