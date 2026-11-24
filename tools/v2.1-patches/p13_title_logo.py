import sys, re, base64, os
p = sys.argv[1]; s = open(p, encoding='utf-8').read()
assert s.count('<title>Signal 5 Prototype</title>') == 1
s = s.replace('<title>Signal 5 Prototype</title>', '<title>SIGNAL 5 - RVI</title>')
b64 = base64.b64encode(open(os.path.join(os.path.dirname(__file__), 'assets/teampura.webp'), 'rb').read()).decode()
s, n = re.subn(r"'teampura':'data:image/webp;base64,[^']+'", lambda m: "'teampura':'data:image/webp;base64," + b64 + "'", s)
assert n == 1
for k in ('menu_main', 'load_main'):
    d = base64.b64encode(open(os.path.join(os.path.dirname(__file__), 'assets/%s_new.webp' % k), 'rb').read()).decode()
    s, n = re.subn(r"'%s':'data:image/webp;base64,[^']+'" % k, lambda m: "'%s':'data:image/webp;base64,%s'" % (k, d), s)
    assert n == 1, k
open(p, 'w', encoding='utf-8').write(s); print('ok')
