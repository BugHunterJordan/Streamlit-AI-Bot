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
# CSS FOR ROLL BUTTON IMAGE
# -----------------------------
st.markdown("""
<style>
.roll-btn img {
    width: 120px;
    cursor: pointer;
    transition: transform 0.08s ease;
}
.roll-btn img:active {
    transform: scale(0.9);
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# AI API FUNCTION
# -----------------------------
def ai_ask(prompt, data=None, temperature=0.5, max_tokens=250,
           model="mistral-small-latest",
           api_key=None,
           api_url="https://api.mistral.ai/v1/chat/completions"):

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
# STREAM RESPONSE
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
    return [player_die1,player_die2], player_die1+player_die2, [ai_die1,ai_die2], ai_die1+ai_die2

def calculate_yards(roll):
    if roll==7: return random.choice([1,2,3,4,5])
    if roll in [6,8]: return random.choice([4,5,6,7,8])
    if roll in [5,9]: return random.choice([6,7,8,9,10])
    if roll in [4,10]: return random.choice([8,9,10,11,12])
    if roll in [3,11]: return random.choice([15,20,25,30,40])
    return 0

def animate_dice(final_rolls,label,dice_type="user",width=60,speed=0.1,frames=6):
    st.write(f"🎲 {label} rolled:")
    cols = st.columns(len(final_rolls))
    for i,val in enumerate(final_rolls):
        placeholder = cols[i].empty()
        for _ in range(frames):
            rand = random.randint(1,6)
            if dice_type=="user":
                placeholder.image(f"userdice{rand}.png",width=width)
            else:
                placeholder.image(f"aidice{rand}.png",width=width)
            time.sleep(speed)
        if dice_type=="user":
            placeholder.image(f"userdice{val}.png",width=width)
        else:
            placeholder.image(f"aidice{val}.png",width=width)

def display_yard_line(y):
    if y<50: return f"your {y} yard line"
    if y==50: return "50 yard line"
    if y<100: return f"opponent's {100-y} yard line"
    return "Touchdown!"

def reset_game():
    st.session_state.game_mode=False
    st.session_state.yard_line=25
    st.session_state.yards_to_go=10
    st.session_state.down=1

# -----------------------------
# SESSION STATE
# -----------------------------
if "messages" not in st.session_state: st.session_state.messages=[]
if "game_mode" not in st.session_state: st.session_state.game_mode=False
if "yard_line" not in st.session_state: st.session_state.yard_line=25
if "yards_to_go" not in st.session_state: st.session_state.yards_to_go=10
if "down" not in st.session_state: st.session_state.down=1
if "roll_click" not in st.session_state: st.session_state.roll_click=False

# -----------------------------
# TITLE + LOGO
# -----------------------------
st.title("AI Football Chat & Play")
st.image("logo.png", caption="Longshot Dynasty")

# -----------------------------
# CHAT HISTORY
# -----------------------------
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# -----------------------------
# FUNCTION FOR CLICKABLE ROLL BUTTON USING SESSION STATE
# -----------------------------
def roll_button():
    clicked = False
    # Render HTML button with image
    st.markdown("""
    <div class="roll-btn">
        <form action="." method="post">
            <button type="submit" name="roll" value="1" style="all:unset;">
                <img src="roll.png">
            </button>
        </form>
    </div>
    """, unsafe_allow_html=True)
    # Check session state
    if st.session_state.roll_click:
        clicked = True
        st.session_state.roll_click = False
    return clicked

# -----------------------------
# CHAT INPUT
# -----------------------------
prompt = st.chat_input("Ask the AI or type roll to play Longshot Dynasty")

# Normal "roll" via button
if st.button("roll"):
    st.session_state.roll_click = True

# If roll button clicked, treat as "roll"
if st.session_state.roll_click or (prompt and prompt.strip().lower()=="roll"):
    prompt = "roll"

# -----------------------------
# USER INPUT HANDLING
# -----------------------------
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role":"user","content":prompt})
    p = prompt.strip().lower()

    # START GAME
    if p=="roll" and not st.session_state.game_mode:
        st.session_state.game_mode=True
        with st.chat_message("assistant"):
            st.markdown("""
### 🏈 Welcome to Longshot Dynasty
Start on the **25 yard line**. Score a **touchdown**.

**Rules**
• 4 downs for 10 yards  
• Outroll defense to gain yards  

**Special Rolls**  
12 → TD  
2 → Interception  

**Defense**  
12 → Pick Six  
11 → Sack  
10 → Swatted Pass
""")
        st.stop()

    # GAMEPLAY
    if p=="roll" and st.session_state.game_mode:
        pd, ur, ad, ar = roll_dice()
        with st.chat_message("assistant"):
            animate_dice(pd,"You","user")
            time.sleep(0.5)
            animate_dice(ad,"Defense","ai")

            yards_gained = 0
            if ur>ar and ar not in [10,11,12]:
                yards_gained = calculate_yards(ur)
                st.session_state.yard_line += yards_gained
                st.session_state.yards_to_go -= yards_gained
            elif ar==11:
                yards_gained=-10
                st.session_state.yard_line -=10

            if ur==12 or st.session_state.yard_line>=100:
                st.balloons()
                st.markdown("<h1 style='text-align:center;color:gold;font-size:80px;'>🏆 YOU WON</h1>", unsafe_allow_html=True)
                st.image("trophy.png", width=300)
                reset_game()
                st.stop()

            if st.session_state.yards_to_go <= 0:
                st.session_state.down=1
                st.session_state.yards_to_go=10
                st.markdown("**✅ FIRST DOWN**")
            else:
                st.session_state.down += 1
                if st.session_state.down>4:
                    st.markdown("<h1 style='text-align:center;color:red;font-size:70px;'>💀 YOU'VE LOST</h1>", unsafe_allow_html=True)
                    reset_game()
                    st.stop()

            # Display result
            st.markdown(f"🏈 You rolled: {ur}\n🛡 Defense rolled: {ar}\n📍 Ball: {display_yard_line(st.session_state.yard_line)}\nDown: {st.session_state.down} & {st.session_state.yards_to_go}")

            # SHOW ROLL BUTTON AGAIN BELOW DOWN & DISTANCE
            if roll_button():
                st.session_state.roll_click = True
                st.experimental_rerun()

    # NORMAL AI CHAT
    if not st.session_state.game_mode:
        with st.chat_message("assistant"):
            response = st.write_stream(response_generator())
        st.session_state.messages.append({"role":"assistant","content":response})
