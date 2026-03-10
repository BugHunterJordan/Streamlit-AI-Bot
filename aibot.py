import streamlit as st
import random
import time
import requests
import json

st.set_page_config(page_title="Longshot Dynasty", page_icon="🏈")

st.title("🏈 Longshot Dynasty")

# -----------------------------
# FIELD VISUALIZATION
# -----------------------------

def draw_field(yard_line):

    yard = max(0, min(100, yard_line))

    st.markdown(
        f"""
        <div style="
        position:relative;
        width:100%;
        height:120px;
        background:#1e7f3f;
        border:4px solid white;
        border-radius:12px;
        overflow:hidden;
        ">

        <div style="
        position:absolute;
        left:{yard}%;
        top:45%;
        transform:translate(-50%,-50%);
        font-size:36px;
        transition:left 0.7s ease;
        ">
        🏈
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------
# AI COMMENTATOR
# -----------------------------

def commentator(play_result, yards):

    lines = [
        f"The offense runs the play... {play_result}",
        f"The quarterback drops back... {play_result}",
        f"The crowd watches closely... {play_result}",
        f"The offense attacks the defense... {play_result}",
    ]

    return random.choice(lines)

# -----------------------------
# DICE FUNCTIONS
# -----------------------------

def roll_dice():

    p1=random.randint(1,6)
    p2=random.randint(1,6)

    a1=random.randint(1,6)
    a2=random.randint(1,6)

    return [p1,p2],p1+p2,[a1,a2],a1+a2


def calculate_yards(roll):

    if roll==7: return random.choice([1,2,3,4,5])
    if roll in [6,8]: return random.choice([4,5,6,7,8])
    if roll in [5,9]: return random.choice([6,7,8,9,10])
    if roll in [4,10]: return random.choice([8,9,10,11,12])
    if roll in [3,11]: return random.choice([15,20,25,30,40])

    return 0

# -----------------------------
# SESSION STATE
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages=[]

if "game_mode" not in st.session_state:
    st.session_state.game_mode=False

if "yard_line" not in st.session_state:
    st.session_state.yard_line=25

if "yards_to_go" not in st.session_state:
    st.session_state.yards_to_go=10

if "down" not in st.session_state:
    st.session_state.down=1


# -----------------------------
# DISPLAY CHAT
# -----------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# -----------------------------
# GAME PLAY
# -----------------------------

def run_play():

    player_dice,user_roll,ai_dice,ai_roll=roll_dice()

    yards_gained=0

    if user_roll>ai_roll and ai_roll not in [10,11,12]:

        yards_gained=calculate_yards(user_roll)

        st.session_state.yard_line+=yards_gained
        st.session_state.yards_to_go-=yards_gained

    elif ai_roll==11:

        yards_gained=-10
        st.session_state.yard_line-=10


    if user_roll==12 or st.session_state.yard_line>=100:
        result=f"🏈 TOUCHDOWN! (+{yards_gained} yards)"

    elif user_roll==2:
        result="❌ Interception!"

    elif ai_roll==12:
        result="💥 Pick Six!"

    elif ai_roll==11:
        result="🛑 Sack! Lost 10 yards."

    elif ai_roll==10:
        result="🖐 Swatted pass!"

    elif user_roll>ai_roll:
        result=f"📈 Gain of {yards_gained} yards"

    else:
        result="No gain"


    if st.session_state.yards_to_go<=0:

        st.session_state.down=1
        st.session_state.yards_to_go=10

        first_down="✅ First Down!"

    else:

        st.session_state.down+=1
        first_down=""


    commentary=commentator(result,yards_gained)

    with st.chat_message("assistant"):

        draw_field(st.session_state.yard_line)

        st.markdown(f"""
### 🎙 Commentary
{commentary}

---

**{result}**

🏈 You rolled **{user_roll}**

🛡 Defense rolled **{ai_roll}**

📍 Ball on **{st.session_state.yard_line} yard line**

**Down {st.session_state.down} & {st.session_state.yards_to_go}**
""")

        if first_down:
            st.success(first_down)


    if st.session_state.yard_line>=100:

        st.balloons()

        st.markdown(
        "<h1 style='text-align:center;color:gold;'>🏆 TOUCHDOWN YOU WIN 🏆</h1>",
        unsafe_allow_html=True
        )

        reset_game()

    if st.session_state.down>4:

        st.markdown(
        "<h1 style='text-align:center;color:red;'>💀 TURNOVER ON DOWNS 💀</h1>",
        unsafe_allow_html=True
        )

        reset_game()


def reset_game():

    st.session_state.game_mode=False
    st.session_state.yard_line=25
    st.session_state.yards_to_go=10
    st.session_state.down=1


# -----------------------------
# START GAME
# -----------------------------

def start_game():

    st.session_state.game_mode=True

    with st.chat_message("assistant"):

        st.markdown("""
### Welcome to Longshot Dynasty

Roll the dice to advance the ball.

You must outroll the defense to gain yards.

Reach the endzone to win.

Press **Roll 🎲** to start.
""")


# -----------------------------
# INPUT BAR (BOTTOM)
# -----------------------------

st.divider()

col1,col2=st.columns([5,1])

with col1:
    prompt=st.text_input(
        "Chat or Play",
        placeholder="Ask something or press Roll...",
        key="chatbox"
    )

with col2:
    roll_clicked=st.button("🎲 Roll",use_container_width=True)

if roll_clicked:
    prompt="roll"
    st.session_state.chatbox=""

# -----------------------------
# HANDLE INPUT
# -----------------------------

if prompt:

    prompt_clean=prompt.lower().strip()

    if prompt_clean=="roll":

        if not st.session_state.game_mode:

            start_game()

        else:

            run_play()

    else:

        with st.chat_message("assistant"):

            st.write("I'm your football assistant! Type roll to play.")
