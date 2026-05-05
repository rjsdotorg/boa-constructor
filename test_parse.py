import sys, wx
app = wx.App(False)
import moduleparse, methodparse, sourceconst
from Views import ObjCollection

src = open(r'C:\Users\rjs\Documents\GitHub\visual-phaser\VP_Config_GUI_Boa.py', encoding='utf-8').read()
lines = src.split('\n')
mod = moduleparse.Module('VP_Config_GUI_Boa', lines)
cls = mod.classes['VPConfigBoaFrame']

# Simulate identifyCollectionMethods
results = [meth for meth in cls.methods.keys() if len(meth) > 6 and meth[:6] == '_init_']
print('collection methods:', results)
print()

# Simulate readComponents for each method
for oc in results:
    codeSpan = cls.methods[oc]
    codeBody = mod.source[codeSpan.start : codeSpan.end]
    try:
        if ObjCollection.isInitCollMeth(oc):
            ctrlName = methodparse.ctrlNameFromMeth(oc)
            allInitialisers, unmatched = methodparse.parseMixedBody(
                [methodparse.EventParse, methodparse.CollectionItemInitParse], codeBody)
            creators = allInitialisers.get(methodparse.CollectionItemInitParse, [])
        else:
            allInitialisers, unmatched = methodparse.parseMixedBody(
                [methodparse.ConstructorParse, methodparse.EventParse,
                 methodparse.CollectionInitParse, methodparse.PropertyParse],
                codeBody)
            creators = allInitialisers.get(methodparse.ConstructorParse, [])
        n_unmatched = len(unmatched) if unmatched else 0
        print(f'{oc}: creators={len(creators)} unmatched={n_unmatched}')
        if n_unmatched:
            for u in unmatched[:5]:
                print(f'    UNMATCHED: {u!r}')
    except Exception as e:
        import traceback
        print(f'ERROR in {oc}:')
        traceback.print_exc()

print()
print('--- readSpecialAttrs test ---')
try:
    initMeth = cls.methods['__init__']
    for idx in range(initMeth.start, initMeth.end):
        line = mod.source[idx].strip()
        if line.startswith('self._init_ctrls('):
            print(f'Found _init_ctrls call at line {idx}: {line!r}')
            break
    else:
        print('ERROR: self._init_ctrls not found in __init__')
except Exception as e:
    import traceback
    traceback.print_exc()

print()
print('--- window ID regex test ---')
import re
reWinIds = re.compile(sourceconst.srchWindowIdsCont % sourceconst.init_ctrls)
for i, line in enumerate(mod.source):
    m = reWinIds.match(line)
    if m or 'NewIdRef' in line:
        print(f'  line {i}: match={bool(m)!r}  {line!r}')
        break
