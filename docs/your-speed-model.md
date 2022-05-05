## generateTerafic
1. Instead of multiple vehicles running (this is what generate traffic does right now), change it so it creates a single pedestrian which then walks/acts for 10 seconds or so. Might be easier to write from scratch than to modify the existing script.

2. Change camera so it has a top-down view, instead of the default perspective (oblique) view. Or, change camera so it is above and behind the shoulder of the pedestrian.


## speedModel
1. Define and use your speed model. For example, you can return the desired speed from a uniform distribution of [1,2. instead of a constant value. You might also consider using one of the speed models from this week’s readings and invent a new one. 
* The speed model is difined as radom from ...

2. How is your speed model different from the StaticSpeedModel? Could you detect any changes visually? If not, why? 
* The static speedmodel is .....

3. Submit answers to the questions (both carla questions) in "docs/your-speed-model.md" file in the same repository.

* Referense
- https://www.sciencedirect.com/science/article/pii/S000145752100021X
- https://www.sciencedirect.com/science/article/pii/S0968090X14000114
