import streamlit as st
import random
import time
import requests
import json

# -----------------------------
# PAGE SETTINGS
# -----------------------------
st.set_page_config(page_title="AI Football Chat & Play", page_icon="🏈")

# -----------------------------
# ROLL BUTTON STYLE
# -----------------------------
st.markdown("""
<style>

.roll-button img{
    width:140px;
    transition: transform 0.1s ease;
}

.roll-button img:active{
    transform: scale(0.92);
}

div.stButton > button {
    background: none;
    border: none;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# AI API FUNCTION
# -----------------------------
def ai_ask(prompt, data=None, temperature=0.5, max_tokens=250, model="mistral-small-latest", api_key=None, api_url="https://api.mistral.ai/v1/chat/completions"):

    if api_key is None or api_url is None:
        return "API key missing."

    message = prompt

    if data is not None:
        data_str = json.dumps(data, indent=2)
        message += f"\n\nConversation Context:\n{data_str}"

    payload = {
        "messages": [{"role": "user", "content": message}],
        "temperature": float(temperature),
        "model": model,
        "max_tokens": int(max_tokens)
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.post(api_url, headers=headers, json=payload)

    try:
        response.raise_for_status()
        response_data = response.json()
        return response_data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error: {str(e)}"


# -----------------------------
# STREAMING RESPONSE
# -----------------------------
def response_generator():

    response = ai_ask(
        "You are a friendly football AI assistant.",
        data=st.session_state.messages,
        api_key=st.secrets["apikey"]
    )

    for word in response.split():
        yield word + " "
        time.sleep(0.04)


# -----------------------------
# GAME FUNCTIONS
# -----------------------------
def roll_dice():

    player_die1 = random.randint(1,6)
    player_die2 = random.randint(1,6)

    ai_die1 = random.randint(1,6)
    ai_die2 = random.randint(1,6)

    player_total = player_die1 + player_die2
    ai_total = ai_die1 + ai_die2

    return [player_die1,player_die2],player_total,[ai_die1,ai_die2],ai_total


def calculate_yards(roll):

    if roll == 7: return random.choice([1,2,3,4,5])
    if roll in [6,8]: return random.choice([4,5,6,7,8])
    if roll in [5,9]: return random.choice([6,7,8,9,10])
    if roll in [4,10]: return random.choice([8,9,10,11,12])
    if roll in [3,11]: return random.choice([15,20,25,30,40])

    return 0


# -----------------------------
# DICE ANIMATION
# -----------------------------
def animate_dice(final_rolls,label,dice_type="user",width=60,speed=0.1,frames=6):

    st.write(f"🎲 {label} rolled:")

    cols = st.columns(len(final_rolls))

    for i,final_value in enumerate(final_rolls):

        placeholder = cols[i].empty()

        for _ in range(frames):

            rand_val = random.randint(1,6)

            if dice_type == "user":
                placeholder.image(f"userdice{rand_val}.png",width=width)
            else:
                placeholder.image(f"aidice{rand_val}.png",width=width)

            time.sleep(speed)

        if dice_type == "user":
            placeholder.image(f"userdice{final_value}.png",width=width)
        else:
            placeholder.image(f"aidice{final_value}.png",width=width)


# -----------------------------
# FIELD DISPLAY
# -----------------------------
def display_yard_line(yard_line):

    if yard_line < 50:
        return f"your {yard_line} yard line"

    elif yard_line == 50:
        return "50 yard line"

    elif yard_line < 100:
        return f"opponent's {100-yard_line} yard line"

    else:
        return "Touchdown!"


# -----------------------------
# RESET GAME
# -----------------------------
def reset_game():

    st.session_state.game_mode=False
    st.session_state.yard_line=25
    st.session_state.yards_to_go=10
    st.session_state.down=1


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
# TITLE + LOGO
# -----------------------------
st.title("AI Football Chat & Play")

st.image("logo.png",caption="Longshot Dynasty")


# -----------------------------
# ROLL BUTTON
# -----------------------------
roll_button = st.button("ROLL", use_container_width=True)


# -----------------------------
# CHAT HISTORY
# -----------------------------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# -----------------------------
# CHAT INPUT
# -----------------------------
prompt = st.chat_input("Ask the AI or type roll to play Longshot Dynasty")

if roll_button:
    prompt = "roll"


# -----------------------------
# USER INPUT
# -----------------------------
if prompt:

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role":"user","content":prompt})

    prompt_clean = prompt.strip().lower()


    # -----------------------------
    # START GAME
    # -----------------------------
    if prompt_clean=="roll" and not st.session_state.game_mode:

        st.session_state.game_mode=True

        with st.chat_message("assistant"):

            st.markdown("""
### 🏈 Welcome to Longshot Dynasty!

Your drive starts on the **25 yard line**

Goal: **score a touchdown**

### Rules

• 4 downs to gain 10 yards  
• First down resets downs  
• Must **outroll defense** to gain yards

Special Rolls

12 → TD  
2 → Interception  

Defense

12 → Pick Six  
11 → Sack  
10 → Swatted Pass
""")

        st.stop()


    # -----------------------------
    # GAME PLAY
    # -----------------------------
    if prompt_clean=="roll" and st.session_state.game_mode:

        player_dice,user_roll,ai_dice,ai_roll = roll_dice()

        with st.chat_message("assistant"):

            animate_dice(player_dice,"You","user")

            time.sleep(0.5)

            animate_dice(ai_dice,"Defense","ai")

            yards_gained=0

            if user_roll>ai_roll and ai_roll not in [10,11,12]:

                yards_gained=calculate_yards(user_roll)

                st.session_state.yard_line += yards_gained
                st.session_state.yards_to_go -= yards_gained

            elif ai_roll==11:

                yards_gained=-10
                st.session_state.yard_line -=10


            if user_roll==12 or st.session_state.yard_line>=100:

                st.balloons()

                st.markdown(
                "<h1 style='text-align:center;color:gold;font-size:80px;'>🏆 YOU WON 🏆</h1>",
                unsafe_allow_html=True
                )

                st.image("trophy.png",width=300)

                reset_game()

                st.stop()


            if st.session_state.yards_to_go<=0:

                st.session_state.down=1
                st.session_state.yards_to_go=10

                st.markdown("**✅ FIRST DOWN!**")

            else:

                st.session_state.down+=1

                if st.session_state.down>4:

                    st.markdown(
                    "<h1 style='text-align:center;color:red;font-size:70px;'>💀 YOU'VE LOST! TRY AGAIN 💀</h1>",
                    unsafe_allow_html=True
                    )

                    reset_game()

                    st.stop()


            st.markdown(
                f"🏈 You rolled: {user_roll}\n\n"
                f"🛡 Defense rolled: {ai_roll}\n\n"
                f"📍 Ball on: {display_yard_line(st.session_state.yard_line)}\n\n"
                f"Down: {st.session_state.down} & {st.session_state.yards_to_go}"
            )

        st.stop()


    # -----------------------------
    # NORMAL AI CHAT
    # -----------------------------
    if not st.session_state.game_mode:

        with st.chat_message("assistant"):

            response = st.write_stream(response_generator())

        st.session_state.messages.append({"role":"assistant","content":response})
