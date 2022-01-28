In deze file staat wat uitleg over wat de verschillende files in de repo doen.


- .gitignore: gitignore
- batch_run.py: de code om batch runs van de simulatie uit te voeren
- requirements.txt: required imports
- run.py: run this file to start the mesa simulation environment
- DenBoschBusRoute: map met alle simulatie code
    - resources: data files en images
    - agent.py: classes voor alle agents (de hele connected intersection structuur)
    - model.py: de code om agents te plaatsen en de simulatie uit te voeren
    - server.py: hier wordt het model aangeroepen, we geven hier parameters mee aand het model zoals een functie die de busroute maakt
    - utils.py: willekeurige functies zoals het omzetten van de xml files naar python dicts
