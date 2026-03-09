import streamlit as st
import random
import time
import requests
import json

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
        "You are a friendly football AI assistant. "
        "Help the user with football or chat normally.",
        data=st.session_state.messages,
        api_key=st.secrets["apikey"]
    )

    for word in response.split():
        yield word + " "
        time.sleep(0.04)


# -----------------------------
# DICE GAME FUNCTIONS
# -----------------------------

def roll_dice():

    user_roll = random.randint(1,6) + random.randint(1,6)
    ai_roll = random.randint(1,6) + random.randint(1,6)

    return user_roll, ai_roll


def calculate_yards(roll):

    if roll == 7:
        return random.choice([1,2,3,4,5])

    if roll in [6,8]:
        return random.choice([4,5,6,7,8])

    if roll in [5,9]:
        return random.choice([6,7,8,9,10])

    if roll in [4,10]:
        return random.choice([8,9,10,11,12])

    if roll in [3,11]:
        return random.choice([15,20,25,30,40])

    return 0


# -----------------------------
# PAGE SETTINGS
# -----------------------------

st.set_page_config(page_title="AI Football Chat & Play", page_icon="🏈")

st.title("AI Football Chat")

# -----------------------------
# SESSION STATE
# -----------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "game_mode" not in st.session_state:
    st.session_state.game_mode = False

if "yard_line" not in st.session_state:
    st.session_state.yard_line = 25

if "yards_to_go" not in st.session_state:
    st.session_state.yards_to_go = 10

if "down" not in st.session_state:
    st.session_state.down = 1


# -----------------------------
# SHOW LOGO
# -----------------------------

st.image("logo.png", caption="CIT 144 – Longshot Dynasty AI")


# -----------------------------
# DISPLAY CHAT HISTORY
# -----------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -----------------------------
# USER INPUT
# -----------------------------

if prompt := st.chat_input("Ask the AI or type //roll to play Longshot Dynasty"):

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})


    # -----------------------------
    # START GAME MODE
    # -----------------------------

    if prompt == "//roll" and not st.session_state.game_mode:

        st.session_state.game_mode = True

        with st.chat_message("assistant"):
            st.markdown("""

### 🏈 Welcome to Longshot Dynasty!

You are the offense and the AI controls the defense.

Your drive starts on the **25 yard line**, and your goal is to move the ball **75 yards for a touchdown.**

### Rules

• You have **4 downs to gain 10 yards**  
• If you gain 10 yards, you earn a **new first down**  
• If you fail to gain 10 yards in 4 plays, the drive ends  

### How to Play

Type **//roll** to roll the dice.

Both you and the AI will roll **two six-sided dice**.

If your total is higher than the AI's roll, you gain yards based on your roll.

### Special Plays

**12** → Automatic Touchdown  
**2** → Interception (Game Over)

### Defensive Big Plays

AI rolls **12** → Pick Six  
AI rolls **11** → Sack (−10 yards)  
AI rolls **10** → Swatted Pass (No Gain)

Good luck!

Type **//roll** again to run your first play.
""")

        st.stop()


    # -----------------------------
    # GAME PLAY
    # -----------------------------

    if prompt == "//roll" and st.session_state.game_mode:

        user_roll, ai_roll = roll_dice()

        with st.chat_message("assistant"):

            st.write(f"You rolled **{user_roll}**")
            st.write(f"Defense rolled **{ai_roll}**")

            # USER AUTO TD
            if user_roll == 12:

                st.write("🏈 **TOUCHDOWN! You win!**")
                st.session_state.game_mode = False
                st.stop()

            # USER INTERCEPTION
            if user_roll == 2:

                st.write("❌ **Interception! Game Over.**")
                st.session_state.game_mode = False
                st.stop()

            # DEFENSE PICK SIX
            if ai_roll == 12 and user_roll != 12:

                st.write("💥 **Pick Six! Defense scores! You lose.**")
                st.session_state.game_mode = False
                st.stop()

            # SACK
            if ai_roll == 11 and user_roll != 12:

                st.write("🛑 Sack! You lose 10 yards.")
                st.session_state.yard_line -= 10

            # SWAT
            elif ai_roll == 10 and user_roll not in [11,12]:

                st.write("🖐 Swatted pass! No gain.")

            # USER WINS PLAY
            elif user_roll > ai_roll:

                yards = calculate_yards(user_roll)

                st.session_state.yard_line += yards
                st.session_state.yards_to_go -= yards

                st.write(f"📈 You gained **{yards} yards!**")

            else:

                st.write("No gain on the play.")

            # FIRST DOWN
            if st.session_state.yards_to_go <= 0:

                st.write("✅ **First Down!**")
                st.session_state.down = 1
                st.session_state.yards_to_go = 10

            else:

                st.session_state.down += 1

            # TOUCHDOWN CHECK
            if st.session_state.yard_line >= 100:

                st.write("🏈 **Touchdown! You win the game!**")
                st.session_state.game_mode = False
                st.stop()

            # TURNOVER ON DOWNS
            if st.session_state.down > 4:

                st.write("❌ **Turnover on downs! Drive failed.**")
                st.session_state.game_mode = False
                st.stop()

            st.write(f"Ball on the **{st.session_state.yard_line} yard line**")
            st.write(f"Down **{st.session_state.down}** & **{st.session_state.yards_to_go}**")

        st.stop()


    # -----------------------------
    # NORMAL AI CHAT
    # -----------------------------

    if not st.session_state.game_mode:

        with st.chat_message("assistant"):

            response = st.write_stream(response_generator())

        st.session_state.messages.append({"role": "assistant", "content": response})
