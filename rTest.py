from rote import Rote

raw = "Alice knows Bob. Tom lives in Paris. Alice knows Tom Bob works at OpenAI. Alice lives in Paris. Alice lives in Paris Bob lives in New York..."

rote = Rote()

rote.build_triples(raw)

#rote.print_triples()

rote.build_nx_graph()

facts = rote.recall("Paris")
facts = facts + "\n\n" + rote.recall("Alice")

print(facts)