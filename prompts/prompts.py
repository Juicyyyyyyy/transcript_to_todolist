from DTO.Requests.todo_list_request import TodoListRequest

class Prompt:
	@staticmethod
	def transcript_to_todo_prompt(transcript):
		return f"""
		Tu es un assistant spécialisé dans la synthèse de réunions. À partir du transcript fourni, identifie toutes les 
		actions concrètes mentionnées et transforme-les en une to-do list claire, concise et actionable. Reformule les 
		actions en phrases impératives ("Faire X", "Préparer Y", "Envoyer Z"). Inclue une deadline si elle est explicitement 
		mentionnée. Si des tâches sont floues, propose une clarification entre parenthèses. Structure la sortie sous forme 
		de liste à puces. Output attendu : une to-do list synthétique et hiérarchisée, facile à lire.
		
		TRANSCRIPT = <{transcript}>
		"""

	@staticmethod
	def transcript_to_technical_todo_prompt(Request: TodoListRequest):
		ast_text = Request.get_parsed_project()
		MAX_LEN = 120_000
		if len(ast_text) > MAX_LEN:
			ast_text = ast_text[:MAX_LEN] + "\n...\n[AST TRONQUÉ POUR LA BRIÈVETÉ]"

		return f"""
Tu es un **lead dev full-stack** chargé de dériver une **to-do technique détaillée** à partir d'un transcript de réunion **en respectant la structure réelle du projet** et **le stack détecté dans l'AST** (ex. Laravel/PHP, React/Vite, etc.).

# Objectif
Produire une to-do **technique et exécutable** qui indique précisément *où* intervenir (chemins de fichiers réels), *quoi* modifier/créer (classes, fonctions, composants, routes, migrations, tests), et *comment* le faire au niveau signature / squelette de code lorsque pertinent.

# Contexte — Structure & AST du projet
<{ast_text}>

# Contexte — Transcript de réunion
<{Request.get_transcript()}>

# Ce que tu dois déduire automatiquement
- Déterminer le **stack** et l’architecture (ex. Laravel: contrôleurs, FormRequest, Eloquent models, migrations, routes/web.php ou routes/api.php; React: composants dans resources/js, router, hooks, Vite).
- Identifier les **points d’extension** existants (contrôleurs, services, repositories, DTO, vues Blade/React, tests) à partir des fichiers listés/AST.

# Règles de sortie (FORMAT EXIGÉ)
- Réponds en **Markdown** avec les sections suivantes (seulement si applicable) :
  - **Backend (Laravel/PHP)**  
  - **Frontend (React/JS/TS)**  
  - **Base de données / Migrations**  
  - **Tests (PHPUnit / Frontend)**  
  - **Infra / DevOps**  
  - **Clarifications requises**
- Dans chaque section, liste des tâches sous forme de cases à cocher :
  - `- [ ] <PRIORITÉ: P0/P1/P2> <TAILLE: S/M/L> <ACTION IMPÉRATIVE>`
  - Indique **chemin(s) de fichier** exact(s) à modifier/créer (ex: `app/Http/Controllers/UserController.php`, `routes/api.php`, `resources/js/components/...`).
  - Quand utile, donne **signatures/squelettes** minimalistes (ex: méthode, FormRequest, Rule, composant React, hook, slice store).
  - Pour Laravel : précise **route** (verbe + path), **validation** (FormRequest), **Eloquent model/relations**, **Policy/Gate** si sécurité, **Job/Event/Listener** si asynchrone.
  - Pour DB : fournis **migrations** (up/down) et **rollback** envisagé.
  - Pour Frontend : précise **point d’intégration** (composant/page), **état** (Context/Redux/Zustand), **appel API** (endpoint, méthode, payload, traitement des erreurs), **types** s’il y a TypeScript.
  - Pour Tests : **Feature** + **Unit** côté PHP, et tests frontend (Vitest/Jest/RTL). Donne **cas de test** clés.
  - Ajoute pour chaque tâche : **dépendances** (bloqueurs/pré-requis) & **critères d’acceptation** mesurables (Given/When/Then bref).

# Contraintes
- **Respecte l’architecture existante** déduite de l’AST (namespaces, conventions, répertoires).
- **Ne propose pas** de créer des dossiers ou patterns absents si une alternative cohérente existe déjà dans le projet.
- **Ignore** explicitement les dossiers exclus usuels (vendor, node_modules, storage, bootstrap/cache, public/build, dist, etc.) pour les chemins proposés.
- Si le transcript est **ambigu** ou **incomplet**, ajoute une section **Clarifications requises** avec les questions bloquantes.

# Exemple de tâche (gabarit)
- [ ] **P0 · M** Créer `app/Http/Requests/StoreProjectRequest.php` (FormRequest) — *dépend de la route POST `/api/projects`*
  - Signatures: `rules(): array`, `authorize(): bool`
  - Critères: 422 si validation échoue; 201 avec JSON `id, name, ...` si succès.
  - Tests: Feature test `tests/Feature/ProjectStoreTest.php` couvrant 200/422/auth.

# Sortie attendue
Une **liste actionnable** et **priorisée** de tâches techniques, groupées par domaine (Backend/Frontend/DB/Tests/Infra), s’appuyant sur la **structure réelle** du projet ci-dessus.
"""

