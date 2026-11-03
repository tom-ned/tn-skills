#!/usr/bin/env python3
"""build_xlsx.py - classeur Excel pure data du rapport mensuel 3-en-1 (charte Suisseo).
Entree : report_data.json (prepare_data.py). Sortie : --out .xlsx
Onglets crees selon les donnees disponibles.
"""
import argparse, json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import LineChart, Reference
from openpyxl.utils import get_column_letter

DARK="2B3A4E"; GREEN="95C11F"; GREYBG="E8EAED"; GREEN_BG="F0F9E8"; RED_BG="FBE9E7"; WHITE="FFFFFF"
H_FONT=Font(name="Calibri",bold=True,color=WHITE,size=11); H_FILL=PatternFill("solid",fgColor=DARK)
SUB_FILL=PatternFill("solid",fgColor=GREYBG); GAIN=PatternFill("solid",fgColor=GREEN_BG); LOSS=PatternFill("solid",fgColor=RED_BG)
THIN=Side(style="thin",color="CCCCCC"); BORDER=Border(left=THIN,right=THIN,top=THIN,bottom=THIN)
CENTER=Alignment(horizontal="center",vertical="center"); LEFT=Alignment(horizontal="left",vertical="center")
TITLE=Font(name="Calibri",bold=True,color=DARK,size=14); SUBT=Font(name="Calibri",color="666666",size=9)

def hrow(ws,row,headers,widths=None):
    for i,h in enumerate(headers,1):
        c=ws.cell(row=row,column=i,value=h); c.font=H_FONT; c.fill=H_FILL; c.alignment=CENTER; c.border=BORDER
    if widths:
        for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width=w

def cell(ws,r,c,v,bold=False,fill=None,align=None,border=True):
    x=ws.cell(row=r,column=c,value=v); x.font=Font(name="Calibri",bold=bold,color="333333",size=10)
    if fill: x.fill=fill
    if align: x.alignment=align
    if border: x.border=BORDER
    return x

def evol(cur,prev,inv=False):
    if cur is None or prev is None: return "-"
    d=round(cur-prev,1)
    if d==0: return "="
    if inv:  # position: baisse = gain
        return (f"+{-d} places") if d<0 else (f"-{d} places")
    return (f"+{d}") if d>0 else f"{d}"

