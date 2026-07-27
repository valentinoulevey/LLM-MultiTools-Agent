# 🎬 Démo — scénarios d'utilisation

Ces scénarios illustrent le raisonnement ReAct de l'agent : quelle demande
déclenche quel(s) outil(s).

---

## 1. Question météo simple

**Requête :** « Quel temps fera-t-il demain à Paris ? »

**Raisonnement :** un seul outil suffit.

| Étape | Action |
|-------|--------|
| reasoning | décide d'appeler `get_weather` |
| tools | `get_weather(city="Paris")` → Open-Meteo |
| respond | « Météo à Paris (demain) : … » |

🛠️ Outils utilisés : `get_weather`

---

## 2. Comparaison de villes

**Requête :** « Compare Paris et Lyon pour ce week-end »

🛠️ Outils utilisés : `compare_weather`

L'agent renvoie température, pluie et conditions pour les deux villes, puis
conclut sur la plus chaude / la plus sèche.

---

## 3. Recherche d'activités

**Requête :** « Trouve-moi une activité culturelle dans le Marais »

🛠️ Outils utilisés : `search_activity`

L'agent géocode « le Marais », interroge Overpass et liste des musées / lieux
culturels à proximité.

---

## 4. Organisation complète (multi-outils)

**Requête :** « Organise-moi une sortie à Montmartre pour 4 personnes avec 40 €
par personne »

🛠️ Outils utilisés : `build_simple_itinerary`
(qui orchestre en interne météo + activités + budget)

L'agent produit un programme complet : météo du jour, activités suggérées et
répartition du budget.

---

## 5. Trajet entre deux lieux

**Requête :** « Combien de temps pour aller du Louvre à Montmartre ? »

🛠️ Outils utilisés : `get_transport_route`

L'agent renvoie distance, durée en voiture (OSRM) et estimation métro.

---

## Astuce

La sidebar Streamlit affiche le **modèle** utilisé et les **APIs actives**.
Chaque réponse indique les **outils réellement appelés** — pratique pour
observer le comportement de l'agent en direct.
