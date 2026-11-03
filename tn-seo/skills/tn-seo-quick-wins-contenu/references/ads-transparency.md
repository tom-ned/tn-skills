# Collecte des annonces Google Ads via l'Ads Transparency Center

Procédure testée le 24.09.2026 sur un site client.
L'API est interne à Google, non documentée : si un appel échoue, refaire l'étape 2
(capture) avant de conclure à une absence de données.

## Outils

Claude in Chrome : `navigate`, `computer` (clic, scroll, capture), `javascript_tool`.
web_fetch ne fonctionne pas (page rendue en JavaScript, jeton XSRF obligatoire).

Code région Suisse : `2756` (autres pays : identifiants Google Ads geo target, ex. France 2250).

## Étape 1 : ouvrir la page du domaine

```
https://adstransparency.google.com/?region=CH&domain=<domaine>
```

Capture d'écran : le nombre d'annonces et le ou les annonceurs s'affichent sous le cartouche
du domaine. Zéro annonce : arrêter ici, le skill suit le workflow de base.

## Étape 2 : capturer le jeton XSRF

Les appels RPC exigent les en-têtes `X-Framework-Xsrf-Token` et `X-Same-Domain: 1`.
Le jeton se récupère en interceptant un appel émis par la page elle-même.

1. Installer l'intercepteur (javascript_tool). Ne rien renvoyer qui contienne une URL avec
   paramètres : l'outil bloque la sortie (« Cookie/query string data »).

```js
window.__cap = [];
const oOpen = XMLHttpRequest.prototype.open, oSet = XMLHttpRequest.prototype.setRequestHeader, oSend = XMLHttpRequest.prototype.send;
XMLHttpRequest.prototype.open = function(m,u){ this.__u=u; this.__h={}; return oOpen.apply(this, arguments); };
XMLHttpRequest.prototype.setRequestHeader = function(k,v){ this.__h[k]=v; return oSet.apply(this, arguments); };
XMLHttpRequest.prototype.send = function(b){ const x=this; this.addEventListener('load',()=>{ window.__cap.push({u:x.__u,h:x.__h,b:String(b||'')}); }); return oSend.apply(this, arguments); };
'ok'
```