def sheet_synthese(wb,R):
    m=R["meta"]; ws=wb.active; ws.title="Synthèse"
    ws["A1"]="Reporting SEO mensuel"; ws["A1"].font=TITLE
    ws["A2"]=f"{m.get('client','')} - {m.get('domain','')} - {m.get('language','')} - {m.get('market','')}"; ws["A2"].font=SUBT
    ws["A3"]=f"Période : {m.get('month_name','')} (comparaison M-1 / M-2)"; ws["A3"].font=SUBT
    K=R["kpi"]; M,M1,M2=K.get("M"),K.get("M1"),K.get("M2")
    r=5; hrow(ws,r,["Indicateur","M-2","M-1","M","Évolution M-1>M"],[30,14,14,14,18])
    def line(lbl,key,inv=False,pct=False):
        nonlocal r; r+=1
        vals=[(M2 or {}).get(key),(M1 or {}).get(key),(M or {}).get(key)]
        cell(ws,r,1,lbl,bold=True,fill=SUB_FILL,align=LEFT)
        for i,v in enumerate(vals,2): cell(ws,r,i,(f"{v}%" if pct and v is not None else v),align=CENTER)
        e=evol(vals[2],vals[1],inv=inv)
        c=cell(ws,r,5,e,align=CENTER)
        if isinstance(e,str) and e.startswith("+") and "places" not in e: c.fill=GAIN
        if e.startswith("-") and "places" not in e: c.fill=LOSS
    r=5
    line("Clics","clicks"); line("Impressions","impressions"); line("CTR moyen","ctr",pct=True)
    line("Position moyenne","avg_position",inv=True); line("Requêtes positionnées","queries")
    line("TOP 3","top3"); line("TOP 10","top10")
    line("Clics de marque","brand_clicks"); line("Clics non-marque","nonbrand_clicks")
    line("Part de marque","brand_share",pct=True)
    r+=2
    cell(ws,r,1,"Note : le bloc ci-dessus vient de la dimension requête de Search Console, agrégée au niveau du site.",align=LEFT,border=False)
    ws.cell(row=r,column=1).font=SUBT
    r+=1
    cell(ws,r,1,"Search Console n'associe pas une requête à une langue : la segmentation par langue figure dans le bloc suivant et dans les onglets Par page et GA4.",align=LEFT,border=False)
    ws.cell(row=r,column=1).font=SUBT
    lk=m.get("lang_kpi")
    if lk:
        r+=2
        cell(ws,r,1,f"Périmètre linguistique : {m.get('language','')} (pages {m.get('perimeter_prefix','')})",bold=True,align=LEFT,border=False)
        ws.cell(row=r,column=1).font=TITLE
        r+=1
        hrow(ws,r,["Indicateur","M-2","M-1","M","Évolution M-1>M"],[46,14,14,14,18])
        for lbl,key,inv,pct in [("Clics","clicks",False,False),("Impressions","impressions",False,False),
                                ("CTR moyen","ctr",False,True),("Position moyenne","position",True,False),
                                ("Pages indexées avec impressions","pages",False,False)]:
            r+=1
            vals=[(lk.get("M2") or {}).get(key),(lk.get("M1") or {}).get(key),(lk.get("M") or {}).get(key)]
            cell(ws,r,1,lbl,bold=True,fill=SUB_FILL,align=LEFT)
            for i,v in enumerate(vals,2): cell(ws,r,i,(f"{v}%" if pct and v is not None else v),align=CENTER)
            e=evol(vals[2],vals[1],inv=inv)
            c=cell(ws,r,5,e,align=CENTER)
            if isinstance(e,str) and e.startswith("+") and "places" not in e: c.fill=GAIN
            if isinstance(e,str) and e.startswith("-") and "places" not in e: c.fill=LOSS
        r+=2
        cell(ws,r,1,"Source : Search Console, dimension langue (préfixe d'URL). Données réelles, non extrapolées.",align=LEFT,border=False)
        ws.cell(row=r,column=1).font=SUBT
    ck=m.get("ch_kpi")
    if ck:
        r+=2
        cell(ws,r,1,"Marché suisse (Google Switzerland, toutes langues)",bold=True,align=LEFT,border=False)
        ws.cell(row=r,column=1).font=TITLE
        r+=1
        hrow(ws,r,["Indicateur","M-2","M-1","M","Évolution M-1>M"],[46,14,14,14,18])
        for lbl,key,inv,pct in [("Clics depuis la Suisse","clicks",False,False),
                                ("Impressions depuis la Suisse","impressions",False,False),
                                ("CTR moyen","ctr",False,True),("Position moyenne","position",True,False),
                                ("Part des clics du site","share",False,True)]:
            r+=1
            vals=[(ck.get("M2") or {}).get(key),(ck.get("M1") or {}).get(key),(ck.get("M") or {}).get(key)]
            cell(ws,r,1,lbl,bold=True,fill=SUB_FILL,align=LEFT)
            for i,v in enumerate(vals,2): cell(ws,r,i,(f"{v}%" if pct and v is not None else v),align=CENTER)
            e=evol(vals[2],vals[1],inv=inv)
            c=cell(ws,r,5,e,align=CENTER)
            if isinstance(e,str) and e.startswith("+") and "places" not in e: c.fill=GAIN
            if isinstance(e,str) and e.startswith("-") and "places" not in e: c.fill=LOSS
        r+=2
        cell(ws,r,1,"Source : Search Console, dimension pays. Cartograph ne permet pas de filtrer les requêtes par pays : les onglets Requêtes et Opportunités restent au niveau du site.",align=LEFT,border=False)
        ws.cell(row=r,column=1).font=SUBT

