import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
def rep(a, b, n=1):
    global s
    c = s.count(a); assert c == n, (a[:70], c); s = s.replace(a, b)
# v2.2: the Construction Office never goes offline for lack of power (its crew works by hand).
# Before, a burning/destroyed Hall with no working Substation switched it off -> 0 worker actions -> no way to rebuild.
rep("    v.tiles.forEach((b, i) => { if (alive(b) && def(b).power) { demand += def(b).power; users.push(i); } });",
    "    v.tiles.forEach((b, i) => { if (alive(b) && def(b).power) { demand += def(b).power; if (b.type !== 'cons') users.push(i); } });")
rep("    desc: 'Each Construction Worker gives 1 worker action per turn: build, upgrade, repair, or add walls and drains.',",
    "    desc: 'Each Construction Worker gives 1 worker action per turn: build, upgrade, repair, rebuild, or add walls and drains. Keeps working during a blackout.',")
open(p, 'w', encoding='utf-8').write(s); print('ok')
