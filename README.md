Run the game using `python3 tennis_pong.py`

All arguments are optional:
- `-ballspeed {float}` determines the starting ball speed
- `increment` determines the increase in ball speed after each hit
- `randomness {['gauss'|'uniform']}` determines the type of randomess that is implemented, generated random ball speeds after each hit
- `-speed1 {int}` sets the movement speed of the bottom player
- `-speed2 {int}` sets the movement speed of the top player
- `-handicap1 {['full|half]}` sets the movement boundaries for bottom player
- `-handicap2 {['full|half]}` sets the movement boundaries for top player
- `-p1 {['user'|'basic'|'phanton'|'sentinel'|'titan'|'rival'|'teleporter'|'matrix']}` selects the player/AI for bottom player
- `-p2 {['user'|'basic'|'phanton'|'sentinel'|'titan'|'rival'|'teleporter'|'matrix']}` selects the player/AI for top player
- `-flash` enables flashing the ball target destination for accessibility purposes
- `-court {['ao'|'uso'|'sw'|'rg'|'davis'|'nitto'|'nextgen'|'laver'|'cancun'|'riyadh'|'shanghai']}` sets the court colours to famous ATP/WTA year round tournaments
