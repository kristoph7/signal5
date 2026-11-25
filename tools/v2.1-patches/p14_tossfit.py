import sys
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
a = "const h = $('tzHead'); h.textContent = iAmA ? 'YOU GO FIRST' : esc(opp).toUpperCase() + ' GOES FIRST'; h.classList.add('pop');"
b = ("const h = $('tzHead'); h.innerHTML = '<span>' + (iAmA ? 'YOU GO FIRST' : esc(opp).toUpperCase() + ' GOES FIRST') + '</span>'; h.classList.add('pop');\n"
     "      { const sp = h.firstChild; let fs = 66; h.style.fontSize = fs + 'px'; while (fs > 26 && sp.offsetWidth > h.clientWidth - 70) { fs -= 2; h.style.fontSize = fs + 'px'; } }")
assert s.count(a) == 1; s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s); print('ok')