def sheet_langues(wb,R):
    langs=(R["meta"].get("langues") or [])
    if not langs: return
    ws=wb.create_sheet("Langues")
    m=R["meta"]
    ws["A1"]="Performance par version linguistique"; ws["A1"].font=TITLE
    ws["A2"]=f"Periode : {m.get('month_name','')} (comparaison {m.get('month_m1','')} et {m.get('month_m2','')})"; ws["A2"].font=SUBT
    hrow(ws,4,["Version","Mois","Clics","Impressions","CTR","Position moyenne","Pages avec impressions","Part du site"],
         [22,14,10,14,10,18,22,14])
    r=4
    for l in langs:
        for key,lbl in (("M2",m.get("month_m2","M-2")),("M1",m.get("month_m1","M-1")),("M",m.get("month_name","M"))):
            k=(l.get("kpi") or {}).get(key) or {}
            if not k: continue
            r+=1
            cell(ws,r,1,f"{l.get('label','')} ({l.get('prefix','')})",bold=(key=="M"),align=LEFT)
            cell(ws,r,2,lbl,align=CENTER)
            cell(ws,r,3,k.get("clicks"),align=CENTER); cell(ws,r,4,k.get("impressions"),align=CENTER)
            cell(ws,r,5,(str(k.get('ctr')).replace(".",",")+" %" if k.get("ctr") is not None else None),align=CENTER)
            cell(ws,r,6,k.get("position"),align=CENTER); cell(ws,r,7,k.get("pages"),align=CENTER)
            cell(ws,r,8,(str(k.get('share')).replace(".",",")+" %" if k.get("share") is not None else None),align=CENTER)
        r+=1
    r+=1
    cell(ws,r,1,"Source : Search Console, dimension langue (prefixe d'URL). Les trois versions additionnent le trafic du site.",align=LEFT,border=False)
    ws.cell(row=r,column=1).font=SUBT


def sheet_historique(wb,R):
    h=(R["meta"].get("historique") or {})
    months=h.get("months") or []
    daily=h.get("daily") or []
    if not months: return
    ws=wb.create_sheet("Historique")
    ws["A1"]="Historique long, 16 mois"; ws["A1"].font=TITLE
    ws["A2"]="Source : Search Console, dimension date. Le dernier mois peut etre incomplet."; ws["A2"].font=SUBT
    hrow(ws,4,["Mois","Clics","Impressions","CTR","Jours couverts"],[14,12,14,10,16])
    r=4
    for mth in months:
        r+=1
        cell(ws,r,1,mth["month"]+(" (incomplet)" if mth.get("partial") else ""),align=CENTER)
        cell(ws,r,2,mth["clicks"],align=CENTER); cell(ws,r,3,mth["impressions"],align=CENTER)
        cell(ws,r,4,str(mth["ctr"]).replace(".",",")+" %",align=CENTER); cell(ws,r,5,mth["days"],align=CENTER)
    ch=LineChart(); ch.title="Clics par mois"; ch.height=7; ch.width=18; ch.style=2
    data=Reference(ws,min_col=2,min_row=4,max_row=4+len(months))
    cats=Reference(ws,min_col=1,min_row=5,max_row=4+len(months))
    ch.add_data(data,titles_from_data=True); ch.set_categories(cats)
    ws.add_chart(ch,"G4")
    r+=3
    cell(ws,r,1,"Donnees quotidiennes",bold=True,align=LEFT,border=False)
    r+=1
    hrow(ws,r,["Date","Clics","Impressions","Position"],[14,12,14,12])
    for d in daily:
        r+=1
        cell(ws,r,1,d["key"],align=CENTER); cell(ws,r,2,d["clicks"],align=CENTER)
        cell(ws,r,3,d["impressions"],align=CENTER); cell(ws,r,4,d.get("position"),align=CENTER)


