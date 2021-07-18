### _How does a person learn?_
### By doing the thing it wants to learn!

Famous quote:  
> If you do something for 1.000 hours, you will become good in it.

# Chess (-student) implemented using pygame

This project will be used to train a model using deep reinforcement learning (deep RL) based on opponents play.  
Nevertheless, the game can be played in multi-player mode without fancy ML features.

The project will eventually contain the following features (ticked ones implemented)
- [ ] complete chess game
- [ ] history log and game loading

- [ ] deep learning reinforced model
- [ ] trained example model
- [ ] payable against trained model
- [ ] can train own model based on **your** moves!


## Interesting problems to analyze
### How would the model behave in such situation:
- King on `e1`, Pawn `e2` moves up until `e8` and gets promoted into Rook
    - Enable underpromoted Rook castling using `Game(underpromoted_castling=True)`


### Usage:
clone the project
```shell
git clone git@github.com:philsupertramp/chess
```

Install requirements
```shell
pip install -r requirements.txt
```

Run the game in 2P mode
```shell
python main.py
```

## Development

clone the repository and install the dependencies as described before.

### Note:
- Do not, and I repeat **not** use Pawn-d4 as a first step for testing. **This pawn is on the (4,4)-tile and will always work!**

## Demo


https://user-images.githubusercontent.com/9550040/126046245-74f7ed12-d695-4153-b909-2535f48e3706.mp4
