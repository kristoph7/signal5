import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (a[:70], c); s = s.replace(a, b)
rep("`⚡ Quick Match · 6 rounds · Balanced vs Balanced<br>Player A moves first every round (no halftime switch).`", "`⚡ Quick Match · 6 rounds<br>Player A moves first every round.`")
rep("`Pass & Play · 6 rounds<br>Player A moves first every round (no halftime switch).`", "`Pass & Play · 6 rounds<br>Player A moves first every round.`")
open(p, 'w', encoding='utf-8').write(s); print('ok')
