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