def sheet_queries(wb,R):
    if not R.get("queries"): return
    ws=wb.create_sheet("Requêtes"); hrow(ws,1,["Requête","Marque","Clics","Impressions","CTR","Position","Statut"],[46,10,10,13,8,10,12])
    for i,q in enumerate(R["queries"],2):
        cell(ws,i,1,q["key"],align=LEFT); cell(ws,i,2,"oui" if q["brand"] else "non",align=CENTER)
        cell(ws,i,3,q["clicks"],align=CENTER); cell(ws,i,4,q["impressions"],align=CENTER)
        cell(ws,i,5,f'{q["ctr"]}%',align=CENTER); cell(ws,i,6,q["position"],align=CENTER)
        c=cell(ws,i,7,q.get("status") or "-",align=CENTER)
        if q.get("status")=="up" or q.get("status")=="new": c.fill=GAIN
        if q.get("status")=="down" or q.get("status")=="dormant": c.fill=LOSS
    ws.freeze_panes="A2"; ws.auto_filter.ref=f"A1:G{len(R['queries'])+1}"

def sheet_pages(wb,R):
    if not R.get("pages"): return
    ws=wb.create_sheet("Par page"); hrow(ws,1,["Page","Clics","Impressions","Position"],[70,10,13,10])
    for i,p in enumerate(R["pages"],2):
        cell(ws,i,1,p["url"],align=LEFT); cell(ws,i,2,p["clicks"],align=CENTER)
        cell(ws,i,3,p["impressions"],align=CENTER); cell(ws,i,4,p["position"],align=CENTER)
    ws.freeze_panes="A2"

ISO3={"che":"Suisse","fra":"France","deu":"Allemagne","aut":"Autriche","ita":"Italie","ukr":"Ukraine",
 "usa":"Etats-Unis","gbr":"Royaume-Uni","phl":"Philippines","bel":"Belgique","can":"Canada","esp":"Espagne",
 "nld":"Pays-Bas","irq":"Irak","afg":"Afghanistan","tjk":"Tadjikistan","kos":"Kosovo","srb":"Serbie",
 "hrv":"Croatie","bih":"Bosnie-Herzegovine","alb":"Albanie","lby":"Libye","col":"Colombie","zwe":"Zimbabwe",
 "ind":"Inde","pak":"Pakistan","lao":"Laos","arm":"Armenie","caf":"Republique centrafricaine","civ":"Cote d'Ivoire",
 "cod":"Republique democratique du Congo","mar":"Maroc","tun":"Tunisie","dza":"Algerie","sen":"Senegal",
 "lux":"Luxembourg","swe":"Suede","nor":"Norvege","dnk":"Danemark","pol":"Pologne","prt":"Portugal",
 "aus":"Australie","jpn":"Japon","chn":"Chine","rus":"Russie","tur":"Turquie","bra":"Bresil","mex":"Mexique"}

def country_label(code):
    c=(code or "").lower()
    n=ISO3.get(c)
    return f"{n} ({c.upper()})" if n else (code or "-")

def sheet_countries(wb,R):
    if not R.get("countries"): return
    ws=wb.create_sheet("Pays"); hrow(ws,1,["Pays","Clics","Impressions","CTR","Position"],[16,10,13,8,10])
    focus=set((R["meta"].get("countries_focus") or []))
    for i,c in enumerate(R["countries"],2):
        cc=cell(ws,i,1,country_label(c["country"]),align=LEFT,bold=(c["country"] in focus))
        if c["country"] in focus: cc.fill=GAIN
        cell(ws,i,2,c["clicks"],align=CENTER); cell(ws,i,3,c["impressions"],align=CENTER)
        cell(ws,i,4,f'{c["ctr"]}%',align=CENTER); cell(ws,i,5,c["position"],align=CENTER)