2. Déclencher une recherche depuis l'interface : fermer l'éventuel sondage, ouvrir le filtre
   « Tous les formats » et choisir « Texte ». Le simple rechargement ne suffit pas (le
   rechargement efface l'intercepteur).

3. Stocker le jeton sans l'afficher :

```js
window.__tok = window.__cap.find(x=>x.h && x.h['X-Framework-Xsrf-Token']).h['X-Framework-Xsrf-Token'];
!!window.__tok
```

## Étape 3 : lister les annonces (SearchCreatives)

```js
const H = {'Content-Type':'application/x-www-form-urlencoded','X-Same-Domain':'1','X-Framework-Xsrf-Token':window.__tok};
const DOMAIN = 'exemple.ch', REGION = 2756;
let all=[], t=null, guard=0;
do {
  const req = {"2":100,"3":{"8":[REGION],"12":{"1":DOMAIN,"2":true}},"7":{"1":1,"2":38,"3":REGION}};
  if (t) req["4"] = t;
  const j = await (await fetch('/anji/_/rpc/SearchService/SearchCreatives?authuser=0',{method:'POST',headers:H,body:'f.req='+encodeURIComponent(JSON.stringify(req))})).json();
  all = all.concat(j["1"]||[]); t = j["2"]; guard++;
} while (t && guard < 10);
window.__ads = all;
const now = Date.now()/1000;
({total: all.length, actives30j: all.filter(a=>now-Number(a["7"]["1"])<30*86400).length,
  annonceurs: [...new Set(all.map(a=>a["12"]))]})
```

Champs utiles d'une annonce : `1` identifiant annonceur, `2` identifiant créa, `4` format
(1 texte, 2 image, 3 vidéo), `6.1` première diffusion (epoch s), `7.1` dernière diffusion,
`12` nom de l'annonceur, `14` domaine. Filtre format optionnel : `"3":{"4":1,...}`.

## Étape 4 : texte des annonces (GetCreativeById puis content.js)

La liste ne contient qu'un aperçu image. Le texte est servi par un script `content.js`
référencé dans le détail de chaque annonce ; il est lisible en fetch depuis la page.

```js
const decode = s => s.replace(/\\x([0-9a-fA-F]{2})/g,(m,h)=>String.fromCharCode(parseInt(h,16))).replace(/\\u([0-9a-fA-F]{4})/g,(m,h)=>String.fromCharCode(parseInt(h,16)));
function extract(dec){ const a=dec.indexOf('<div'), b=dec.lastIndexOf('</div>'); if(a<0) return [];
  const doc=new DOMParser().parseFromString(dec.slice(a,b+6),'text/html'); doc.querySelectorAll('style,script,svg').forEach(n=>n.remove());
  return [...new Set([...doc.body.querySelectorAll('*')].filter(n=>n.children.length===0).map(n=>n.textContent.trim()).filter(s=>s.length>2))]; }
async function one(ad){
  const j = await (await fetch('/anji/_/rpc/LookupService/GetCreativeById?authuser=0',{method:'POST',headers:H,
    body:'f.req='+encodeURIComponent(JSON.stringify({"1":ad["1"],"2":ad["2"],"5":{"1":1,"2":38,"3":REGION}}))})).json();
  let texts=[]; for (const v of ((j["1"]&&j["1"]["5"])||[])) { const u=v["1"]&&v["1"]["4"]; if(u) texts=texts.concat(extract(decode(await (await fetch(u)).text()))); }
  return {first:new Date(ad["6"]["1"]*1000).toISOString().slice(0,10), last:new Date(ad["7"]["1"]*1000).toISOString().slice(0,10), texts:[...new Set(texts)]};
}
const res=[]; for (let i=0;i<window.__ads.length;i+=5) res.push(...await Promise.all(window.__ads.slice(i,i+5).map(one)));
window.__res = res;
const noise = /^(Sponsorisé|website|call|directions|Appeler|Site Web|Itinéraire)$|^</;
res.filter(r=>r.texts.length).map(r=>[r.last, r.first, r.texts.filter(x=>!noise.test(x)&&!/^https?:/.test(x)).slice(0,5).join(' | ')].join(' ; '))
```

Renvoyer uniquement ce tableau texte : il ne contient pas d'URL à paramètres, donc il passe
le filtre de l'outil.

## Lecture des résultats

- `{KeyWord:Formation en ligne}` : insertion dynamique de mot-clé. Le texte entre
  accolades est le libellé par défaut, donc une requête que l'annonceur cible
  explicitement. C'est le signal le plus fiable de mot-clé acheté.
- Chemin d'affichage (`www.domaine.ch/formations/autodesk`) : indication de la page de
  destination, pas l'URL finale. À rapprocher des pages réelles du site.
- `<Rating (Reviews)>`, `<Open Hours>`, adresse : extensions de lieu, annonces liées à la
  fiche Google Business Profile. Utile pour savoir quelles villes sont ciblées.
- Dates : dernière diffusion à moins de 30 jours = annonce active. Première diffusion
  ancienne + toujours active = thème que l'annonceur paie de façon durable.

Ce que l'outil ne donne pas : budget, CPC payé, liste complète des mots-clés, URL finale.
Ne jamais présenter de chiffre de dépense.

## Pannes connues

- `XSRF token is MISSING` (400) : jeton absent ou expiré, refaire l'étape 2.
- `read_network_requests` ne capte pas les appels RPC de chargement initial : ne pas
  compter dessus, utiliser l'intercepteur.
- Sortie bloquée par l'outil : la valeur renvoyée contient une URL avec paramètres ou un
  jeton. Réduire la sortie aux champs textuels.
- Fermer l'onglet (`tabs_close_mcp`) en fin de collecte.
