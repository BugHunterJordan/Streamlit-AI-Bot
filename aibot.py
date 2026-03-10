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
# BUTTON STYLE
# -----------------------------
st.markdown("""
<style>

.roll-button button {
    background: none;
    border: none;
    padding: 0;
}

.roll-button img {
    width:140px;
    transition: transform .08s ease;
    cursor:pointer;
}

.roll-button img:active {
    transform: scale(.9);
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
        time.sleep(.04)

# -----------------------------
# GAME FUNCTIONS
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
# DICE ANIMATION
# -----------------------------
def animate_dice(final_rolls,label,dice_type="user",width=60,speed=.1,frames=6):

    st.write(f"🎲 {label} rolled:")

    cols = st.columns(len(final_rolls))

    for i,value in enumerate(final_rolls):

        placeholder = cols[i].empty()

        for _ in range(frames):

            rand=random.randint(1,6)

            if dice_type=="user":
                placeholder.image(f"userdice{rand}.png",width=width)
            else:
                placeholder.image(f"aidice{rand}.png",width=width)

            time.sleep(speed)

        if dice_type=="user":
            placeholder.image(f"userdice{value}.png",width=width)
        else:
            placeholder.image(f"aidice{value}.png",width=width)

# -----------------------------
# FIELD DISPLAY
# -----------------------------
def display_yard_line(y):

    if y<50: return f"your {y} yard line"
    if y==50: return "50 yard line"
    if y<100: return f"opponent's {100-y} yard line"

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
# CHAT HISTORY
# -----------------------------
for m in st.session_state.messages:

    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# -----------------------------
# ROLL IMAGE BUTTON (BOTTOM)
# -----------------------------
st.markdown('<div class="roll-button">', unsafe_allow_html=True)

roll_clicked = st.button("roll_button")

st.image("roll.png")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# CHAT INPUT
# -----------------------------
prompt = st.chat_input("Ask the AI or type roll to play Longshot Dynasty")

if roll_clicked:
    prompt="roll"

# -----------------------------
# USER INPUT
# -----------------------------
if prompt:

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({"role":"user","content":prompt})

    p = prompt.strip().lower()

    # -----------------------------
    # START GAME
    # -----------------------------
    if p=="roll" and not st.session_state.game_mode:

        st.session_state.game_mode=True

        with st.chat_message("assistant"):

            st.markdown("""
### 🏈 Welcome to Longshot Dynasty

Start on the **25 yard line**

Score a **touchdown**

Rules

• 4 downs for 10 yards  
• Outroll defense to gain yards  

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
    if p=="roll" and st.session_state.game_mode:

        pd,ur,ad,ar = roll_dice()

        with st.chat_message("assistant"):

            animate_dice(pd,"You","user")

            time.sleep(.5)

            animate_dice(ad,"Defense","ai")

            yards=0

            if ur>ar and ar not in [10,11,12]:

                yards=calculate_yards(ur)

                st.session_state.yard_line+=yards
                st.session_state.yards_to_go-=yards

            elif ar==11:

                yards=-10
                st.session_state.yard_line-=10

            if ur==12 or st.session_state.yard_line>=100:

                st.balloons()

                st.markdown(
                "<h1 style='text-align:center;color:gold;font-size:80px;'>🏆 YOU WON</h1>",
                unsafe_allow_html=True
                )

                st.image("trophy.png",width=300)

                reset_game()
                st.stop()

            if st.session_state.yards_to_go<=0:

                st.session_state.down=1
                st.session_state.yards_to_go=10
                st.markdown("**✅ FIRST DOWN**")

            else:

                st.session_state.down+=1

                if st.session_state.down>4:

                    st.markdown(
                    "<h1 style='text-align:center;color:red;font-size:70px;'>💀 YOU'VE LOST</h1>",
                    unsafe_allow_html=True
                    )

                    reset_game()
                    st.stop()

            st.markdown(
                f"🏈 You rolled: {ur}\n\n"
                f"🛡 Defense rolled: {ar}\n\n"
                f"📍 Ball: {display_yard_line(st.session_state.yard_line)}\n\n"
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