def sheet_trend(wb,R):
    t=R.get("trend")
    if not t: return
    ws=wb.create_sheet("Tendance")
    ws["A1"]="Par mois"; ws["A1"].font=TITLE
    hrow(ws,2,["Mois","Clics","Impressions","Position"],[14,12,14,10])
    r=2
    for mo in t.get("months",[]):
        r+=1; cell(ws,r,1,mo["key"],align=CENTER); cell(ws,r,2,mo["clicks"],align=CENTER)
        cell(ws,r,3,mo["impressions"],align=CENTER); cell(ws,r,4,mo["position"],align=CENTER)
    wr=r+3; ws.cell(row=wr-1,column=1,value="Par semaine ISO").font=TITLE
    hrow(ws,wr,["Semaine","Clics","Impressions","Position"],[14,12,14,10])
    start=wr
    for wk in t.get("weeks",[]):
        wr+=1; cell(ws,wr,1,wk["key"]+("" if wk.get("days",7)>=7 else " (semaine incomplète)"),align=CENTER); cell(ws,wr,2,wk["clicks"],align=CENTER)
        cell(ws,wr,3,wk["impressions"],align=CENTER); cell(ws,wr,4,wk["position"],align=CENTER)
    nwk=wr-start
    if nwk>=2:
        ch=LineChart(); ch.title="Clics par semaine"; ch.height=6; ch.width=14
        data=Reference(ws,min_col=2,min_row=start,max_row=wr); cats=Reference(ws,min_col=1,min_row=start+1,max_row=wr)
        ch.add_data(data,titles_from_data=False); ch.set_categories(cats); ws.add_chart(ch,"F"+str(start))
        ch2=LineChart(); ch2.title="Position moyenne par semaine"; ch2.height=6; ch2.width=14
        d2=Reference(ws,min_col=4,min_row=start,max_row=wr); ch2.add_data(d2,titles_from_data=False); ch2.set_categories(cats)
        ws.add_chart(ch2,"F"+str(start+13))

def sheet_opps(wb,R):
    o=R.get("opportunities")
    if not o or not o.get("items"): return
    ws=wb.create_sheet("Opportunités")
    src={"enrichi":"Source : opportunités scorées (mots-clés enrichis)","fallback_gsc":"Source : repli Search Console (aucun mot-clé enrichi)","aucune":"Aucune opportunité"}
    ws["A1"]="Opportunités à capter"; ws["A1"].font=TITLE; ws["A2"]=src.get(o.get("source"),""); ws["A2"].font=SUBT
    if o.get("source")=="enrichi":
        hrow(ws,4,["Requête","Volume","Clics potentiels","Valeur/mois","Effort","Page cible","Action"],[36,10,14,12,10,44,26])
        for i,it in enumerate(o["items"],5):
            cell(ws,i,1,it.get("keyword") or it.get("query") or it.get("key"),align=LEFT)
            cell(ws,i,2,it.get("volume"),align=CENTER); cell(ws,i,3,it.get("potential_clicks") or it.get("clicks_potential"),align=CENTER)
            cell(ws,i,4,it.get("value") or it.get("monthly_value"),align=CENTER); cell(ws,i,5,it.get("effort"),align=CENTER)
            cell(ws,i,6,it.get("target_page") or it.get("page"),align=LEFT); cell(ws,i,7,it.get("action"),align=LEFT)
    else:
        hrow(ws,4,["Requête non-marque","Impressions","Clics","Position","Type"],[46,13,10,10,26])
        for i,it in enumerate(o["items"],5):
            cell(ws,i,1,it["key"],align=LEFT); cell(ws,i,2,it["impressions"],align=CENTER)
            cell(ws,i,3,it["clicks"],align=CENTER); cell(ws,i,4,it["position"],align=CENTER); cell(ws,i,5,it["type"],align=LEFT)

