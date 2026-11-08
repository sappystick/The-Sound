# Follow-up to john_miniature.py: the NT step-by-step test under three ancient NT orders.
# Usage: python3 john_miniature_nt_orders.py <sblgnt dir> <lxx-swete/data>
import sys, runpy, numpy as np
sys.argv=["x",sys.argv[1],sys.argv[2]]
src=open("/home/user/sound-of-the-word/analysis/john_miniature.py").read().split("# ---------------------------------------------------------------- 1.")[0]
g={"__file__":"/home/user/sound-of-the-word/analysis/john_miniature.py"}; exec(src,g)
parts=None
def parts(ws,k):
    S=[g["syl"](w) for _,_,_,w in ws];T=sum(S);acc=0;seg=[[] for _ in range(k)];lab=[None]*k
    for (b,c,v,w),s in zip(ws,S):
        i=min(k-1,int(k*acc/T));seg[i].append(w);lab[i]=lab[i] or f"{b} {c}";acc+=s
    return seg,lab
B=g["B"];vec=g["vec"];cos=g["cos"];JCH=g["JCH"]
NTO="Mt Mk Lk Ac Ro 1Co 2Co Ga Eph Php Col 1Th 2Th 1Ti 2Ti Tit Phm Heb Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud Re".split()
SIN="Mt Mk Lk Ro 1Co 2Co Ga Eph Php Col 1Th 2Th Heb 1Ti 2Ti Tit Phm Ac Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud Re".split()
ALX="Mt Mk Lk Ac Jas 1Pe 2Pe 1Jn 2Jn 3Jn Jud Ro 1Co 2Co Ga Eph Php Col 1Th 2Th Heb 1Ti 2Ti Tit Phm Re".split()
rng=np.random.default_rng(5)
for lab,o in (("modern",NTO),("Sinaiticus",SIN),("Alexandrinus",ALX)):
    ws=[(b,c,v,w) for b in o for (c,v,w) in B[b]];seg,starts=parts(ws,21)
    M=np.array([[cos(vec(s),j) for j in JCH] for s in seg]);M=(M-M.mean(0))/(M.std(0)+1e-9)
    real=np.trace(M);null=[M[rng.permutation(21),range(21)].sum() for _ in range(5000)]
    print(lab,round(real,2),"p",np.mean(np.array(null)>=real))
    if lab=="modern": print("  top diagonal:",sorted([(round(M[k,k],2),f"part {k+1} ({starts[k]}) ~ John {k+1}") for k in range(21)],reverse=True)[:6])
