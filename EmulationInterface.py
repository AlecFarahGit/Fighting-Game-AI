import time
import subprocess
from torch.utils.tensorboard import SummaryWriter

'''Creates graqphs with data associated to the AI's success. Pipes data from the AI to the game and
 also allows the AI to see data from the emulator. Holds functions which start the training process, resets the environment
 and pushes the AI to the next frame of the environment'''
def initialize():
    open(r'nesgym-pipe-out', 'w').close()
    open(r'nesgym-pipe-in', 'w').close()
    global proc
    global file
    global filein
    global writer
    writer = SummaryWriter()
    args = [r'C:\Users\Alec\Downloads\fceux-2.6.6-win64\fceux64.exe', '-lua', "Luafiles.lua", "Game.nes"]
    proc = subprocess.Popen(' '.join(args))
    file = open(r'nesgym-pipe-out', 'w', buffering=1)
    filein = open(r'nesgym-pipe-in', 'rb', buffering=0)


games = 0
framenum = 0
total_reward = 0
stocks_taken=0

def envreset():
    #increases the game count by one, tells the emulator to reset, writes data like length, reward and stocks to the tensor board and resets culmulative reward, percent and framenumber to zero
    global file
    global filein
    global framenum
    global stock
    global percent
    global total_reward
    global stocks_taken
    global games
    games += 1

    writer.add_scalar("Length", framenum, games)
    writer.add_scalar("Reward", total_reward, games)
    writer.add_scalar("Stocks", stocks_taken, games)
    writer.flush()
    total_reward = 0
    percent = 0
    framenum = 0
    file.write("reset")

    file.flush()

    while True:
        pipe_content = filein.readline()
        if pipe_content !=  b"":
            pipe_data = pipe_content.decode('utf-8').split(',')
            state = [int(pipe_data[0]),int(pipe_data[1]),int(pipe_data[2]),int(pipe_data[3]),int(pipe_data[4]),int(pipe_data[5]),int(pipe_data[6]),int(pipe_data[7]),int(pipe_data[8]),int(pipe_data[9])]
            stock = state[9]
            return state

def envstep(action):
    #tells the AI do a new input for every new frame of the game and also controls what reward is given for the frame
    global file
    global filein
    global framenum
    global stock
    global percent
    global total_reward
    global stocks_taken

    framenum += 1
    actions = ['U', 'D', 'L', 'R',
        'UR', 'DR', 'URA', 'DRB',
        'A', 'B', 'RB', 'RA','UL', 'DL', 'ULA', 'DLB',
        'LB', 'LA']

    file.write("joypad"+ '|' + actions[action])

    file.flush()

    while True:
        pipe_content = filein.readline()
        if pipe_content !=  b"":
            pipe_data = pipe_content.decode('utf-8').split(',')
            state = [int(pipe_data[0]),int(pipe_data[1]),int(pipe_data[2]),int(pipe_data[3]),int(pipe_data[4]),int(pipe_data[5]),int(pipe_data[6]),int(pipe_data[7]),int(pipe_data[8]),int(pipe_data[9])]
            break
    percent = state[7]
    stock = state[9]
    reward = .00015
    if state[0] == 2:
        print("player 1 lost")
        print(f"the total reward was {total_reward}")
    elif state[1] == 2:
        print("player 2 lost")
        stock = -1
    if stock == 4:
        reward += .015
    elif stock == 3:
        reward += .11
    elif stock == 2:
        reward += .55
    elif stock == 1:
        reward += .85
    elif stock == 0:
        reward = 1
    if state[1] ==2:
        reward = 1
    if state[3] < 80:
        reward = 0
    stocks_taken = stock

    end = False


    if state[0] == 2  or state[1] == 2:
        end = True
    timeout = False

    if framenum == 3600:
        timeout == True

    total_reward += reward

    return state, reward, end, timeout