def sheet_serp(wb,R):
    s=R.get("serp")
    if not s: return
    ws=wb.create_sheet("Concurrence")
    ws["A1"]="Partage de SERP observe (photo a l'instant T)"; ws["A1"].font=TITLE
    cols=["Requête","Client"]+s["competitors"]
    hrow(ws,3,cols,[40,10]+[22]*len(s["competitors"]))
    for i,q in enumerate(s["per_query"],4):
        cell(ws,i,1,q["query"],align=LEFT); cell(ws,i,2,"oui" if q["client"] else "-",align=CENTER,fill=GAIN if q["client"] else None)
        for j,c in enumerate(s["competitors"],3):
            cell(ws,i,j,"oui" if q.get(c) else "-",align=CENTER)
    r=4+len(s["per_query"])+1
    ws.cell(row=r,column=1,value="Presence top 10 (nb de requetes)").font=TITLE
    hrow(ws,r+1,["Domaine","Presences","/"+str(s["n_queries"])],[30,12,10])
    rr=r+1
    for dmn,cnt in sorted(s["tally"].items(),key=lambda x:-x[1]):
        rr+=1; cell(ws,rr,1,dmn,align=LEFT,bold=(dmn==s["client_domain"])); cell(ws,rr,2,cnt,align=CENTER); cell(ws,rr,3,s["n_queries"],align=CENTER)

def sheet_ga4(wb,R):
    g=R.get("ga4")
    if not g: return
    ws=wb.create_sheet("GA4")
    ws["A1"]="Comportement (GA4)"; ws["A1"].font=TITLE
    sub=f"Part organique : {g.get('organic_share')}% des sessions" + (f" | AI Assistant : {g.get('ai_sessions')} sessions" if g.get('ai_sessions') else "")
    ws["A2"]=sub; ws["A2"].font=SUBT
    hrow(ws,4,["Canal","Sessions","Users","Conversions","Engagement","Rebond","Durée (s)"],[22,12,10,12,12,10,10])
    r=4
    for c in g["channels"]:
        r+=1; b=norm=c["channel"]; isorg=str(c["channel"]).lower()=="organic search"
        cell(ws,r,1,c["channel"],align=LEFT,bold=isorg,fill=GAIN if isorg else None)
        cell(ws,r,2,c["sessions"],align=CENTER); cell(ws,r,3,c["users"],align=CENTER); cell(ws,r,4,c["conversions"],align=CENTER)
        cell(ws,r,5,f'{c["engagement_rate"]}%',align=CENTER); cell(ws,r,6,f'{c["bounce_rate"]}%',align=CENTER); cell(ws,r,7,c["avg_engagement_s"],align=CENTER)
    if g.get("landing"):
        r+=3; ws.cell(row=r-1,column=1,value="Landing pages organiques").font=TITLE
        hrow(ws,r,["Page","Sessions","Conversions","Engagement"],[60,12,12,12])
        for lp in g["landing"]:
            r+=1; cell(ws,r,1,lp["page"],align=LEFT); cell(ws,r,2,lp["sessions"],align=CENTER)
            cell(ws,r,3,lp["conversions"],align=CENTER); cell(ws,r,4,f'{lp["engagement_rate"]}%',align=CENTER)

def sheet_hygiene(wb,R):
    c=R.get("crawl")
    if not c: return
    ws=wb.create_sheet("Hygiène")
    ws["A1"]="Hygiène technique (dernier crawl)"; ws["A1"].font=TITLE
    ws["A2"]=f"Score : {c.get('score')} | Pages : {c.get('pages')}"; ws["A2"].font=SUBT
    hrow(ws,4,["Type de probleme","Nombre","Gravité"],[50,12,14])
    for i,it in enumerate(c.get("issues",[]),5):
        cell(ws,i,1,it.get("type"),align=LEFT); cell(ws,i,2,it.get("count"),align=CENTER); cell(ws,i,3,it.get("severity") or "-",align=CENTER)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--data",required=True); ap.add_argument("--out",required=True)
    a=ap.parse_args(); R=json.load(open(a.data,encoding="utf-8"))
    wb=Workbook()
    sheet_synthese(wb,R); sheet_langues(wb,R); sheet_historique(wb,R); sheet_queries(wb,R); sheet_pages(wb,R); sheet_countries(wb,R)
    sheet_trend(wb,R); sheet_opps(wb,R); sheet_serp(wb,R); sheet_ga4(wb,R); sheet_hygiene(wb,R)
    wb.save(a.out); print("xlsx:",a.out,"| onglets:",", ".join(wb.sheetnames))

if __name__=="__main__": main()
